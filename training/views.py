from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
import uuid

from .models import User, Course, Enrollment, Quiz, Question, QuizSubmission, Certificate
from .serializers import (
    UserSerializer, RegisterSerializer, CourseSerializer,
    CourseDetailSerializer, EnrollmentSerializer, QuizSerializer,
    QuizSubmissionSerializer, CertificateSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CourseListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer


class MyEnrollmentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('course')


class EnrollCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'progress': 10}
        )
        if not created:
            return Response({'message': 'Already enrolled in this course', 'enrollment': EnrollmentSerializer(enrollment).data}, status=status.HTTP_200_OK)
        return Response({'message': 'Successfully enrolled', 'enrollment': EnrollmentSerializer(enrollment).data}, status=status.HTTP_201_CREATED)


class UpdateProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        progress = request.data.get('progress', 50)
        enrollment = get_object_or_404(Enrollment, user=request.user, course_id=course_id)
        enrollment.progress = min(100, max(0, int(progress)))
        if enrollment.progress >= 100:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
        enrollment.save()
        return Response(EnrollmentSerializer(enrollment).data)


class QuizDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class SubmitQuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        answers = request.data.get('answers', {})  # Dict of { question_id: 'A' }

        questions = quiz.questions.all()
        if not questions.exists():
            return Response({'error': 'This quiz has no questions available.'}, status=status.HTTP_400_BAD_REQUEST)

        correct_count = 0
        total_questions = questions.count()

        for question in questions:
            user_choice = answers.get(str(question.id)) or answers.get(int(question.id))
            if user_choice and str(user_choice).strip().upper() == question.correct_option:
                correct_count += 1

        score_percentage = round((correct_count / total_questions) * 100, 1)
        passed = score_percentage >= quiz.passing_score

        # Save submission record
        submission = QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            score_percentage=score_percentage,
            passed=passed
        )

        certificate_data = None
        if passed:
            # Update enrollment to 100% completed
            enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=quiz.course)
            enrollment.progress = 100
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()

            # Generate digital certificate if not already issued
            cert_id = f"ST-{uuid.uuid4().hex[:8].upper()}"
            certificate, _ = Certificate.objects.get_or_create(
                user=request.user,
                course=quiz.course,
                defaults={'certificate_id': cert_id}
            )
            certificate_data = CertificateSerializer(certificate).data

        return Response({
            'correct_count': correct_count,
            'total_questions': total_questions,
            'score_percentage': score_percentage,
            'passing_score': quiz.passing_score,
            'passed': passed,
            'certificate': certificate_data,
            'submission_id': submission.id
        }, status=status.HTTP_200_OK)


class MyCertificatesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user).select_related('course')


class CertificateVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, certificate_id):
        cert = get_object_or_404(Certificate, certificate_id=certificate_id)
        return Response(CertificateSerializer(cert).data)


class AdminAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Allow Admin or any staff to view analytics
        total_users = User.objects.filter(role='EMPLOYEE').count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        completed_enrollments = Enrollment.objects.filter(completed=True).count()
        total_certificates = Certificate.objects.count()

        avg_score = QuizSubmission.objects.aggregate(Avg('score_percentage'))['score_percentage__avg'] or 0

        completion_rate = round((completed_enrollments / total_enrollments * 100), 1) if total_enrollments > 0 else 0

        # Course popularity
        courses_data = Course.objects.annotate(
            enrolled_count=Count('enrollments')
        ).values('title', 'enrolled_count', 'category')[:5]

        return Response({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'completed_enrollments': completed_enrollments,
            'total_certificates': total_certificates,
            'completion_rate': completion_rate,
            'avg_score': round(avg_score, 1),
            'top_courses': list(courses_data)
        })
