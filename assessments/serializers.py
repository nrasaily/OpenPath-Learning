from rest_framework import serializers

from .models import AnswerOption, Assessment, Question


class PublicAnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ("id", "text", "position")


class QuestionSerializer(serializers.ModelSerializer):
    options = PublicAnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "prompt", "question_type", "points", "position", "options")


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = (
            "id",
            "title",
            "description",
            "assessment_type",
            "course",
            "language_tag",
            "time_limit_minutes",
            "questions",
        )


from .models import AssessmentAttempt


class AssessmentAttemptStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAttempt
        fields = ("id", "assessment", "status", "started_at")
        read_only_fields = ("id", "status", "started_at")

    def validate_assessment(self, assessment):
        if not assessment.is_published:
            raise serializers.ValidationError(
                "This assessment is not available."
            )
        return assessment


from .models import AttemptAnswer, Question


class AttemptAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = ("question", "selected_option", "text_response")

    def validate(self, attrs):
        attempt = self.context["attempt"]
        question = attrs["question"]
        option = attrs.get("selected_option")

        if attempt.status != AssessmentAttempt.Status.IN_PROGRESS:
            raise serializers.ValidationError("This attempt is not in progress.")

        if question.assessment_id != attempt.assessment_id:
            raise serializers.ValidationError(
                "This question is not part of the assessment."
            )

        if question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
            if option is None or option.question_id != question.id:
                raise serializers.ValidationError(
                    "Choose an option for this question."
                )
        elif option is not None:
            raise serializers.ValidationError(
                "Written questions cannot use a multiple-choice option."
            )

        if question.question_type != Question.QuestionType.MULTIPLE_CHOICE:
            if not attrs.get("text_response", "").strip():
                raise serializers.ValidationError(
                    "Enter a written response for this question."
                )

        return attrs


class AssessmentAttemptResultSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(
        source="assessment.title",
        read_only=True,
    )

    class Meta:
        model = AssessmentAttempt
        fields = (
            "id",
            "assessment_title",
            "status",
            "score",
            "feedback",
            "started_at",
            "submitted_at",
        )
        read_only_fields = fields
