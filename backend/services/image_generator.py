import os
from huggingface_hub import InferenceClient
from PIL import Image
import io
import base64

HF_CLIENT = InferenceClient(token=os.getenv("HF_TOKEN"))

def generate_image_base64(prompt: str, style: str = "cartoon") -> str:
    full_prompt = f"{prompt}, {style} style, bright colors, clean background, 16:9 aspect ratio"
    try:
        image = HF_CLIENT.text_to_image(
            prompt=full_prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            parameters={"num_inference_steps": 25}
        )
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # Заглушка: 1x1 прозрачный PNG в base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="