# 🧙 PixelSage

A professional AI-powered image analyzer that describes every detail of your photo — from foreground to background — in one clean, natural paragraph.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 📖 Overview

PixelSage uses a powerful vision-language model to understand and describe uploaded images in natural language. It reads the entire scene — foreground, middle ground, background, edges and corners — and returns a single, flowing description that reads like a human expert looking at your photo.

Perfect for accessibility, content tagging, visual understanding, and learning what's really inside an image.

## ✨ Features

- 📸 Upload JPG, JPEG, PNG, and WebP images
- 🧙 Clean, product-grade UI with animated logo
- 🧠 AI-powered descriptions (Groq + Qwen 3.6)
- 🎚️ Three detail levels: Brief · Standard · Detailed
- 📝 Natural one-paragraph output (no reasoning leaks)
- 📚 History panel — auto-saves last 30 analyses with thumbnails
- ⚙️ Settings panel — adjustable detail level, temperature, and token limit
- 💾 Persistent settings and history (JSON-backed)
- 🎨 Beautiful gradient theme with sidebar
- 📋 Copy output as plain text

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI Model:** Qwen 3.6 (via Groq API)
- **Image Processing:** Pillow
- **Language:** Python 3.10+
- **Storage:** Local JSON files (`history.json`, `settings.json`)

## 📂 Project Structure

    AI-Image-Recognizer/
    ├── app.py                # Streamlit app (main entry point)
    ├── requirements.txt      # Python dependencies
    ├── history.json          # Auto-generated — saved analyses
    ├── settings.json         # Auto-generated — saved preferences
    ├── thumbnails/           # Auto-generated — thumbnails for history
    ├── .gitignore            # Git ignore rules
    └── README.md

## ⚙️ Installation

### 1. Clone the repository

    git clone https://github.com/Faizan-Ali-00/AI-Image-Recognizer.git
    cd AI-Image-Recognizer

### 2. Create a virtual environment

    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Set up your Groq API key

Create a `.env` file in the root directory:

    GROQ_API_KEY=gsk_your_groq_api_key_here

Get your free API key from https://console.groq.com/keys

## ▶️ Usage

Run the Streamlit app:

    streamlit run app.py

Then open your browser at http://localhost:8501

1. Upload an image (JPG, JPEG, PNG, or WebP)
2. Choose a detail level (Brief / Standard / Detailed)
3. Click **Analyze Image**
4. Read the natural-language description
5. Every analysis is auto-saved to the History panel

## 🎛️ Settings

Open the **⚙️ Settings** tab in the sidebar to configure:

| Setting | Description | Default |
|---------|-------------|---------|
| **Detail Level** | Length and depth of the description | Standard |
| **Temperature** | Creativity (0.0 – 1.0) | 0.4 |
| **Max Tokens** | Maximum response length | 900 |

Click **💾 Save Settings** to persist them. Click **↺ Reset to Defaults** to restore original values.

## 📚 History

Every analysis is automatically saved in the **📚 History** tab (up to the last 30). Each entry includes:

- 🕐 Timestamp
- 🖼️ Thumbnail of the analyzed image
- 📝 Full description
- ⚙️ Detail level used

You can **View**, **Delete** individual entries, or **Clear All** at once.

## 🔒 Notes

- Never commit your `.env` file — it contains your API key
- Make sure `.env` is listed in `.gitignore`
- If you accidentally expose a key, revoke it immediately at https://console.groq.com/keys
- On Streamlit Cloud, `history.json` and `thumbnails/` are wiped when the app reboots

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m "Add some AmazingFeature"`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

Faizan Ali

- GitHub: https://github.com/Faizan-Ali-00
- Repository: https://github.com/Faizan-Ali-00/AI-Image-Recognizer

## ⭐ Show Your Support

If this project helped you, please give it a star on GitHub.

## 🙏 Acknowledgments

- Groq — https://groq.com
- Qwen — https://qwenlm.github.io
- Streamlit — https://streamlit.io
- Open-source contributors
