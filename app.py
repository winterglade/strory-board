import streamlit as st
import json
import os
from groq import Groq
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw 
import io
from dotenv import load_dotenv

# === Загрузка ключей ===
load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not GROQ_KEY or not HF_TOKEN:
    st.error("⚠️ Не найдены API-ключи! Проверьте .env файл.")
    st.stop()

# === Инициализация клиентов ===
groq_client = Groq(api_key=GROQ_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# === Промпт для LLM (строгий JSON) ===
SCRIPT_PROMPT = """You are a professional short-video scriptwriter.
Create a 30-second video script for: "{idea}".
Tone: {tone}.
Output ONLY valid JSON — no markdown, no extra text — with this structure:
{{
  "title": "string",
  "scenes": [
    {{
      "scene_num": 1,
      "visual_description": "detailed visual: characters, setting, action, mood",
      "voiceover": "short narrator line",
      "dialogue": "character line or ''"
    }}
  ]
}}
Use exactly 5 scenes. Be vivid and specific."""

def generate_script(idea: str, tone: str) -> dict:
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Быстрый и точный
            messages=[{"role": "user", "content": SCRIPT_PROMPT.format(idea=idea, tone=tone)}],
            temperature=0.7,
            max_tokens=1000
        )
        text = resp.choices[0].message.content.strip()
        # Очистка от ```json ... ```
        if text.startswith("```"):
            text = text.split("```json")[-1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"❌ Ошибка LLM: {str(e)[:200]}")
        # Fallback — минимальный JSON для продолжения
        return {
            "title": "Ошибка генерации",
            "scenes": [
                {"scene_num": i, "visual_description": "a placeholder scene", "voiceover": "", "dialogue": ""}
                for i in range(1, 6)
            ]
        }

def generate_image(prompt: str, style: str = "cartoon") -> Image.Image:
    """Возвращает PIL Image — совместимо с новыми и старыми версиями huggingface-hub"""
    full_prompt = f"{prompt}, {style} style, bright colors, clean background, 16:9 aspect ratio, high quality"
    try:
        # text_to_image в новых версиях возвращает PIL Image напрямую
        image = hf_client.text_to_image(
            prompt=full_prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0"
        )
        # Если вдруг вернуло bytes (старая версия) — конвертируем
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        return image
    except Exception as e:
        st.warning(f"🖼️ Изображение не сгенерировано ({str(e)[:100]}). Используем заглушку.")
        # Заглушка: цветной прямоугольник
        img = Image.new("RGB", (600, 340), color=(220, 240, 255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 160), "🖼️ Image placeholder", fill="black", font=draw._font)
        return img

# === Streamlit UI ===
st.set_page_config(page_title="📽️ StoryboardGen (FREE)", layout="wide")
st.title("📽️ StoryboardGen — 100% бесплатно")
st.caption("Groq (LLM) + Hugging Face (SDXL) | Без оплаты и карт")

# Ввод
col1, col2 = st.columns([3, 1])
with col1:
    idea = st.text_input("💡 Идея видео", "Спа-массаж для домашних котов")
with col2:
    tone = st.selectbox("🎭 Тон", ["юмористический", "трогательный", "образовательный", "динамичный"])

# Генерация
if st.button("🚀 Сгенерировать (бесплатно!)"):
    with st.spinner("Пишем сценарий через Groq..."):
        script = generate_script(idea, tone)
    st.session_state.script = script
    st.session_state.images = []

# Вывод
if "script" in st.session_state:
    st.subheader(f"📜 {st.session_state.script.get('title', 'Сценарий')}")
    scenes = st.session_state.script["scenes"]

    # Генерация изображений (если ещё не сделано)
    if "images" not in st.session_state or len(st.session_state.images) != len(scenes):
        with st.spinner("Рисуем раскадровку через Hugging Face (SDXL)..."):
            images = []
            for scene in scenes:
                img = generate_image(scene["visual_description"], tone)
                images.append(img)
            st.session_state.images = images

    # Отображение
    for i, (scene, img) in enumerate(zip(scenes, st.session_state.images)):
        with st.expander(f"Сцена {scene['scene_num']}", expanded=True):
            col_img, col_txt = st.columns([2, 3])
            with col_img:
                st.image(img, use_container_width=True)
                if st.button(f"🔄 Перегенерировать", key=f"regen_{i}"):
                    with st.spinner(f"Сцена {i+1}..."):
                        new_img = generate_image(scene["visual_description"], tone)
                        st.session_state.images[i] = new_img
                        st.rerun()
            with col_txt:
                st.markdown(f"**Voiceover:** {scene.get('voiceover', '')}")
                if scene.get("dialogue"):
                    st.markdown(f"**Диалог:** _{scene['dialogue']}_")
                st.caption(scene["visual_description"])

st.divider()
st.caption("ℹ️ Первый запуск может занять 20–40 сек (Hugging Face inference queue). Демо-видео — наша страховка!")