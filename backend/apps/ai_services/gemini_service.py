import os
import json
import re
from django.conf import settings
from groq import Groq


class GeminiService:
    def __init__(self):
        api_key = getattr(settings, 'GROQ_API_KEY', os.getenv('GROQ_API_KEY', ''))
        self.client = Groq(api_key=api_key) if api_key else None
        self.model_name = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.fast_model_name = os.getenv('GROQ_FAST_MODEL', 'llama-3.1-8b-instant')

    def _safe_generate(self, prompt, use_fast=False):
        if not self.client:
            return "Unable to generate response: GROQ_API_KEY is not configured."

        try:
            model_name = self.fast_model_name if use_fast else self.model_name
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Respond clearly and accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            return content.strip() if isinstance(content, str) else str(content)
        except Exception as e:
            return f"Unable to generate response: {str(e)}"

    def _parse_json_response(self, text):
        def repair_multiline_json(raw):
            result = []
            in_string = False
            escaped = False

            for char in raw:
                if in_string:
                    if escaped:
                        result.append(char)
                        escaped = False
                    elif char == '\\':
                        result.append(char)
                        escaped = True
                    elif char == '"':
                        result.append(char)
                        in_string = False
                    elif char in ('\n', '\r'):
                        result.append('\\n')
                    else:
                        result.append(char)
                else:
                    if char == '"':
                        result.append(char)
                        in_string = True
                    else:
                        result.append(char)

            return ''.join(result)

        try:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                cleaned = repair_multiline_json(json_match.group(1))
                return json.loads(cleaned)
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                cleaned = repair_multiline_json(json_match.group(0))
                return json.loads(cleaned)
            return json.loads(repair_multiline_json(text))
        except (json.JSONDecodeError, ValueError):
            return None

    def _build_fallback_questions(self, category, skill_level, skills=None):
        skills = skills or []
        skill_label = skills[0] if skills else category.replace('_', ' ').title()
        templates = [
            f"What interests you most about {category.replace('_', ' ')}?",
            f"Which {skill_label} tasks do you enjoy most?",
            f"How comfortable are you learning new tools in {category.replace('_', ' ')}?",
            f"What kind of projects would you like to build in this field?",
            f"How do you usually approach solving a difficult problem?",
            f"What resources have helped you learn best so far?",
            f"Which skills do you want to improve first?",
            f"How do you prefer to work: alone, in a team, or both?",
            f"What career goals do you have for the next few years?",
            f"How important is hands-on practice when learning a new skill?",
        ]

        questions = []
        for index, question in enumerate(templates):
            questions.append({
                'id': f'q{index + 1}',
                'question': question,
                'type': 'mcq',
                'options': [
                    'I enjoy it a lot',
                    'I am somewhat interested',
                    'I am not sure yet',
                    'I prefer other areas'
                ],
                'skill': skill_label,
                'difficulty': 'easy' if index < 4 else 'medium',
                'marks': 1,
            })

        return {'questions': questions}

    def generate_text(self, prompt):
        return self._safe_generate(prompt, use_fast=True)

    def answer_doubt(self, question, subject, chat_history=None, code=''):
        chat_history = chat_history or []
        context = ''
        if chat_history:
            context = '\n'.join([f"{m['role']}: {m['content']}" for m in chat_history[-6:]])

        prompt = f"""You are an AI tutor helping a student with {subject}.

Previous conversation context:
{context}

Student's question: {question}

{f'Code provided: {code}' if code else ''}

Provide a clear, detailed, and helpful answer. If there's code, explain it line by line. Include examples where helpful.
Format your response with sections and bullet points for readability."""
        return self._safe_generate(prompt)

    def analyze_image(self, image, question=''):
        try:
            prompt = f"Analyze this image. {question}" if question else "Describe and analyze this image in detail."
            return self._safe_generate(prompt)
        except Exception as e:
            return f"Unable to analyze image: {str(e)}"

    def generate_blog(self, keywords, title='', tone='professional', length='medium', target_audience=''):
        length_map = {'short': '500-800 words', 'medium': '1000-1500 words', 'long': '2000-3000 words'}

        prompt = f"""Generate a blog article with the following parameters:
Keywords: {', '.join(keywords)}
{f'Title: {title}' if title else 'Generate an engaging title'}
Tone: {tone}
Length: {length_map.get(length, '1000-1500 words')}
{f'Target Audience: {target_audience}' if target_audience else ''}

Return a JSON object with:
- title: The blog title
- content: Full blog content in markdown format
- excerpt: A 2-3 sentence summary
- seo_title: SEO-optimized title (max 60 chars)
- seo_description: Meta description (max 160 chars)
- seo_tags: Array of 5-10 SEO tags"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict):
            return parsed

        return {
            'title': title or 'Generated Blog',
            'content': raw_response,
            'excerpt': '',
            'seo_title': '',
            'seo_description': '',
            'seo_tags': [],
        }

    def optimize_seo(self, title, content, keywords):
        prompt = f"""Analyze and optimize this blog content for SEO:
Title: {title}
Keywords: {', '.join(keywords)}
Content: {content[:2000]}

Return a JSON object with:
- seo_title: Optimized title (max 60 chars)
- seo_description: Optimized meta description (max 160 chars)
- seo_tags: Array of 10-15 SEO tags
- suggestions: Array of objects with type, current, suggested, reason"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict):
            return parsed

        return {
            'seo_title': title,
            'seo_description': '',
            'seo_tags': [],
            'suggestions': [],
        }

    def check_grammar(self, content):
        prompt = f"""Check this content for grammar, spelling, and style issues:

{content[:3000]}

Return a JSON object with:
- has_issues: boolean
- issues: Array of objects with type, original, suggestion, explanation
- corrected_content: The full corrected version
- score: A grammar score from 0-100"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict):
            return parsed

        return {
            'has_issues': False,
            'issues': [],
            'corrected_content': content,
            'score': 100,
        }

    def generate_quiz_from_content(self, summary, key_points):
        prompt = f"""Based on this content, generate a quiz with 5 multiple-choice questions:

Summary: {summary}
Key Points: {json.dumps(key_points)}

Return a JSON array of objects with:
- question: The question
- options: Array of 4 options
- correct_answer: The correct option
- explanation: Why this is correct"""
        return self._safe_generate(prompt)

    def answer_pdf_question(self, question, context, chat_history=None):
        chat_history = chat_history or []
        context_text = '\n'.join([f"{m['role']}: {m['content']}" for m in chat_history[-6:]]) if chat_history else ''

        prompt = f"""Answer the question based on the provided document context.

Document Context:
{context[:8000]}

Chat History:
{context_text}

Question: {question}

Provide a comprehensive answer citing specific parts of the document. If the answer is not in the context, say so.
Return your response and relevant_sections as a JSON object:
- answer: Your detailed response
- relevant_sections: Array of relevant text passages from the document"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict) and 'answer' in parsed:
            return parsed.get('answer', ''), parsed.get('relevant_sections', [])

        return raw_response, []

    def generate_assessment(self, category, skill_level, skills=None):
        skills = skills or []
        skills_text = ', '.join(skills) if skills else 'general knowledge'

        prompt = f"""Generate a skill assessment for {category} at {skill_level} level.
Skills to evaluate: {skills_text}

Return a JSON object with:
- questions: Array of 10 objects with:
  - id: unique string
  - question: The question text
  - type: "mcq" or "theory"
  - options: Array of 4 options (for MCQ)
  - skill: Which skill this evaluates
  - difficulty: easy/medium/hard
  - marks: Points for this question"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict) and isinstance(parsed.get('questions'), list):
            valid_questions = [
                q for q in parsed.get('questions', [])
                if isinstance(q, dict) and q.get('id') and q.get('question')
            ]
            if len(valid_questions) >= 5:
                return parsed

        return self._build_fallback_questions(category, skill_level, skills)

    def evaluate_assessment(self, questions, answers):
        prompt = f"""Evaluate this assessment:

Questions: {json.dumps(questions)}
Answers: {json.dumps(answers)}

Return a JSON object with:
- scores: Object with skill names as keys and scores (0-100) as values
- overall_score: Overall percentage score
- recommendations: Array of improvement recommendations based on performance
- strengths: Array of strong areas
- weaknesses: Array of areas needing improvement"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict):
            scores = parsed.get('scores')
            if isinstance(scores, dict) and 'overall_score' in parsed:
                return parsed

        questions = questions or []
        answers = answers or {}
        skill_scores = {}
        for question in questions:
            if not isinstance(question, dict):
                continue
            skill_name = question.get('skill') or 'General'
            skill_scores[skill_name] = skill_scores.get(skill_name, 0)

        answered_count = sum(1 for value in answers.values() if value not in (None, ''))
        overall_score = min(100, round((answered_count / max(len(questions), 1)) * 100)) if questions else 0

        if skill_scores:
            base = max(0, overall_score - 10)
            for skill_name in skill_scores:
                skill_scores[skill_name] = min(100, max(0, base + (len(skill_scores) * 2)))
        else:
            skill_scores = {'General': overall_score}

        return {
            'scores': skill_scores,
            'overall_score': overall_score,
            'recommendations': [
                'Practice consistently with short daily exercises.',
                'Review concepts and apply them to small real projects.'
            ],
            'strengths': ['Shows initiative and willingness to learn.'],
            'weaknesses': ['Could improve consistency and hands-on practice.'],
        }

    def generate_question_paper(self, subject, syllabus='', difficulty='medium',
                                 num_mcq=5, num_short_answer=5, num_long_answer=3):
        prompt = f"""Generate a question paper for {subject}.
Syllabus: {syllabus if syllabus else 'General curriculum'}
Difficulty: {difficulty}
Requirements:
- {num_mcq} Multiple Choice Questions (1 mark each)
- {num_short_answer} Short Answer Questions (2 marks each)
- {num_long_answer} Long Answer Questions (5 marks each)

Return a JSON object with:
- title: The paper title
- questions: Array of all questions with:
  - id: unique string
  - type: "mcq" or "short_answer" or "long_answer"
  - question: The question text
  - options: Array of 4 options (for MCQ only)
  - correct_answer: The answer (for easy grading)
  - marks: Marks for this question
  - difficulty: easy/medium/hard"""
        raw_response = self._safe_generate(prompt)
        parsed = self._parse_json_response(raw_response)

        if isinstance(parsed, dict):
            return parsed

        return {
            'title': f"{subject} {difficulty.title()} Question Paper",
            'questions': [],
        }
