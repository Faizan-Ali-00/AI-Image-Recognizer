🖼️ AI Image Analyzer
An AI-powered image analysis application built with Streamlit and Hugging Face Transformers. Upload an image and the application analyzes the entire visible scene and generates a natural-language description.
✨ Features
- 🖼️ Upload JPG, JPEG, PNG, and WebP images
- 👤 Detect and describe visible people and their actions
- 📦 Identify important objects
- 🌄 Analyze the background and surroundings
- 📍 Describe the position of objects
- 🏠 Identify the visible environment or setting
- 🎨 Describe important colors, shapes, materials, and lighting
- 🔍 Analyze the whole image, including edges and corners
- 🚫 Instructs the model not to invent details
- ♻️ Includes repetition controls to reduce repeated responses
- ⚡ Resizes large images for faster processing
- 🌐 Can be deployed with Streamlit Community Cloud
🤖 AI Model
This project uses:
HuggingFaceTB/SmolVLM-256M-Instruct
The model is a lightweight vision-language model designed to understand images and generate text descriptions.
🛠️ Technologies
- Python
- Streamlit
- PyTorch
- Hugging Face Transformers
- SmolVLM
- Pillow
- Torchvision
- Accelerate
📁 Project Structure
AI_Image_Recognizer/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
⚙️ Installation
Clone the repository:
git clone https://github.com/Faizan-Ali-00/AI-Image-Recognizer.git
Enter the project directory:
cd AI-Image-Recognizer
Create a virtual environment:
python -m venv venv
Activate it on Windows:
venv\Scripts\activate
Install the dependencies:
pip install -r requirements.txt
▶️ Run the Application
Start Streamlit:
streamlit run app.py
The application will open in your browser.
Upload an image and click:
🔍 Analyze Image
🚀 Deployment
The application can be deployed using Streamlit Community Cloud.
Use:
- Repository: Faizan-Ali-00/AI-Image-Recognizer
- Branch: main
- Main file: app.py
Streamlit will install the dependencies listed in requirements.txt.
⚠️ Limitations
This project uses a 256M-parameter vision-language model, so it is intentionally lightweight. It can provide useful basic image descriptions, but it will not have the scene-understanding accuracy of much larger vision models.
Performance also depends heavily on the computer's CPU/GPU and available memory.
The model may occasionally:
- Miss small objects
- Misinterpret complex scenes
- Miss background details
- Produce inaccurate descriptions
- Repeat information in difficult images
The application therefore instructs the model to describe only visibly supported information and avoid guessing.
🔮 Future Improvements
Possible future improvements include:
- Better vision models
- Object detection
- Face/person detection
- OCR for reading text in images
- Image question answering
- Multiple image support
- Image comparison
- Automatic scene classification
- GPU acceleration
- More detailed background analysis
👨‍💻 Author
Faizan Ali
GitHub: Faizan-Ali-00
📄 License
This project can be released under the MIT License.
