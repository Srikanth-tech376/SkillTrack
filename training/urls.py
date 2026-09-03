from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView, CurrentUserView, CourseListView, CourseDetailView,
    MyEnrollmentsView, EnrollCourseView, UpdateProgressView,
    QuizDetailView, SubmitQuizView, MyCertificatesView,
    CertificateVerifyView, AdminAnalyticsView
)

urlpatterns = [
    # Authentication & Profile
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),

    # Courses
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:course_id>/enroll/', EnrollCourseView.as_view(), name='enroll_course'),
    path('courses/<int:course_id>/progress/', UpdateProgressView.as_view(), name='update_progress'),

    # Enrollments & Learning
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),

    # Assessments & Quizzes
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='submit_quiz'),

    # Certificates
    path('my-certificates/', MyCertificatesView.as_view(), name='my_certificates'),
    path('certificates/verify/<str:certificate_id>/', CertificateVerifyView.as_view(), name='verify_certificate'),

    # Admin & Analytics
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),
]
