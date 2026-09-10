# 🖼️ AI Image Analyzer

An AI-powered image analysis application built with Streamlit and Hugging Face Transformers. Upload an image and the application analyzes the entire visible scene and generates a natural-language description.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

## 📖 Overview

AI Image Analyzer uses a vision-language model to describe people, objects, backgrounds, environments, and other visible details in uploaded images. It turns any image into a rich, natural-language description — great for accessibility, content tagging, and visual understanding.

## ✨ Features

- 🖼️ Upload JPG, JPEG, PNG, and WebP images
- 🧑 Detect and describe visible people and their actions
- 📦 Identify important objects
- 🏞️ Analyze the background and surroundings
- 📍 Describe the position of objects
- 🌍 Identify the visible environment or setting
- 🎨 Describe important colors, shapes, materials, and lighting
- 🔍 Analyze the whole image, including edges and corners

## 🛠️ Tech Stack

- Frontend: Streamlit
- Model: Hugging Face Transformers (vision-language)
- Image Processing: Pillow
- Language: Python 3.10+

## 📂 Project Structure

    AI-Image-Recognizer/
    ├── app.py                # Streamlit app (main entry point)
    ├── requirements.txt      # Python dependencies
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

### 4. Set up your API key (optional)

If your implementation uses the Hugging Face Inference API, create a `.env` file:

    HUGGINGFACE_API_KEY=your_huggingface_api_key_here

Get your API key from https://huggingface.co/settings/tokens

## ▶️ Usage

Run the Streamlit app:

    streamlit run app.py

Then open your browser at http://localhost:8501

1. Upload an image (JPG, JPEG, PNG, or WebP)
2. Wait for the model to analyze the scene
3. Read the natural-language description of the image

## 🔒 Notes

- Never commit your `.env` file — it contains your API key
- Make sure `.env` is listed in `.gitignore`
- If you accidentally expose a key, revoke it immediately

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

- Hugging Face — https://huggingface.co
- Streamlit — https://streamlit.io
- Open-source contributors
