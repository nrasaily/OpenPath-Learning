from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Assessment
from .serializers import AssessmentSerializer


class AssessmentListView(generics.ListAPIView):
    queryset = Assessment.objects.filter(
        is_published=True
    ).prefetch_related(
        "questions__options"
    ).order_by("title")
    serializer_class = AssessmentSerializer
    permission_classes = [AllowAny]


from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import AssessmentAttempt
from .serializers import AssessmentAttemptStartSerializer


class StartAssessmentAttemptView(generics.CreateAPIView):
    serializer_class = AssessmentAttemptStartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.groups.filter(name="student").exists():
            raise PermissionDenied("Only student accounts can start assessments.")

        serializer.save(student=user)


from django.shortcuts import get_object_or_404
from .models import AttemptAnswer
from .serializers import AttemptAnswerSerializer


class SubmitAttemptAnswerView(generics.CreateAPIView):
    serializer_class = AttemptAnswerSerializer
    permission_classes = [IsAuthenticated]

    def get_attempt(self):
        return get_object_or_404(
            AssessmentAttempt,
            pk=self.kwargs["attempt_id"],
            student=self.request.user,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["attempt"] = self.get_attempt()
        return context

    def perform_create(self, serializer):
        serializer.save(attempt=self.get_attempt())


from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SubmitAssessmentAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):
        attempt = get_object_or_404(
            AssessmentAttempt,
            pk=attempt_id,
            student=request.user,
        )

        if attempt.status != AssessmentAttempt.Status.IN_PROGRESS:
            return Response(
                {"detail": "This attempt has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unanswered = attempt.assessment.questions.filter(
            is_required=True
        ).exclude(
            submitted_answers__attempt=attempt
        )

        if unanswered.exists():
            return Response(
                {"detail": "Answer all required questions before submitting."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = attempt.answers.select_related(
            "question",
            "selected_option",
        )

        for answer in answers:
            if answer.question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
                answer.is_correct = answer.selected_option.is_correct
                answer.points_awarded = (
                    Decimal(answer.question.points)
                    if answer.is_correct
                    else Decimal("0")
                )
                answer.save(update_fields=("is_correct", "points_awarded"))

        needs_teacher_review = attempt.answers.filter(
            question__question_type__in=(
                Question.QuestionType.SHORT_ANSWER,
                Question.QuestionType.ESSAY,
            )
        ).exists()

        attempt.submitted_at = timezone.now()

        if needs_teacher_review:
            attempt.status = AssessmentAttempt.Status.SUBMITTED
            attempt.score = None
        else:
            attempt.status = AssessmentAttempt.Status.GRADED
            attempt.score = sum(
                (answer.points_awarded for answer in attempt.answers.all()),
                Decimal("0"),
            )

        attempt.save(update_fields=("submitted_at", "status", "score"))

        return Response(
            {
                "detail": "Assessment submitted.",
                "status": attempt.status,
                "score": str(attempt.score) if attempt.score is not None else None,
            },
            status=status.HTTP_200_OK,
        )


from .models import Question


from .serializers import AssessmentAttemptResultSerializer


class MyAssessmentAttemptsView(generics.ListAPIView):
    serializer_class = AssessmentAttemptResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AssessmentAttempt.objects.filter(
            student=self.request.user
        ).select_related("assessment").order_by("-started_at")
