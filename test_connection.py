from core.engine import get_cad_code
import os
from dotenv import load_dotenv

load_dotenv()
print(f"HF_TOKEN found: {os.getenv('HF_TOKEN')[:5]}...") # Security check

print("Testing Hugging Face connection...")
try:
    code = get_cad_code("Create a 10x10x10 cube")
    print("--- AI Response Received ---")
    print(code)
    print("----------------------------")
except Exception as e:
    print(f"Connection failed: {e}")