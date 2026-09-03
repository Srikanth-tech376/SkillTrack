from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Enrollment, Quiz, Question, QuizSubmission, Certificate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'department')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'role', 'department')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'EMPLOYEE'),
            department=validated_data.get('department', 'Engineering')
        )
        return user


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'content', 'order')


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)
    has_quiz = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'category', 'duration_hours', 'thumbnail_url', 'created_at', 'lessons_count', 'has_quiz')

    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz')


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    quiz_id = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'category', 'duration_hours', 'thumbnail_url', 'created_at', 'lessons', 'quiz_id')

    def get_quiz_id(self, obj):
        return obj.quiz.id if hasattr(obj, 'quiz') else None


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ('id', 'user', 'course', 'course_id', 'progress', 'completed', 'enrolled_at', 'completed_at')
        read_only_fields = ('id', 'user', 'progress', 'completed', 'enrolled_at', 'completed_at')


class QuestionSerializer(serializers.ModelSerializer):
    """
    Public question serializer: omits correct_option so students cannot inspect client-side JSON to cheat!
    """
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'course_title', 'title', 'passing_score', 'questions')


class QuizSubmissionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = ('id', 'user', 'quiz', 'quiz_title', 'score_percentage', 'passed', 'submitted_at')
        read_only_fields = ('id', 'user', 'score_percentage', 'passed', 'submitted_at')


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ('id', 'certificate_id', 'recipient_name', 'course_title', 'issued_at')

    def get_recipient_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else obj.user.username
