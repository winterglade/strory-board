from pydantic import BaseModel
from typing import List

class Scene(BaseModel):
    scene_num: int
    visual_description: str
    voiceover: str
    dialogue: str = ""

class ScriptResponse(BaseModel):
    title: str
    scenes: List[Scene]