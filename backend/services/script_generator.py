import os
from groq import Groq
from ..schemas import ScriptResponse
import json
import logging

logger = logging.getLogger(__name__)

GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

SCRIPT_PROMPT = """You are a professional short-video scriptwriter.
Create a 30-second video script for: '{idea}'.
Tone: {tone}.
Output ONLY a valid JSON object — no text before or after.
Use this exact structure:
{{
  "title": "string",
  "scenes": [
    {{
      "scene_num": 1,
      "visual_description": "vivid visual details",
      "voiceover": "short line",
      "dialogue": "line or empty string"
    }}
  ]
}}
Use exactly 5 scenes. Be specific. Do not add explanations."""

def generate_script(idea: str, tone: str) -> ScriptResponse:
    try:
        # Экранируем кавычки в идеях
        safe_idea = idea.replace('"', "'").replace('\n', ' ')
        safe_tone = tone.replace('"', "'").replace('\n', ' ')

        completion = GROQ_CLIENT.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": SCRIPT_PROMPT.format(idea=safe_idea, tone=safe_tone)
            }],
            temperature=0.7,
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        
        raw = completion.choices[0].message.content.strip()
        
        # 🔑 Надёжная очистка JSON
        # Удаляем всё до первой { и после последней }
        start = raw.find('{')
        end = raw.rfind('}')
        if start == -1 or end == -1:
            raise ValueError(f"No JSON braces found in LLM output: {raw[:100]}...")
        clean_json = raw[start:end+1]
        
        data = json.loads(clean_json)
        return ScriptResponse(**data)
    
    except Exception as e:
        logger.error(f"Script generation failed: {e} | Raw LLM output: {raw if 'raw' in locals() else 'N/A'}")
        # Fallback с диагностикой
        return ScriptResponse(
            title=f"⚠️ Ошибка: {str(e)[:50]}",
            scenes=[
                {"scene_num": i, "visual_description": f"DEBUG: idea='{idea}', tone='{tone}'", "voiceover": "", "dialogue": ""}
                for i in range(1, 6)
            ]
        )