"""
Check actual .env file content byte by byte
"""

from pathlib import Path

env_file = Path(".env")

print("="*60)
print("RAW .ENV FILE ANALYSIS")
print("="*60)

with open(env_file, 'rb') as f:
    raw_bytes = f.read()
    
print(f"File size: {len(raw_bytes)} bytes")
print(f"\nRaw bytes (hex):")
print(raw_bytes.hex())

print(f"\nDecoded as text:")
text = raw_bytes.decode('utf-8')
print(repr(text))

print(f"\nLines:")
for i, line in enumerate(text.split('\n'), 1):
    print(f"  Line {i}: {repr(line)}")
    if 'GEMINI_API_KEY' in line:
        if '=' in line:
            key = line.split('=', 1)[1].strip()
            print(f"    -> Key extracted: '{key}'")
            print(f"    -> Key length: {len(key)}")
            print(f"    -> Contains '...': {'...' in key}")

print("="*60)

# Now test with dotenv
print("\nTesting with python-dotenv:")
from dotenv import load_dotenv
import os

# Clear any existing value
if 'GEMINI_API_KEY' in os.environ:
    del os.environ['GEMINI_API_KEY']

load_dotenv(dotenv_path=env_file)
loaded_key = os.getenv('GEMINI_API_KEY')

print(f"Loaded key: {repr(loaded_key)}")
print(f"Length: {len(loaded_key) if loaded_key else 0}")
print(f"Contains '...': {'...' in loaded_key if loaded_key else 'N/A'}")

print("="*60)