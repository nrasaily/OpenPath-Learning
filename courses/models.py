from django.db import models


class AcademicTerm(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=80, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PLANNING,
    )

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    class Level(models.TextChoices):
        SECONDARY = "secondary", "Secondary"
        FOUNDATION = "foundation", "Foundation"

    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=150)
    subject = models.CharField(max_length=80)
    subject_catalog = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="courses",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.SECONDARY,
    )
    grade = models.PositiveSmallIntegerField(
        choices=(
            (9, "Grade 9"),
            (10, "Grade 10"),
            (11, "Grade 11"),
            (12, "Grade 12"),
        ),
        null=True,
        blank=True,
        help_text="Leave blank for foundation courses.",
    )
    language_tag = models.CharField(
        max_length=35,
        default="en",
        help_text="Language tag, for example en, ne, hi, or ur.",
    )
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} — {self.title}"


from django.conf import settings


class CourseOffering(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="offerings",
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.PROTECT,
        related_name="offerings",
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_offerings",
        null=True,
        blank=True,
    )
    section_code = models.CharField(max_length=30)
    capacity = models.PositiveSmallIntegerField(default=30)
    is_open = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("course", "term", "section_code"),
                name="unique_course_term_section",
            )
        ]

    def __str__(self):
        return f"{self.course.code} / {self.term.name} / {self.section_code}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_enrollments",
    )
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("student", "offering"),
                name="unique_student_offering_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student.email} — {self.offering}"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    language_tag = models.CharField(max_length=10, default="en")
    position = models.PositiveSmallIntegerField()
    estimated_minutes = models.PositiveSmallIntegerField(default=30)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ("position",)
        constraints = [
            models.UniqueConstraint(
                fields=("course", "position", "language_tag"),
                name="unique_course_lesson_language_position",
            )
        ]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class ClassGroup(models.Model):
    grade = models.PositiveSmallIntegerField(
        choices=(
            (9, "Grade 9"),
            (10, "Grade 10"),
            (11, "Grade 11"),
            (12, "Grade 12"),
        )
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.PROTECT,
        related_name="class_groups",
    )
    section_code = models.CharField(max_length=30)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advisory_class_groups",
    )
    course_offerings = models.ManyToManyField(
        CourseOffering,
        blank=True,
        related_name="class_groups",
    )

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        constraints = [
            models.UniqueConstraint(
                fields=("grade", "term", "section_code"),
                name="unique_grade_term_class_section",
            )
        ]

    def __str__(self):
        return f"Grade {self.grade} — {self.section_code} — {self.term.name}"
