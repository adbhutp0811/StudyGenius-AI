from .gemini_service import GeminiService
import json
import re


class ResumeAnalyzer:
    def __init__(self):
        self.gemini = GeminiService()

    def analyze(self, resume):
        resume_data = {
            'full_name': resume.full_name,
            'email': resume.email,
            'phone': resume.phone,
            'professional_summary': resume.professional_summary,
            'skills': resume.skills,
            'experience': resume.experience,
            'education': resume.education,
            'certifications': resume.certifications,
            'projects': resume.projects,
        }

        prompt = f"""Analyze this resume and provide a comprehensive evaluation:

{json.dumps(resume_data, indent=2)}

Return a JSON object with:
- score: Overall ATS score (0-100)
- strengths: Array of 3-5 strengths
- weaknesses: Array of 3-5 weaknesses
- suggestions: Array of specific improvement suggestions
- keyword_analysis: Object with found_keywords (array), missing_keywords (array), industry_keywords (array)
- section_scores: Object with scores for each section (summary, experience, education, skills, projects)
- improvement_tips: A detailed paragraph with actionable improvement advice"""

        result = self.gemini._safe_generate(prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                analysis = json.loads(result)
        except (json.JSONDecodeError, ValueError):
            analysis = {
                'score': 70,
                'strengths': ['Resume is complete'],
                'weaknesses': ['Could not perform detailed analysis'],
                'suggestions': ['Ensure all sections are well populated'],
                'keyword_analysis': {'found_keywords': [], 'missing_keywords': [], 'industry_keywords': []},
                'section_scores': {'summary': 70, 'experience': 70, 'education': 70, 'skills': 70, 'projects': 70},
                'improvement_tips': 'Review your resume against job descriptions in your target industry.',
            }

        return analysis
