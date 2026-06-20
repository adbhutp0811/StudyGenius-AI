from .gemini_service import GeminiService
from apps.career.models import CareerRecommendation
import json
import re


class CareerService:
    def __init__(self):
        self.gemini = GeminiService()

    def generate_recommendation(self, assessment, scores):
        prompt = f"""Based on this skill assessment, generate career recommendations:

Category: {assessment.category}
Skills Evaluated: {json.dumps(assessment.skills_evaluated)}
Scores: {json.dumps(scores.get('scores', {}))}
Overall Score: {scores.get('overall_score', 0)}
Strengths: {json.dumps(scores.get('strengths', []))}
Weaknesses: {json.dumps(scores.get('weaknesses', []))}

Return a JSON object with:
- career_options: Array of 3-5 career paths with title, match_percentage, description, required_skills
- skill_gaps: Array of skills to develop with skill name, priority (high/medium/low), resources
- suggested_courses: Array of course recommendations with title, platform, url, reason
- industry_insights: Object with growing_fields, average_salaries, demand_level
- salary_insights: Object with entry_level, mid_level, senior_level ranges
- career_path: Array of career progression steps with role, years_experience, description
- internship_recommendations: Array of internship types to pursue
- project_recommendations: Array of projects to build with title, description, skills_gained
- summary: A personalized 2-3 paragraph career summary"""

        result = self.gemini._safe_generate(prompt)
        data = self.gemini._parse_json_response(result)

        if not isinstance(data, dict):
            data = {
                'career_options': [{'title': 'Continue Learning', 'match_percentage': 70, 'description': 'Focus on skill development', 'required_skills': []}],
                'skill_gaps': [],
                'suggested_courses': [],
                'industry_insights': {'growing_fields': [], 'average_salaries': [], 'demand_level': 'Moderate'},
                'salary_insights': {'entry_level': '$40k-$60k', 'mid_level': '$60k-$90k', 'senior_level': '$90k-$130k'},
                'career_path': [],
                'internship_recommendations': [],
                'project_recommendations': [],
                'summary': 'Continue developing your skills and exploring career options.',
            }

        recommendation = CareerRecommendation.objects.create(
            user=assessment.user,
            assessment=assessment,
            career_options=data.get('career_options', []),
            skill_gaps=data.get('skill_gaps', []),
            suggested_courses=data.get('suggested_courses', []),
            industry_insights=data.get('industry_insights', {}),
            salary_insights=data.get('salary_insights', {}),
            career_path=data.get('career_path', []),
            internship_recommendations=data.get('internship_recommendations', []),
            project_recommendations=data.get('project_recommendations', []),
            summary=data.get('summary', ''),
        )

        return recommendation
