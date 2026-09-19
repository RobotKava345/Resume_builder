from django import forms

from .models import Education, Resume, Skill, WorkExperience


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'title', 'template', 'full_name', 'email', 'phone',
            'address', 'summary', 'photo',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = [
            'company', 'position', 'start_date', 'end_date',
            'is_current', 'description', 'order',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'start_date', 'end_date',
            'description', 'order',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level', 'order']