import os
print('START')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
print('DJANGO_IMPORT_OK')
django.setup()
print('DJANGO_SETUP_OK')
from apps.ai_services.gemini_service import GeminiService
from apps.ai_services.career_service import CareerService
from apps.career.models import SkillAssessment
from django.contrib.auth import get_user_model

print('IMPORTS_OK')
User = get_user_model()
user, created = User.objects.get_or_create(
    email='career-test@example.com',
    defaults={'username': 'career-test', 'full_name': 'Career Test'}
)
if created:
    user.set_password('123456')
    user.save()
print('USER_OK', user.id, created)

assessment = SkillAssessment.objects.create(
    user=user,
    title='Test Assessment',
    category='technology',
    skills_evaluated=['Python', 'Django'],
    questions=[
        {
            'id': 'q1',
            'question': 'What is Python?',
            'type': 'mcq',
            'options': ['A programming language', 'A database', 'A browser', 'An OS'],
            'skill': 'Python',
            'difficulty': 'easy',
            'marks': 1,
        }
    ],
    answers={'q1': 'A programming language'}
)
print('ASSESSMENT_OK', assessment.id)

service = GeminiService()
results = service.evaluate_assessment(assessment.questions, assessment.answers)
print('RESULTS_TYPE', type(results))
print('RESULTS', results)

career_service = CareerService()
rec = career_service.generate_recommendation(assessment=assessment, scores=results)
print('REC_OK', rec is not None)
if rec:
    print('REC_FIELDS', rec.career_options[:2])
    print('REC_SUMMARY', rec.summary)
