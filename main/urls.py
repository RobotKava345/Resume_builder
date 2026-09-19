from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    # Каталог шаблонів
    path('templates/', views.ResumeTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.ResumeTemplateDetailView.as_view(), name='template_detail'),

    # Оголошення
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),

    # CRUD резюме
    path('resumes/', views.ResumeListView.as_view(), name='resume_list'),
    path('resumes/create/', views.ResumeCreateView.as_view(), name='resume_create'),
    path('resumes/<int:pk>/', views.ResumeDetailView.as_view(), name='resume_detail'),
    path('resumes/<int:pk>/edit/', views.ResumeUpdateView.as_view(), name='resume_update'),
    path('resumes/<int:pk>/delete/', views.ResumeDeleteView.as_view(), name='resume_delete'),
    path('resumes/<int:pk>/clone/', views.ResumeCloneView.as_view(), name='resume_clone'),

    # Експорт (заглушки)
    path('resumes/<int:pk>/export/pdf/', views.ResumeExportPDFView.as_view(), name='resume_export_pdf'),
    path('resumes/<int:pk>/export/docx/', views.ResumeExportDOCXView.as_view(), name='resume_export_docx'),

    # Досвід роботи
    path('resumes/<int:resume_pk>/experience/add/', views.WorkExperienceCreateView.as_view(), name='experience_add'),
    path('resumes/<int:resume_pk>/experience/<int:pk>/edit/', views.WorkExperienceUpdateView.as_view(), name='experience_edit'),
    path('resumes/<int:resume_pk>/experience/<int:pk>/delete/', views.WorkExperienceDeleteView.as_view(), name='experience_delete'),

    # Освіта
    path('resumes/<int:resume_pk>/education/add/', views.EducationCreateView.as_view(), name='education_add'),
    path('resumes/<int:resume_pk>/education/<int:pk>/edit/', views.EducationUpdateView.as_view(), name='education_edit'),
    path('resumes/<int:resume_pk>/education/<int:pk>/delete/', views.EducationDeleteView.as_view(), name='education_delete'),

    # Навички
    path('resumes/<int:resume_pk>/skills/add/', views.SkillCreateView.as_view(), name='skill_add'),
    path('resumes/<int:resume_pk>/skills/<int:pk>/edit/', views.SkillUpdateView.as_view(), name='skill_edit'),
    path('resumes/<int:resume_pk>/skills/<int:pk>/delete/', views.SkillDeleteView.as_view(), name='skill_delete'),
]