from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import AcademicTerm, Course, CourseOffering, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "status")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "subject", "subject_catalog", "grade", "level", "language_tag", "is_published")
    list_filter = ("grade", "level", "language_tag", "is_published")
    search_fields = ("code", "title", "subject", "subject_catalog__name")


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("course", "term", "section_code", "instructor", "capacity", "is_open")
    list_filter = ("term", "is_open", "course__level")
    search_fields = ("course__code", "course__title", "section_code", "instructor__email")


from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "offering", "status", "enrolled_at")
    list_filter = ("status",)
    search_fields = ("student__email", "offering__course__title")


from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "language_tag",
        "position",
        "estimated_minutes",
        "is_published",
    )
    list_filter = ("language_tag", "is_published")
    search_fields = ("title", "course__title")


from .models import ClassGroup


class ClassGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields["class_teacher"].queryset = User.objects.filter(
            is_active=True,
            groups__name="teacher",
            teacher_application__status="approved",
        ).distinct().order_by("first_name", "last_name", "email")


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    form = ClassGroupAdminForm
    list_display = ("grade", "term", "section_code", "class_teacher")
    list_filter = ("grade", "term")
    search_fields = ("section_code", "class_teacher__email")
    filter_horizontal = ("course_offerings",)
