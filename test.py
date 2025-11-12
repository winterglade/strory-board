import openai

GEMINI_KEY = "AIzaSyBdUY3grbKBAdgBu6f92cY39vPwgruzCGs"
PROXY_URL = "https://gentle-night-1af3.ai-proxy-danil.workers.dev"  # ← уберите пробелы в конце!

client = openai.OpenAI(
    api_key=GEMINI_KEY,
    base_url=f"{PROXY_URL}/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash-thinking-exp",  # ✅ работает, мощная, 1500/день
    # ИЛИ:
    # model="gemini-1.5-flash",               # ✅ быстрее, 1500/день
    messages=[{
        "role": "user",
        "content": """Create a 30-second video script for: 'Студент находит котёнка'.
Tone: добрый.
Output ONLY valid JSON with this structure:
{
  "title": "string",
  "scenes": [
    {
      "scene_num": 1,
      "visual_description": "detailed visual",
      "voiceover": "short line",
      "dialogue": "line or empty string"
    }
  ]
}
Use exactly 5 scenes. No extra text."""
    }],
    response_format={"type": "json_object"},  # ✅ поддерживается
    temperature=0.7,
    max_tokens=1200
)

print(response.choices[0].message.content)