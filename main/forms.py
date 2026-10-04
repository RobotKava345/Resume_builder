from django import forms

from .models import Education, Resume, Skill, WorkExperience


class BootstrapFormMixin:
    """Додає Bootstrap-класи всім полям форми залежно від типу віджета."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault('class', 'form-control')
            else:
                widget.attrs.setdefault('class', 'form-control')


class ResumeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'title', 'template', 'full_name', 'email', 'phone',
            'address', 'summary', 'photo',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }


class WorkExperienceForm(BootstrapFormMixin, forms.ModelForm):
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


class EducationForm(BootstrapFormMixin, forms.ModelForm):
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


class SkillForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level', 'order']