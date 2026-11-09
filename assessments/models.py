from django.db import models

# Create your models here.


from django.db import models


class Assessment(models.Model):
    class AssessmentType(models.TextChoices):
        PLACEMENT = "placement", "Placement"
        COURSE = "course", "Course"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        default=AssessmentType.COURSE,
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessments",
    )
    language_tag = models.CharField(max_length=10, default="en")
    time_limit_minutes = models.PositiveSmallIntegerField(default=60)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"
        SHORT_ANSWER = "short_answer", "Short answer"
        ESSAY = "essay", "Essay"

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    points = models.PositiveSmallIntegerField(default=1)
    position = models.PositiveSmallIntegerField()
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ("position",)
        constraints = [
            models.UniqueConstraint(
                fields=("assessment", "position"),
                name="unique_assessment_question_position",
            )
        ]

    def __str__(self):
        return f"{self.assessment.title} — Question {self.position}"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ("position",)
        constraints = [
            models.UniqueConstraint(
                fields=("question", "position"),
                name="unique_question_option_position",
            )
        ]

    def __str__(self):
        return f"Option {self.position} for Question {self.question.position}"


from django.conf import settings


class AssessmentAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        SUBMITTED = "submitted", "Submitted"
        GRADED = "graded", "Graded"

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        related_name="attempts",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assessment_attempts",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )
    feedback = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.email} — {self.assessment.title}"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="submitted_answers",
    )
    selected_option = models.ForeignKey(
        AnswerOption,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="selected_by",
    )
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points_awarded = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("attempt", "question"),
                name="unique_attempt_question_answer",
            )
        ]

    def __str__(self):
        return f"Answer to Question {self.question.position}"
