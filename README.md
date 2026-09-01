# Aurelia-chan — Executive Career Mentor & Life Strategist

A sophisticated interactive AI character featuring dynamic expression portraits, multi-language voice synthesis, resume auditing, interview simulation, and a complete 3D production pipeline for character model generation.

## 🌟 Features

### Web Application
- **Interactive Character Stage**: 11 dynamic expression portraits with smooth transitions
- **Mentor Chat Module**: AI-powered career guidance with contextual responses
- **Resume Audit Tool**: Executive-level resume analysis with scoring system
- **Interview Simulator**: Practice scenarios with real-time feedback
- **Multi-language Support**: English, Japanese, German, French, Spanish
- **Free Voice Synthesis**: Neural voice synthesis using Web Speech API
- **Professional Design**: Executive-inspired dark theme with gold accents

### 3D Production Pipeline
- **AI-Assisted 3D Generation**: Integration with Meshy and Tripo AI services
- **Reference Preparation**: Automated extraction from master character sheets
- **Canon Validation**: Two-layer quality assurance (mechanical + visual)
- **3D Model Viewer**: WebGL-based inspection tool with validation checklist
- **Material System**: Comprehensive PBR material specifications
- **Optimization**: Desktop and mobile optimization targets

## 📋 Prerequisites

### Required Software
- **Python 3.8+**: For pipeline scripts and voice generation
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge (for web app and viewer)
- **Blender** (optional): For advanced 3D model processing

### Required Python Packages
```bash
pip install requests Pillow edge-tts
```

### Optional (for 3D Pipeline)
- **Meshy API Key**: Sign up at https://www.meshy.ai/
- **Tripo API Key**: Sign up at https://developers.tripo3d.com/

## 🚀 Quick Start

### 1. Web Application
Simply open `index.html` in a modern web browser. No installation required!

```bash
# Option 1: Direct file open
open index.html

# Option 2: Local server (recommended for full functionality)
python -m http.server 8000
# Then visit http://localhost:8000
```

### 2. Voice Generation (Optional)
Generate offline voice files for Aurelia:

```bash
python generate_voice.py
```

This creates an `audio_pack/` directory with MP3 files in multiple languages.

### 3. 3D Pipeline (Requires API Keys)
#### Step 1: Configure API Keys
Edit `pipeline/config.json` and add your API keys:

```json
{
  "provider": {
    "meshy": {
      "api_key": "your_meshy_api_key_here"
    },
    "tripo": {
      "api_key": "your_tripo_api_key_here"
    }
  }
}
```

#### Step 2: Run Full Pipeline
```bash
python pipeline/run_pipeline.py
```

#### Step 3: Review Generated Model
Open `viewer/index.html` in a browser and load the generated GLB file.

## 📁 Project Structure

```
Aurelia-Chan/
├── index.html              # Main web application
├── app.js                  # Application logic (514 lines)
├── style.css               # Executive design system (756 lines)
├── generate_voice.py       # Voice generation script
├── README.md               # This file
│
├── aurelia-canon/          # Character specifications
│   ├── AURELIA_CHAN_IMMUTABLE_CHARACTER_BIBLE.md
│   └── master-sheets/      # 15 reference blueprints
│
├── aurelia-expressions/    # 11 expression portraits
│   ├── 01-neutral-observing.png
│   ├── 02-subtle-confident-smile.png
│   └── ... (9 more expressions)
│
├── pipeline/               # 3D production pipeline
│   ├── config.json         # Pipeline configuration
│   ├── run_pipeline.py     # Master orchestrator
│   ├── generate_3d.py      # AI generation coordinator
│   ├── prepare_references.py # Reference image processing
│   ├── providers/          # AI service integrations
│   │   ├── base.py         # Provider interface
│   │   ├── meshy.py        # Meshy implementation
│   │   └── tripo.py        # Tripo implementation
│   └── validation/         # Canon compliance checking
│       └── canon_checker.py
│
├── viewer/                 # 3D model viewer
│   ├── index.html
│   ├── viewer.css
│   └── viewer.js
│
└── assets/                 # Asset management
    ├── raw/                # Generated 3D models
    ├── approved/           # Approved models
    └── web/                # Web-optimized models
```

## 🎨 Character Canon

Aurelia-chan is an immutable character with strict design specifications:

- **Age**: 33 years (permanently fixed)
- **Height**: 170 cm / 5'7" (7.5-head proportion system)
- **Appearance**: Warm ivory skin, jet-black bob hair, sapphire eyes
- **Wardrobe**: Executive blazer, ivory blouse, charcoal trousers, heels
- **Accessories**: Gold stud earrings, pendant necklace, black-and-gold watch

All character assets must comply with the specifications in `aurelia-canon/AURELIA_CHAN_IMMUTABLE_CHARACTER_BIBLE.md`.

## 🔧 Configuration

### Pipeline Configuration
Edit `pipeline/config.json` to customize:

- **API Keys**: Add service credentials
- **Paths**: Configure asset directories
- **Canon Specifications**: Character measurements and colors
- **Materials**: PBR material properties
- **Optimization**: Polygon counts and texture resolutions
- **Blender Settings**: Scene units and scale

### Web Application Configuration
The web application uses client-side configuration in `app.js`:

- **Voice Settings**: Pitch, rate, and language preferences
- **Expression Mappings**: Text-to-expression associations
- **Translation Dictionary**: Multi-language support strings

## 📊 Usage Examples

### Running Specific Pipeline Steps

```bash
# Prepare reference images only
python pipeline/run_pipeline.py --step prepare

# Generate 3D model only
python pipeline/run_pipeline.py --step generate

# Validate existing model
python pipeline/run_pipeline.py --step validate

# Use specific provider
python pipeline/run_pipeline.py --provider tripo

# Skip generation (use existing GLB)
python pipeline/run_pipeline.py --skip-generate
```

### Voice Generation

```bash
# Generate all voice files
python generate_voice.py

# Output: audio_pack/
#   ├── welcome_en.mp3
#   ├── greeting_ja.mp3
#   ├── approval_en.mp3
#   └── warning_en.mp3
```

### Model Validation

```bash
# Validate specific model
python pipeline/validation/canon_checker.py assets/web/aurelia.glb

# Validate latest generated model
python pipeline/validation/canon_checker.py --latest
```

## 🎯 Web Application Modules

### Mentor Chat
- Interactive conversation with Aurelia-chan
- Context-aware expression changes
- Voice synthesis for responses
- Multi-language support

### Resume Audit
- Paste resume text for analysis
- Executive alignment scoring (0-100%)
- Strengths and improvement suggestions
- Professional feedback

### Interview Simulator
- Practice executive interview scenarios
- Real-time response evaluation
- Score-based feedback system
- Multiple scenario options

### Canon Specification
- View canonical color palette
- Access 15 master reference sheets
- Character specification documentation
- Quality assurance guidelines

## 🔍 3D Viewer Features

- **Model Loading**: Drag-and-drop or file selection
- **Orbit Controls**: Smooth camera navigation
- **Studio Lighting**: 3-point lighting setup
- **Wireframe Mode**: Toggle mesh visualization
- **Auto-Rotate**: Continuous model rotation
- **Screenshot Export**: Save model views
- **Real-time Stats**: Polygon count, materials, dimensions
- **Validation Interface**: Layer A mechanical QA display
- **Visual QA Checklist**: Interactive Layer B review
- **Environment Presets**: Studio, outdoor, warm, neutral

## 🐛 Troubleshooting

### Web Application Issues

**Voice not working:**
- Ensure browser supports Web Speech API
- Check voice toggle is enabled
- Verify language selection matches installed voices

**Expression portraits not loading:**
- Verify `aurelia-expressions/` directory exists
- Check image file permissions
- Ensure images are named correctly

**Chat responses not appearing:**
- Check browser console for JavaScript errors
- Verify `app.js` is loaded correctly
- Test with simple input first

### Pipeline Issues

**API key errors:**
- Verify API keys are correctly set in `pipeline/config.json`
- Check API key format (no extra spaces)
- Ensure API service account is active

**Reference image preparation fails:**
- Verify master sheets exist in `aurelia-canon/master-sheets/`
- Check Pillow installation: `pip install Pillow`
- Ensure sufficient disk space

**3D generation fails:**
- Check internet connection
- Verify API key has sufficient credits
- Try alternative provider (meshy/tripo)
- Check service status pages

**Model validation fails:**
- Ensure GLB file is valid format
- Check file size exceeds limits
- Verify model has required materials

### Python Script Issues

**Import errors:**
- Ensure all required packages are installed
- Check Python version (3.8+ required)
- Verify package names are correct

**File permission errors:**
- Run scripts with appropriate permissions
- Check directory write access
- Verify file paths are correct

**Network timeouts:**
- Check internet connection
- Increase timeout values in scripts
- Verify firewall settings

## 📈 Performance Optimization

### Web Application
- Lazy-load expression portraits
- Optimize image sizes (target < 2MB per portrait)
- Minimize JavaScript bundle size
- Use browser caching for static assets

### 3D Pipeline
- Use appropriate polygon counts (desktop: 80K, mobile: 40K)
- Optimize texture resolutions (desktop: 2048px, mobile: 1024px)
- Compress GLB files using glTF-Pipeline
- Enable Draco compression for web delivery

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **User Input**: Web app has basic input validation
- **File Uploads**: Viewer only accepts GLB/GLTF files
- **Network Traffic**: All API calls use HTTPS

## 🤝 Contributing

To contribute to Aurelia-chan:

1. Follow the character canon specifications strictly
2. Test changes across all supported browsers
3. Validate 3D models against canon requirements
4. Update documentation for any new features
5. Maintain code style consistency

## 📄 License

This project is proprietary. All character assets, specifications, and generated content are subject to copyright and intellectual property restrictions.

## 📞 Support

For issues or questions:
- Check this README first
- Review the character bible for canon questions
- Consult API documentation for service-specific issues
- Check browser console for web application errors

## 🎯 Roadmap

### Current Version: 1.0
- ✅ Web application with all modules
- ✅ Character canon and master sheets
- ✅ Expression portrait system
- ✅ 3D pipeline infrastructure
- ✅ Multi-language support
- ✅ Voice synthesis

### Planned Features
- [ ] Blender automation scripts
- [ ] Advanced material processing
- [ ] Animation system integration
- [ ] Mobile app version
- [ ] Additional language support
- [ ] Cloud deployment options

---

**Aurelia-chan Project Canon v1.0 — Immutable Master Authority**