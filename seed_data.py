import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skilltrack.settings')
django.setup()

from training.models import User, Course, Lesson, Enrollment, Quiz, Question

def seed():
    print("[*] Seeding SkillTrack initial database...")

    # 1. Create Admin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@skilltrack.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'ADMIN',
            'department': 'Human Resources',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("[+] Created Admin user: admin (password: admin123)")
    else:
        admin_user.set_password('admin123')
        admin_user.save()
        print("[+] Updated Admin user password to admin123")

    # 2. Create Demo Employee User
    emp_user, created = User.objects.get_or_create(
        username='srikanth',
        defaults={
            'email': 'srikanth@skilltrack.com',
            'first_name': 'Srikanth',
            'last_name': 'Reddy',
            'role': 'EMPLOYEE',
            'department': 'Software Engineering'
        }
    )
    if created:
        emp_user.set_password('srikanth123')
        emp_user.save()
        print("[+] Created Employee user: srikanth (password: srikanth123)")
    else:
        emp_user.set_password('srikanth123')
        emp_user.save()
        print("[+] Updated Employee user password to srikanth123")

    # 3. Create Courses
    c1, _ = Course.objects.get_or_create(
        title='Python & Django REST Framework Fundamentals',
        defaults={
            'description': 'Master backend engineering with Python, Django ORM, RESTful API design, and JWT authentication.',
            'category': 'Backend Development',
            'duration_hours': 12,
            'thumbnail_url': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600'
        }
    )

    Lesson.objects.get_or_create(
        course=c1, order=1,
        title='Introduction to REST APIs & HTTP Protocol',
        defaults={'content': 'REST stands for Representational State Transfer. In this lesson, we explore HTTP methods: GET, POST, PUT, DELETE, status codes (200, 201, 400, 401, 404, 500), and stateless client-server communication.'}
    )
    Lesson.objects.get_or_create(
        course=c1, order=2,
        title='Django Models, Migrations & ORM',
        defaults={'content': 'Learn how Django Object-Relational Mapping (ORM) translates Python classes into SQL tables, foreign key relationships, and migration files.'}
    )
    Lesson.objects.get_or_create(
        course=c1, order=3,
        title='Securing Endpoints with JWT Authentication',
        defaults={'content': 'Understand JSON Web Tokens (JWT), Access vs Refresh tokens, Bearer token authorization headers, and Role-Based Access Control.'}
    )

    # Quiz for Course 1
    q1, _ = Quiz.objects.get_or_create(course=c1, defaults={'title': 'Python Backend Assessment', 'passing_score': 65})
    Question.objects.get_or_create(
        quiz=q1, question_text='Which HTTP status code signifies that a resource was successfully created?',
        defaults={'option_a': '200 OK', 'option_b': '201 Created', 'option_c': '204 No Content', 'option_d': '202 Accepted', 'correct_option': 'B'}
    )
    Question.objects.get_or_create(
        quiz=q1, question_text='What does JWT stand for in modern web authentication?',
        defaults={'option_a': 'Java Web Technology', 'option_b': 'JSON Web Token', 'option_c': 'Joint Web Terminal', 'option_d': 'JavaScript Working Thread', 'correct_option': 'B'}
    )
    Question.objects.get_or_create(
        quiz=q1, question_text='Which Django component is responsible for serializing database models into JSON?',
        defaults={'option_a': 'ModelViewSet / Serializer', 'option_b': 'WSGI Handler', 'option_c': 'URL Resolver', 'option_d': 'Template Engine', 'correct_option': 'A'}
    )

    # Course 2
    c2, _ = Course.objects.get_or_create(
        title='Generative AI, Prompt Engineering & RAG Systems',
        defaults={
            'description': 'Understand Large Language Models, vector embeddings, chunking strategies, and building reliable RAG architectures.',
            'category': 'Artificial Intelligence',
            'duration_hours': 15,
            'thumbnail_url': 'https://images.unsplash.com/photo-1677442136019-21780efad99a?w=600'
        }
    )
    Lesson.objects.get_or_create(
        course=c2, order=1,
        title='Core Concepts of Large Language Models (LLMs)',
        defaults={'content': 'Learn tokenization, attention mechanisms, context windows, and how temperature influences generation randomness.'}
    )
    Lesson.objects.get_or_create(
        course=c2, order=2,
        title='RAG: Retrieval-Augmented Generation Architecture',
        defaults={'content': 'Explore document loaders, chunking strategies (overlap, size), vector embeddings, and semantic similarity search using cosine similarity.'}
    )
    q2, _ = Quiz.objects.get_or_create(course=c2, defaults={'title': 'Generative AI & RAG Assessment', 'passing_score': 70})
    Question.objects.get_or_create(
        quiz=q2, question_text='What is the primary purpose of RAG (Retrieval-Augmented Generation)?',
        defaults={'option_a': 'To train models from scratch', 'option_b': 'To ground LLM responses with external context and reduce hallucinations', 'option_c': 'To increase GPU memory usage', 'option_d': 'To compress images into text', 'correct_option': 'B'}
    )
    Question.objects.get_or_create(
        quiz=q2, question_text='Which metric is commonly used to calculate semantic similarity between vector embeddings?',
        defaults={'option_a': 'Cosine Similarity', 'option_b': 'Linear Regression', 'option_c': 'Binary Entropy', 'option_d': 'Standard Deviation', 'correct_option': 'A'}
    )

    # Course 3
    c3, _ = Course.objects.get_or_create(
        title='Modern React.js & Frontend State Management',
        defaults={
            'description': 'Build responsive, fast web interfaces with React functional components, hooks, Axios client, and Tailwind CSS.',
            'category': 'Frontend Development',
            'duration_hours': 10,
            'thumbnail_url': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=600'
        }
    )
    Lesson.objects.get_or_create(
        course=c3, order=1,
        title='React Hooks: useState, useEffect & custom hooks',
        defaults={'content': 'Managing component state, side effects, API fetching, and lifecycle synchronization using modern React hooks.'}
    )

    # Enroll demo user in course 1
    Enrollment.objects.get_or_create(user=emp_user, course=c1, defaults={'progress': 33})

    print("[SUCCESS] Seeding completed successfully! Created 3 courses, lessons, quizzes, and demo accounts.")

if __name__ == '__main__':
    seed()
