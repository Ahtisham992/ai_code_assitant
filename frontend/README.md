# AI Code Assistant - Web Interface

Professional web-based frontend for the Hybrid AI Code Assistant.

## Features

✅ **Model Loading Status** - Real-time status indicator  
✅ **5 AI Features** - Explain, Document, Fix, Optimize, Test  
✅ **Modern UI** - Professional gradient design  
✅ **Responsive** - Works on all screen sizes  
✅ **Real-time Processing** - Instant feedback  

## Setup

### 1. Install Flask

```bash
pip install flask
```

### 2. Set Environment Variable (if using Gemini)

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Run the Server

```bash
cd frontend
python app.py
```

### 4. Open Browser

Navigate to: **http://localhost:5000**

## Usage

1. **Wait for Model Loading** - Status bar will show "Model loaded successfully"
2. **Paste Your Code** - Enter Python function/class/method in the input area
3. **Select Feature** - Click one of the 5 buttons:
   - 💡 **Explain** - Get code explanation (Hybrid: Fine-tuned + Gemini)
   - 📚 **Document** - Generate documentation (Hybrid: Fine-tuned + Gemini)
   - 🔧 **Fix Bugs** - Detect and fix bugs (Gemini)
   - ⚡ **Optimize** - Optimize for performance (Gemini)
   - 🧪 **Generate Tests** - Create pytest tests (Gemini)
4. **View Results** - Output appears in the right panel

## Architecture

```
Frontend (Browser)
    ↓ HTTP Request
Flask Server (app.py)
    ↓ Python API
Hybrid AI System
    ├─ Fine-tuned CodeT5 (Explain & Document)
    └─ Gemini AI (Fix, Optimize, Test)
```

## Features Showcase

### Explain Code
- **Base Analysis** from fine-tuned model
- **Enhanced Analysis** with complexity details from Gemini
- Concise 2-5 line output

### Generate Documentation
- **Base Documentation** from fine-tuned model
- **Enhanced Docstring** with Args/Returns from Gemini
- Professional 5-8 line format

### Fix Bugs
- Detects logic errors
- Returns corrected code
- Powered by Gemini AI

### Optimize Code
- Improves time/space complexity
- Cleaner, more efficient code
- Powered by Gemini AI

### Generate Tests
- Comprehensive pytest suite
- Normal, edge, and error cases
- Powered by Gemini AI

## Troubleshooting

### Model Loading Fails
- Check if `./models/finetuned_model` exists
- Ensure all dependencies are installed

### Gemini Not Available
- Set `GEMINI_API_KEY` environment variable
- Get free key at: https://aistudio.google.com/app/apikey
- Install: `pip install -U google-genai`

### Port Already in Use
- Change port in `app.py`: `app.run(port=5001)`

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Models**: 
  - Fine-tuned CodeT5 (60M params)
  - Google Gemini 2.0 Flash
- **Design**: Modern gradient UI with responsive layout

## Project Structure

```
frontend/
├── app.py              # Flask backend
├── templates/
│   └── index.html      # Web interface
└── README.md           # This file
```

## Performance

- **Model Load Time**: 5-10 seconds
- **Explain/Document**: 2-3 seconds (Hybrid)
- **Fix/Optimize/Test**: 1-2 seconds (Gemini)

## Credits

**Semester 7 GenAI Project**  
Hybrid AI Code Assistant with Fine-tuned Model + Gemini Integration
