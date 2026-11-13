from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "preferred_language",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        student_group, _ = Group.objects.get_or_create(name="student")
        user.groups.add(student_group)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "preferred_language",
        )
        read_only_fields = fields


from django.db import transaction
from .models import TeacherApplication


class TeacherApplicationSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    preferred_language = serializers.CharField(max_length=10, default="en")
    country = serializers.CharField(max_length=100)
    subject_areas = serializers.CharField(max_length=300)
    teaching_languages = serializers.CharField(max_length=300)
    years_experience = serializers.IntegerField(min_value=0, max_value=60)
    qualifications = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def to_representation(self, instance):
        return {
            "id": instance.pk,
            "email": instance.user.email,
            "status": instance.status,
            "submitted_at": instance.submitted_at.isoformat(),
        }

    @transaction.atomic
    def create(self, validated_data):
        user_data = {
            "email": validated_data.pop("email"),
            "password": validated_data.pop("password"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "preferred_language": validated_data.pop("preferred_language", "en"),
        }
        user = User.objects.create_user(**user_data)
        return TeacherApplication.objects.create(user=user, **validated_data)


class TeacherApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherApplication
        fields = (
            "status",
            "country",
            "subject_areas",
            "teaching_languages",
            "years_experience",
            "submitted_at",
            "reviewed_at",
            "review_notes",
        )
        read_only_fields = fields


from django.contrib.auth import authenticate


class EmailTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs
