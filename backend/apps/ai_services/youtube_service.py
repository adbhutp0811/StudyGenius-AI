from .gemini_service import GeminiService
import re
import json
import urllib.parse


class YouTubeService:
    def __init__(self):
        self.gemini = GeminiService()

    def extract_video_id(self, url):
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def extract_and_summarize(self, url, language='en'):
        video_id = self.extract_video_id(url)
        if not video_id:
            return {'error': 'Invalid YouTube URL'}

        try:
            import requests
            from urllib.parse import parse_qs, urlparse

            # Fetch video page to get metadata and captions
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(f'https://www.youtube.com/watch?v={video_id}', headers=headers)

            if response.status_code != 200:
                return {'error': 'Could not fetch video information'}

            # Extract video info from page
            title_match = re.search(r'<title>(.*?)</title>', response.text)
            title = title_match.group(1).replace(' - YouTube', '') if title_match else 'Unknown Title'

            channel_match = re.search(r'"author":"(.*?)"', response.text)
            channel_name = channel_match.group(1) if channel_match else ''

            # Get transcript-like content via Gemini based on title and description
            desc_match = re.search(r'"shortDescription":"(.*?)"', response.text)
            description = desc_match.group(1) if desc_match else ''

            # Generate summary using AI
            prompt = f"""Based on a YouTube video titled "{title}" by "{channel_name}" with description:

{description[:1000]}

Generate a comprehensive summary as if you had watched this video. Include:
1. A concise summary (2-3 paragraphs)
2. Key points (as a JSON array of strings)
3. Study notes (as a formatted text)

Return as JSON with keys: summary, key_points, notes"""

            result = self.gemini._safe_generate(prompt)

            try:
                parsed = json.loads(re.search(r'\{[\s\S]*\}', result).group(0))
            except (json.JSONDecodeError, AttributeError):
                parsed = {
                    'summary': result,
                    'key_points': ['Content from video about ' + title],
                    'notes': result,
                }

            return {
                'video_id': video_id,
                'title': title,
                'channel_name': channel_name,
                'duration': 0,
                'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'transcript': description,
                'summary': parsed.get('summary', ''),
                'key_points': parsed.get('key_points', []),
                'notes': parsed.get('notes', ''),
                'quiz': [],
            }

        except Exception as e:
            return {'error': f'Error processing video: {str(e)}'}
