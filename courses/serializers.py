from rest_framework import serializers

from .models import Course


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


from .models import CourseOffering


class CourseOfferingSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    term_name = serializers.CharField(source="term.name", read_only=True)

    class Meta:
        model = CourseOffering
        fields = (
            "id",
            "course",
            "course_title",
            "term",
            "term_name",
            "section_code",
            "capacity",
            "is_open",
        )


from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "offering", "status", "enrolled_at")
        read_only_fields = ("id", "status", "enrolled_at")

    def validate_offering(self, offering):
        if not offering.is_open:
            raise serializers.ValidationError("This course section is closed.")

        if offering.enrollments.count() >= offering.capacity:
            raise serializers.ValidationError("This course section is full.")

        request = self.context.get("request")
        if request and offering.enrollments.filter(student=request.user).exists():
            raise serializers.ValidationError("You are already enrolled in this section.")

        return offering


from .models import Lesson


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
