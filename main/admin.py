from django.contrib import admin

from .models import (
    Announcement,
    Education,
    Resume,
    ResumeTemplate,
    Skill,
    WorkExperience,
)


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "template", "status", "updated_at")
    list_filter = ("status", "template")
    search_fields = ("title", "owner__username", "full_name", "email")
    date_hierarchy = "updated_at"
    inlines = [WorkExperienceInline, EducationInline, SkillInline]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "content")
    readonly_fields = ("author",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)
