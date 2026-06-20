from .gemini_service import GeminiService
import json


class RoadmapGenerator:
    def __init__(self):
        self.gemini = GeminiService()

    def _parse_json(self, text):
        parsed = self.gemini._parse_json_response(text)
        if parsed is not None:
            return parsed
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

    def generate(self, career_goal, duration_months=6, skill_level='beginner', custom_goal=''):
        goal = custom_goal if custom_goal else career_goal
        num_milestones = max(3, duration_months)

        prompt = f"""Create a personalized learning roadmap for someone pursuing {goal}.
Level: {skill_level}
Duration: {duration_months} months

Return ONLY valid JSON with this exact structure (no markdown, no code fences):
{{
  "milestones": [
    {{
      "title": "Milestone name",
      "description": "What to learn/achieve",
      "duration_days": 30,
      "resources": [
        {{"title": "Resource name", "url": "", "resource_type": "course"}}
      ]
    }}
  ],
  "resources": [
    {{
      "title": "Resource name",
      "description": "What it covers",
      "url": "",
      "resource_type": "course",
      "is_free": true
    }}
  ]
}}

Create exactly {num_milestones} milestones spread across the {duration_months}-month period.
resource_type must be one of: course, video, article, book, documentation, tool, project, other.
Include a mix of free and paid resources from well-known platforms (Coursera, Udemy, freeCodeCamp, YouTube, documentation)."""

        result = self.gemini._safe_generate(prompt)
        parsed = self._parse_json(result)

        if parsed and 'milestones' in parsed:
            return parsed

        return {
            'milestones': [
                {
                    'title': f'Foundation in {goal}',
                    'description': f'Learn the basics and core concepts of {goal}',
                    'duration_days': 30,
                    'resources': [
                        {'title': 'Getting Started Guide', 'url': '', 'resource_type': 'article'},
                    ]
                },
                {
                    'title': 'Intermediate Skills',
                    'description': f'Build on your foundation with more advanced topics in {goal}',
                    'duration_days': 45,
                    'resources': [
                        {'title': 'Intermediate Course', 'url': '', 'resource_type': 'course'},
                    ]
                },
                {
                    'title': 'Advanced Topics & Projects',
                    'description': 'Master advanced concepts and build real projects',
                    'duration_days': 60,
                    'resources': [
                        {'title': 'Build a Portfolio Project', 'url': '', 'resource_type': 'project'},
                    ]
                },
            ],
            'resources': [
                {'title': 'Getting Started Guide', 'description': f'Introduction to {goal}', 'url': '', 'resource_type': 'article', 'is_free': True},
            ]
        }

    def generate_daily_plan(self, milestone):
        prompt = f"""Create a detailed daily study plan for this milestone:
Title: {milestone.title}
Description: {milestone.description}
Duration: {milestone.duration_days} days

Return ONLY valid JSON with this exact structure (no markdown, no code fences):
{{
  "tasks": [
    {{
      "day": 1,
      "title": "Task title",
      "description": "Detailed task description",
      "estimated_hours": 2,
      "resources": []
    }}
  ],
  "notes": "Study tips and recommendations"
}}"""

        result = self.gemini._safe_generate(prompt, use_fast=True)
        parsed = self._parse_json(result)

        if parsed and 'tasks' in parsed:
            return parsed

        return {
            'tasks': [
                {
                    'day': 1,
                    'title': 'Introduction',
                    'description': 'Get started with the topic',
                    'estimated_hours': 2,
                    'resources': [],
                }
            ],
            'notes': 'Focus on understanding concepts before moving to practice.',
        }
