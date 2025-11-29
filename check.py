"""
Check what's in your .env file
"""

from pathlib import Path

env_file = Path(".env")

if env_file.exists():
    print("✅ .env file found")
    print("="*60)
    print("Contents:")
    print("="*60)
    
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)
    
    print("="*60)
    
    # Check for issues
    if "..." in content:
        print("❌ ERROR: Your .env file contains '...' (truncated API key!)")
        print("   You need to put the FULL API key, not abbreviated")
    elif len(content.strip()) < 10:
        print("❌ ERROR: .env file is too short or empty")
    else:
        # Extract key
        for line in content.split('\n'):
            if 'GEMINI_API_KEY' in line:
                key = line.split('=')[1].strip()
                print(f"API Key length: {len(key)} characters")
                if len(key) < 30:
                    print("❌ ERROR: API key is too short!")
                else:
                    print(f"✅ API key looks correct: {key[:10]}...{key[-5:]}")
else:
    print("❌ .env file not found!")
    print("Create it with:")
    print('echo "GEMINI_API_KEY=your-full-api-key-here" > .env')