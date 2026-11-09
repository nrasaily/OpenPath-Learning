from django.urls import path

from .views import (
    EmailLoginView,
    LogoutView,
    MyProfileView,
    MyTeacherApplicationView,
    TeacherApplicationSignupView,
    TeacherDashboardView,
    UserRegistrationView,
)


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path(
        "teacher-signup/",
        TeacherApplicationSignupView.as_view(),
        name="teacher-signup",
    ),
    path(
        "teacher-application/",
        MyTeacherApplicationView.as_view(),
        name="my-teacher-application",
    ),
    path(
        "teacher-dashboard/",
        TeacherDashboardView.as_view(),
        name="teacher-dashboard",
    ),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MyProfileView.as_view(), name="my-profile"),
]
