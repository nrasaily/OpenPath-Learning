from django.contrib import admin

from .models import (
    AnswerOption,
    Assessment,
    AssessmentAttempt,
    AttemptAnswer,
    Question,
)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "assessment_type", "language_tag", "is_published")
    list_filter = ("assessment_type", "language_tag", "is_published")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "position", "question_type", "points")
    list_filter = ("question_type",)
    search_fields = ("assessment__title", "prompt")


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("question", "position", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("question__prompt", "text")


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "assessment", "status", "score", "started_at")
    list_filter = ("status", "assessment")
    search_fields = ("student__email", "assessment__title")


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct", "points_awarded")
    list_filter = ("is_correct",)
    search_fields = ("attempt__student__email", "question__prompt")
