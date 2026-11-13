from rest_framework import serializers

from .models import Course, CourseOffering, Enrollment, Lesson


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "title",
            "subject",
            "description",
            "level",
            "grade",
            "language_tag",
            "is_published",
        )


class CourseOfferingSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="course.code", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    grade = serializers.IntegerField(
        source="course.grade",
        read_only=True,
        allow_null=True,
    )
    term_name = serializers.CharField(source="term.name", read_only=True)

    class Meta:
        model = CourseOffering
        fields = (
            "id",
            "course",
            "course_code",
            "course_title",
            "grade",
            "term",
            "term_name",
            "section_code",
            "capacity",
            "is_open",
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(
        source="offering.course.code",
        read_only=True,
    )
    course_title = serializers.CharField(
        source="offering.course.title",
        read_only=True,
    )
    grade = serializers.IntegerField(
        source="offering.course.grade",
        read_only=True,
        allow_null=True,
    )
    term_name = serializers.CharField(
        source="offering.term.name",
        read_only=True,
    )
    section_code = serializers.CharField(
        source="offering.section_code",
        read_only=True,
    )

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "offering",
            "course_code",
            "course_title",
            "grade",
            "term_name",
            "section_code",
            "status",
            "enrolled_at",
        )
        read_only_fields = ("id", "status", "enrolled_at")

    def validate_offering(self, offering):
        if not offering.course.is_published:
            raise serializers.ValidationError("This course is not published.")

        if offering.term.status != "open":
            raise serializers.ValidationError("This academic term is not open.")

        if not offering.is_open:
            raise serializers.ValidationError("This course section is closed.")

        active_enrollments = offering.enrollments.filter(
            status=Enrollment.Status.ENROLLED
        ).count()
        if active_enrollments >= offering.capacity:
            raise serializers.ValidationError("This course section is full.")

        request = self.context.get("request")
        if request and offering.enrollments.filter(student=request.user).exists():
            raise serializers.ValidationError(
                "You are already enrolled in this section."
            )

        return offering


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "title",
            "description",
            "content",
            "language_tag",
            "position",
            "estimated_minutes",
        )
