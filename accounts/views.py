from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        student_group = Group.objects.get(name="student")
        user = serializer.save()
        user.groups.add(student_group)


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from .serializers import UserProfileSerializer


class MyProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


from .serializers import UserProfileSerializer


class MyProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


from .serializers import TeacherApplicationSignupSerializer


class TeacherApplicationSignupView(generics.CreateAPIView):
    serializer_class = TeacherApplicationSignupSerializer
    permission_classes = [AllowAny]


from django.shortcuts import get_object_or_404
from .models import TeacherApplication
from .serializers import TeacherApplicationStatusSerializer


class MyTeacherApplicationView(generics.RetrieveAPIView):
    serializer_class = TeacherApplicationStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            TeacherApplication,
            user=self.request.user,
        )


from rest_framework.exceptions import PermissionDenied


class TeacherDashboardAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.groups.filter(name="teacher").exists():
            raise PermissionDenied(
                "Teacher access is available after application approval."
            )

        return Response(
            {
                "detail": "Teacher access approved.",
                "email": request.user.email,
            }
        )


from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import EmailTokenSerializer


class EmailLoginView(ObtainAuthToken):
    serializer_class = EmailTokenSerializer


from courses.models import CourseOffering
from courses.serializers import CourseOfferingSerializer


class TeacherDashboardView(generics.ListAPIView):
    serializer_class = CourseOfferingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.groups.filter(name="teacher").exists():
            raise PermissionDenied(
                "Teacher access is available after application approval."
            )

        return CourseOffering.objects.filter(
            instructor=user
        ).select_related(
            "course",
            "term",
        ).order_by("course__title")
