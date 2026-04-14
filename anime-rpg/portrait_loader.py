# portrait_loader.py — compatibility shim, delegates to sprite_loader
from sprite_loader import get_speaker_portrait, get_entity_portrait, get_portrait
SPEAKER_MAP = {"Elder Mira": "elder_mira", "Blacksmith": "blacksmith", "Kairu": "kairu"}
ENTITY_MAP  = {"Kairu": "kairu", "Shadow Lurker": "shadow_lurker"}
