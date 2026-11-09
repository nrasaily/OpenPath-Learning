from django.urls import path

from .views import (
    CourseListView,
    CourseOfferingListView,
    CourseDetailView,
    EnrollmentCreateView,
    MyEnrollmentListView,
)


urlpatterns = [
    path("", CourseListView.as_view(), name="course-list"),
    path("offerings/", CourseOfferingListView.as_view(), name="offering-list"),
    path("enrollments/", EnrollmentCreateView.as_view(), name="enrollment-create"),
    path("my-enrollments/", MyEnrollmentListView.as_view(), name="my-enrollments"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
]
