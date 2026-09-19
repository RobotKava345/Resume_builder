from django.conf import settings
from django.db import models
from django.urls import reverse


class ResumeTemplate(models.Model):
    """Шаблон оформлення резюме з каталогу."""

    name = models.CharField("Назва шаблону", max_length=100)
    description = models.TextField("Опис", blank=True)
    preview_image = models.ImageField(
        "Прев'ю", upload_to="template_previews/", blank=True, null=True
    )
    # Ключ, за яким у коді/шаблонізаторі буде обиратись html/css розмітка
    slug = models.SlugField("Ідентифікатор", unique=True)
    is_active = models.BooleanField("Активний", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Шаблон резюме"
        verbose_name_plural = "Шаблони резюме"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Resume(models.Model):
    """Резюме користувача."""

    STATUS_DRAFT = "draft"
    STATUS_READY = "ready"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Чернетка"),
        (STATUS_READY, "Готове"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
        verbose_name="Власник",
    )
    template = models.ForeignKey(
        ResumeTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resumes",
        verbose_name="Шаблон",
    )
    title = models.CharField("Назва резюме", max_length=150)
    status = models.CharField(
        "Статус", max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )

    # Особисті дані
    full_name = models.CharField("ПІБ", max_length=150, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    address = models.CharField("Адреса", max_length=255, blank=True)
    summary = models.TextField("Про себе", blank=True)
    photo = models.ImageField(
        "Фото", upload_to="resume_photos/", blank=True, null=True
    )

    created_at = models.DateTimeField("Створено", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Резюме"
        verbose_name_plural = "Резюме"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.owner})"

    def get_absolute_url(self):
        return reverse("resume_detail", kwargs={"pk": self.pk})

    def clone(self, new_title=None):
        """Створює копію резюме разом з усіма секціями."""
        related_sections = [
            self.work_experiences.all(),
            self.educations.all(),
            self.skills.all(),
        ]

        clone = Resume.objects.get(pk=self.pk)
        clone.pk = None
        clone.id = None
        clone.title = new_title or f"{self.title} (копія)"
        clone.status = self.STATUS_DRAFT
        clone.save()

        for qs in related_sections:
            for item in qs:
                item.pk = None
                item.id = None
                item.resume = clone
                item.save()

        return clone


class WorkExperience(models.Model):
    """Секція 'Досвід роботи'."""

    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="work_experiences"
    )
    company = models.CharField("Компанія", max_length=150)
    position = models.CharField("Посада", max_length=150)
    start_date = models.DateField("Дата початку")
    end_date = models.DateField("Дата закінчення", blank=True, null=True)
    is_current = models.BooleanField("Працюю зараз", default=False)
    description = models.TextField("Опис обов'язків", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Досвід роботи"
        verbose_name_plural = "Досвід роботи"
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.position} — {self.company}"


class Education(models.Model):
    """Секція 'Освіта'."""

    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="educations"
    )
    institution = models.CharField("Навчальний заклад", max_length=200)
    degree = models.CharField("Ступінь / спеціальність", max_length=150, blank=True)
    start_date = models.DateField("Дата початку")
    end_date = models.DateField("Дата закінчення", blank=True, null=True)
    description = models.TextField("Опис", blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Освіта"
        verbose_name_plural = "Освіта"
        ordering = ["order", "-start_date"]

    def __str__(self):
        return f"{self.institution} — {self.degree}"


class Skill(models.Model):
    """Секція 'Навички'."""

    LEVEL_CHOICES = [
        (1, "Початковий"),
        (2, "Базовий"),
        (3, "Впевнений"),
        (4, "Просунутий"),
        (5, "Експерт"),
    ]

    resume = models.ForeignKey(
        Resume, on_delete=models.CASCADE, related_name="skills"
    )
    name = models.CharField("Назва навички", max_length=100)
    level = models.PositiveSmallIntegerField(
        "Рівень", choices=LEVEL_CHOICES, default=3
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Навичка"
        verbose_name_plural = "Навички"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Announcement(models.Model):
    """Оголошення / новини від адміністратора."""

    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
        verbose_name="Автор",
    )
    is_published = models.BooleanField("Опубліковано", default=True)
    created_at = models.DateTimeField("Створено", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Оголошення"
        verbose_name_plural = "Оголошення та новини"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
