import os
import time
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_family_filename(famille_id: int, original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"famille_{famille_id}_{int(time.time())}{ext}"
    return unique_name

