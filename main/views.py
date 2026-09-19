from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
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


# ---------- Експорт (заглушки — реалізуємо окремим кроком) ----------

class ResumeExportPDFView(OwnerResumeQuerysetMixin, View):
    def get(self, request, pk):
        get_object_or_404(self.get_queryset(), pk=pk)
        return HttpResponse('Експорт у PDF ще не реалізовано.', status=501)


class ResumeExportDOCXView(OwnerResumeQuerysetMixin, View):
    def get(self, request, pk):
        get_object_or_404(self.get_queryset(), pk=pk)
        return HttpResponse('Експорт у DOCX ще не реалізовано.', status=501)


# ---------- Секції резюме (досвід/освіта/навички) ----------

class ResumeSectionMixin(LoginRequiredMixin):
    """Спільна логіка для секцій, прив'язаних до конкретного резюме."""

    resume_url_kwarg = 'resume_pk'

    def get_resume(self):
        return get_object_or_404(
            Resume, pk=self.kwargs[self.resume_url_kwarg], owner=self.request.user,
        )

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