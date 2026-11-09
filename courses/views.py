from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Course
from .serializers import CourseSerializer


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True).order_by("title")
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


from .models import CourseOffering
from .serializers import CourseOfferingSerializer


class CourseOfferingListView(generics.ListAPIView):
    queryset = CourseOffering.objects.filter(
        is_open=True,
        course__is_published=True,
    ).select_related("course", "term").order_by("course__title")
    serializer_class = CourseOfferingSerializer
    permission_classes = [AllowAny]


from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentCreateView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.groups.filter(name="student").exists():
            raise PermissionDenied("Only student accounts can enroll.")

        serializer.save(student=user)


class MyEnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.groups.filter(name="student").exists():
            raise PermissionDenied("Only student accounts can view enrollments.")

        return Enrollment.objects.filter(
            student=user
        ).select_related(
            "offering__course",
            "offering__term",
        ).order_by("-enrolled_at")


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
