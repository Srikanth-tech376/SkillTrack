from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Lesson, Enrollment, Quiz, Question, QuizSubmission, Certificate

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('role', 'department')}),
    )
    list_display = ('username', 'email', 'role', 'department', 'is_staff')
    list_filter = ('role', 'department', 'is_staff')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration_hours', 'created_at')
    search_fields = ('title', 'category')
    inlines = [LessonInline]

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score')
    inlines = [QuestionInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'completed', 'enrolled_at')
    list_filter = ('completed', 'course')

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score_percentage', 'passed', 'submitted_at')
    list_filter = ('passed', 'quiz')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'user', 'course', 'issued_at')
    search_fields = ('certificate_id', 'user__username', 'course__title')
