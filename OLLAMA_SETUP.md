# Ollama Installation Guide for Aurelia-chan

## What is Ollama?
Ollama is a tool that lets you run large language models (like Llama 3, Mistral) locally on your computer. It works offline and provides a simple API for your applications.

## Installation Steps

### Windows Installation

1. **Download Ollama for Windows**
   - Go to: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer (ollama-setup.exe)

2. **Verify Installation**
   - Open Command Prompt or PowerShell
   - Run: `ollama --version`
   - You should see version information

3. **Start Ollama Server**
   - Run: `ollama serve`
   - This starts the API server on http://localhost:11434
   - Keep this terminal window open

4. **Pull a Model** (in a new terminal window)
   ```bash
   # Pull Llama 3.2 (recommended - fast and capable)
   ollama pull llama3.2

   # Or pull Mistral (alternative)
   ollama pull mistral

   # Or pull Llama 3.2 Nano (for older computers)
   ollama pull llama3.2:3b
   ```

5. **Test the Model**
   ```bash
   ollama run llama3.2 "Hello, how are you?"
   ```

## Testing Ollama API

### Test with curl (Command Prompt)
```bash
curl http://localhost:11434/api/generate -d "{
  \"model\": \"llama3.2\",
  \"prompt\": \"Hello, how are you?\",
  \"stream\": false
}"
```

### Test with Python
```python
import requests
import json

response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama3.2',
    'prompt': 'Hello, how are you?',
    'stream': False
})

print(response.json()['response'])
```

## Recommended Models for Aurelia-chan

### Llama 3.2 (Recommended)
- **Size**: ~4GB
- **Speed**: Fast
- **Quality**: Excellent
- **Best for**: General conversation, reasoning
- **Command**: `ollama pull llama3.2`

### Llama 3.2 Nano (For older computers)
- **Size**: ~2GB
- **Speed**: Very fast
- **Quality**: Good
- **Best for**: Older computers with limited RAM
- **Command**: `ollama pull llama3.2:3b`

### Mistral
- **Size**: ~4GB
- **Speed**: Fast
- **Quality**: Excellent
- **Best for**: Creative writing, complex reasoning
- **Command**: `ollama pull mistral`

## Troubleshooting

### "ollama command not found"
- Make sure you installed Ollama
- Restart your terminal/command prompt
- Check if Ollama is in your PATH

### "Connection refused" error
- Make sure `ollama serve` is running
- Check if port 11434 is available
- Try restarting the Ollama server

### "Out of memory" error
- Use a smaller model (llama3.2:3b)
- Close other applications
- Restart your computer

### Slow responses
- Use a smaller model
- Check your RAM (8GB+ recommended)
- Close other applications

## Next Steps After Installation

1. ✅ Install Ollama
2. ✅ Pull a model (llama3.2 recommended)
3. ✅ Test the API
4. ✅ Run the test script provided (test_ollama.py)
5. ✅ Integrate with Aurelia-chan chat system

## System Requirements

### Minimum
- Windows 10 or later
- 8GB RAM
- 10GB free disk space
- Modern CPU

### Recommended
- Windows 10 or later
- 16GB RAM
- 20GB free disk space
- Modern CPU with AVX2 support
- GPU (optional, for faster inference)