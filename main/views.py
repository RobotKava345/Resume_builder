from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import EducationForm, ResumeForm, SkillForm, WorkExperienceForm
from .models import (
    Announcement, Education, Resume, ResumeTemplate, Skill, WorkExperience,
)


# ---------- Каталог шаблонів ----------

class ResumeTemplateListView(ListView):
    model = ResumeTemplate
    template_name = 'main/template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return ResumeTemplate.objects.filter(is_active=True)


class ResumeTemplateDetailView(DetailView):
    model = ResumeTemplate
    template_name = 'main/template_detail.html'
    context_object_name = 'template_obj'

    def get_queryset(self):
        return ResumeTemplate.objects.filter(is_active=True)


class _PreviewCollection:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


@method_decorator(xframe_options_sameorigin, name='dispatch')
class ResumeTemplateMiniPreviewView(ResumeTemplateDetailView):
    """Показує шаблон із безпечними демонстраційними даними для каталогу."""

    def get_template_names(self):
        return [f'resume_render/{self.object.slug}.html', 'resume_render/classic-serif.html']

    def get_context_data(self, **kwargs):
        from datetime import date
        from types import SimpleNamespace

        context = super().get_context_data(**kwargs)
        skill_levels = ('Початковий', 'Базовий', 'Впевнений', 'Просунутий', 'Експерт')
        skills = [
            SimpleNamespace(
                name=name,
                level=level,
                lvl=level,
                get_level_display=lambda level=level: skill_levels[level - 1],
            )
            for name, level in [('Стратегія', 5), ('Аналітика', 4), ('Комунікація', 4)]
        ]
        experiences = [
            SimpleNamespace(
                company='Northstar Studio',
                position='Менеджерка проєктів',
                start_date=date(2022, 3, 1),
                end_date=None,
                is_current=True,
                description='Координація команди та запуск цифрових продуктів.',
            ),
        ]
        educations = [
            SimpleNamespace(
                institution='Київський національний університет',
                degree='Маркетинг',
                start_date=date(2017, 9, 1),
                end_date=date(2021, 6, 1),
                description='',
            ),
        ]
        context.update({
            'template_preview': True,
            'resume': SimpleNamespace(
                pk=0,
                title='Маркетологиня',
                full_name='Олена Коваль',
                email='olena.koval@example.com',
                phone='+380 67 123 45 67',
                address='Київ, Україна',
                summary='Маркетологиня з досвідом розвитку брендів і запуску цифрових продуктів.',
                photo=SimpleNamespace(url=static('img/template-preview-avatar.svg')),
                work_experiences=_PreviewCollection(experiences),
                educations=_PreviewCollection(educations),
                skills=_PreviewCollection(skills),
            ),
        })
        return context


# ---------- Оголошення ----------

class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'main/announcement_list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True)


# ---------- Резюме (CRUD) ----------

class OwnerResumeQuerysetMixin(LoginRequiredMixin):
    """Обмежує вибірку резюме лише тими, що належать поточному користувачу."""

    def get_queryset(self):
        return Resume.objects.filter(owner=self.request.user)


class ResumeListView(OwnerResumeQuerysetMixin, ListView):
    model = Resume
    template_name = 'main/resume_list.html'
    context_object_name = 'resumes'


class ResumeDetailView(OwnerResumeQuerysetMixin, DetailView):
    model = Resume
    template_name = 'main/resume_detail.html'
    context_object_name = 'resume'


class ResumeCreateView(LoginRequiredMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'main/resume_form.html'

    def get_initial(self):
        initial = super().get_initial()
        template_id = self.request.GET.get('template')
        if template_id:
            initial['template'] = template_id
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('main:resume_detail', kwargs={'pk': self.object.pk})


class ResumeUpdateView(OwnerResumeQuerysetMixin, UpdateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'main/resume_form.html'

    def get_success_url(self):
        return reverse('main:resume_detail', kwargs={'pk': self.object.pk})


class ResumeDeleteView(OwnerResumeQuerysetMixin, DeleteView):
    model = Resume
    template_name = 'main/resume_confirm_delete.html'
    success_url = reverse_lazy('main:resume_list')


class ResumeCloneView(OwnerResumeQuerysetMixin, View):
    """Клонування доступне лише через POST-запит."""

    def post(self, request, pk):
        resume = get_object_or_404(self.get_queryset(), pk=pk)
        clone = resume.clone()
        return redirect('main:resume_detail', pk=clone.pk)

    def get(self, request, pk):
        return HttpResponseForbidden('Клонування доступне лише через POST-запит.')


# ---------- Експорт ----------

class ResumeExportPDFView(OwnerResumeQuerysetMixin, View):
    def get(self, request, pk):
        from weasyprint import HTML

        resume = get_object_or_404(
            self.get_queryset().select_related('template').prefetch_related(
                'work_experiences', 'educations', 'skills',
            ),
            pk=pk,
        )
        template_slug = resume.template.slug if resume.template else 'classic-serif'
        html = render_to_string(
            [
                f'resume_render/{template_slug}.html',
                'resume_render/classic-serif.html',
            ],
            {'resume': resume},
            request=request,
        )
        pdf = HTML(
            string=html,
            base_url=request.build_absolute_uri('/'),
        ).write_pdf()

        filename = slugify(resume.full_name or resume.title) or f'resume-{resume.pk}'
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        return response


class ResumeExportDOCXView(OwnerResumeQuerysetMixin, View):
    def get(self, request, pk):
        from io import BytesIO

        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt, RGBColor

        resume = get_object_or_404(
            self.get_queryset().prefetch_related(
                'work_experiences', 'educations', 'skills',
            ),
            pk=pk,
        )
        document = Document()
        section = document.sections[0]
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        normal = document.styles['Normal']
        normal.font.name = 'Arial'
        normal.font.size = Pt(10)
        normal.font.color.rgb = RGBColor(42, 48, 56)
        for style_name in ('Heading 1', 'Heading 2'):
            style = document.styles[style_name]
            style.font.name = 'Arial'
            style.font.color.rgb = RGBColor(31, 58, 95)
            style.font.bold = True
        document.styles['Heading 1'].font.size = Pt(22)
        document.styles['Heading 2'].font.size = Pt(12)

        name = resume.full_name or resume.title
        title = document.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.style = document.styles['Title']
        title_run = title.add_run(name)
        title_run.font.name = 'Arial'
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(31, 58, 95)

        contacts = [value for value in (resume.email, resume.phone, resume.address) if value]
        if contacts:
            contact = document.add_paragraph('  ·  '.join(contacts))
            contact.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if resume.photo:
            try:
                with resume.photo.open('rb') as photo_file:
                    picture = document.add_paragraph().add_run().add_picture(
                        photo_file, width=Inches(1.25),
                    )
                picture._inline.docPr.set('descr', 'Фото у резюме')
            except (OSError, ValueError):
                # The document remains exportable if an optional photo is unavailable.
                pass

        def add_section_heading(text):
            document.add_heading(text, level=2)

        if resume.summary:
            add_section_heading('Про себе')
            document.add_paragraph(resume.summary)

        experiences = resume.work_experiences.all()
        if experiences:
            add_section_heading('Досвід роботи')
            for item in experiences:
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.space_after = Pt(1)
                run = paragraph.add_run(f'{item.position} — {item.company}')
                run.bold = True
                start = item.start_date.strftime('%m.%Y') if item.start_date else ''
                end = 'тепер' if item.is_current else (
                    item.end_date.strftime('%m.%Y') if item.end_date else ''
                )
                if start or end:
                    dates = document.add_paragraph(f'{start} — {end}')
                    dates.paragraph_format.space_after = Pt(2)
                if item.description:
                    document.add_paragraph(item.description)

        educations = resume.educations.all()
        if educations:
            add_section_heading('Освіта')
            for item in educations:
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.space_after = Pt(1)
                run = paragraph.add_run(item.institution)
                run.bold = True
                if item.degree:
                    paragraph.add_run(f' — {item.degree}')
                start = item.start_date.strftime('%m.%Y') if item.start_date else ''
                end = item.end_date.strftime('%m.%Y') if item.end_date else ''
                if start or end:
                    dates = document.add_paragraph(f'{start} — {end}')
                    dates.paragraph_format.space_after = Pt(2)
                if item.description:
                    document.add_paragraph(item.description)

        skills = resume.skills.all()
        if skills:
            add_section_heading('Навички')
            for skill in skills:
                document.add_paragraph(
                    f'{skill.name} — {skill.get_level_display()}',
                    style='List Bullet',
                )

        output = BytesIO()
        document.save(output)
        filename = slugify(resume.full_name or resume.title) or f'resume-{resume.pk}'
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.docx"'
        return response


# ---------- Секції резюме (досвід/освіта/навички) ----------

class ResumeSectionMixin(LoginRequiredMixin):
    """Спільна логіка для секцій, прив'язаних до конкретного резюме."""

    resume_url_kwarg = 'resume_pk'

    def get_resume(self):
        return get_object_or_404(
            Resume, pk=self.kwargs[self.resume_url_kwarg], owner=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = self.get_resume()
        return context

    def get_success_url(self):
        return reverse(
            'main:resume_detail', kwargs={'pk': self.kwargs[self.resume_url_kwarg]},
        )


class SectionCreateView(ResumeSectionMixin, CreateView):
    def form_valid(self, form):
        form.instance.resume = self.get_resume()
        return super().form_valid(form)


class SectionOwnedQuerysetMixin(ResumeSectionMixin):
    """Для Update/Delete: гарантує, що секція належить резюме поточного власника."""

    def get_queryset(self):
        return self.model.objects.filter(resume=self.get_resume())


class WorkExperienceCreateView(SectionCreateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'main/section_form.html'


class WorkExperienceUpdateView(SectionOwnedQuerysetMixin, UpdateView):
    model = WorkExperience
    form_class = WorkExperienceForm
    template_name = 'main/section_form.html'


class WorkExperienceDeleteView(SectionOwnedQuerysetMixin, DeleteView):
    model = WorkExperience
    template_name = 'main/section_confirm_delete.html'


class EducationCreateView(SectionCreateView):
    model = Education
    form_class = EducationForm
    template_name = 'main/section_form.html'


class EducationUpdateView(SectionOwnedQuerysetMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'main/section_form.html'


class EducationDeleteView(SectionOwnedQuerysetMixin, DeleteView):
    model = Education
    template_name = 'main/section_confirm_delete.html'


class SkillCreateView(SectionCreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'main/section_form.html'


class SkillUpdateView(SectionOwnedQuerysetMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'main/section_form.html'


class SkillDeleteView(SectionOwnedQuerysetMixin, DeleteView):
    model = Skill
    template_name = 'main/section_confirm_delete.html'

class ResumeRenderView(OwnerResumeQuerysetMixin, DetailView):
    model = Resume
    context_object_name = 'resume'

    def get_template_names(self):
        slug = self.object.template.slug if self.object.template else 'classic-serif'
        return [f'resume_render/{slug}.html', 'resume_render/classic-serif.html']
