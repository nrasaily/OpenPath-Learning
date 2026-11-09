from django.urls import path

from .views import (
    AssessmentListView,
    MyAssessmentAttemptsView,
    StartAssessmentAttemptView,
    SubmitAssessmentAttemptView,
    SubmitAttemptAnswerView,
)


urlpatterns = [
    path("", AssessmentListView.as_view(), name="assessment-list"),
    path(
        "attempts/",
        StartAssessmentAttemptView.as_view(),
        name="assessment-attempt-start",
    ),
    path(
        "attempts/<int:attempt_id>/answers/",
        SubmitAttemptAnswerView.as_view(),
        name="attempt-answer-submit",
    ),
    path(
        "attempts/<int:attempt_id>/submit/",
        SubmitAssessmentAttemptView.as_view(),
        name="assessment-attempt-submit",
    ),
    path(
        "my-attempts/",
        MyAssessmentAttemptsView.as_view(),
        name="my-assessment-attempts",
    ),
]
