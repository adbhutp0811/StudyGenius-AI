from .gemini_service import GeminiService
import json
import re


class RoadmapGenerator:
    def __init__(self):
        self.gemini = GeminiService()

    def generate(self, career_goal, duration_months=6, skill_level='beginner', custom_goal=''):
        goal = custom_goal if custom_goal else career_goal

        prompt = f"""Create a personalized learning roadmap for someone pursuing {goal}.
Level: {skill_level}
Duration: {duration_months} months

Return a JSON object with:
- milestones: Array of milestone objects, each with:
  - title: Milestone name
  - description: What to learn/achieve
  - duration_days: Days to complete this milestone
  - resources: Array of resource objects with title, url (placeholder), type
- resources: Array of general resource objects with:
  - title: Resource name
  - description: What it covers
  - url: Placeholder URL
  - resource_type: One of: course, video, article, book, documentation, tool, project
  - is_free: boolean

Create {max(3, duration_months)} milestones spread across the {duration_months}-month period.
Include a mix of free and paid resources from well-known platforms (Coursera, Udemy, freeCodeCamp, YouTube, documentation)."""

        result = self.gemini._safe_generate(prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(result)
        except (json.JSONDecodeError, ValueError):
            return {
                'milestones': [
                    {
                        'title': f'Foundation in {goal}',
                        'description': f'Learn the basics and core concepts of {goal}',
                        'duration_days': 30,
                        'resources': [
                            {'title': 'Getting Started Guide', 'url': '', 'type': 'article'},
                        ]
                    },
                    {
                        'title': 'Intermediate Skills',
                        'description': 'Build on your foundation with more advanced topics',
                        'duration_days': 45,
                        'resources': [
                            {'title': 'Intermediate Course', 'url': '', 'type': 'course'},
                        ]
                    },
                    {
                        'title': 'Advanced Topics & Projects',
                        'description': 'Master advanced concepts and build real projects',
                        'duration_days': 60,
                        'resources': [
                            {'title': 'Build a Portfolio Project', 'url': '', 'type': 'project'},
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

Return a JSON object with:
- tasks: Array of daily task objects with:
  - day: Day number
  - title: Task title
  - description: Detailed task description
  - estimated_hours: Hours to complete
  - resources: Array of resource names
- notes: Study tips and recommendations"""

        result = self.gemini._safe_generate(prompt, use_fast=True)

        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(result)
        except (json.JSONDecodeError, ValueError):
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
