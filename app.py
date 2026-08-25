import streamlit as st
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Image Analyzer",
    page_icon="🖼️",
    layout="centered"
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "HuggingFaceTB/SmolVLM-256M-Instruct"


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    processor = AutoProcessor.from_pretrained(
        MODEL_NAME
    )

    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32
    )

    model.eval()

    return model, processor


# ============================================================
# HEADER
# ============================================================

st.title("🖼️ AI Image Analyzer")

st.caption(
    "Upload an image and AI will analyze the complete visible scene."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("ℹ️ About This App")

    st.write(
        "AI Image Analyzer uses a lightweight vision-language "
        "model to understand uploaded images."
    )

    st.write(
        "The analyzer looks at:"
    )

    st.markdown(
        """
        - 👤 People
        - 📦 Main objects
        - 🌄 Background
        - 📍 Object positions
        - 🏞️ Environment
        - 🎨 Colors
        - 💡 Lighting
        - 🔎 Small visible details
        """
    )

    st.divider()

    st.caption(
        "Model: SmolVLM-256M-Instruct"
    )

    st.caption(
        "Built with Streamlit and Hugging Face Transformers"
    )


# ============================================================
# UPLOAD IMAGE
# ============================================================

uploaded_file = st.file_uploader(
    "Upload an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)


# ============================================================
# IMAGE
# ============================================================

if uploaded_file:

    try:

        image = Image.open(
            uploaded_file
        ).convert("RGB")

    except Exception:

        st.error(
            "The uploaded file is not a valid image."
        )

        st.stop()


    # --------------------------------------------------------
    # Resize large images
    # --------------------------------------------------------

    image.thumbnail(
        (768, 768)
    )


    # --------------------------------------------------------
    # Display image
    # --------------------------------------------------------

    st.image(
        image,
        caption="Uploaded Image",
        width="stretch"
    )


    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    if st.button(
        "🔍 Analyze Image",
        width="stretch"
    ):

        with st.spinner(
            "AI is analyzing the entire image..."
        ):

            try:

                # ====================================================
                # LOAD MODEL
                # ====================================================

                model, processor = load_model()


                # ====================================================
                # PROMPT
                # ====================================================

                prompt = """
Analyze the ENTIRE image carefully before answering.

Do not focus only on the largest object.

Inspect the image in this order:

1. FOREGROUND
Look at the objects closest to the viewer.

2. MIDDLE GROUND
Look for objects between the foreground and background.

3. BACKGROUND
Carefully inspect everything behind the main objects.

4. EDGES AND CORNERS
Check the left edge, right edge, top edge, bottom edge,
and all four corners for additional objects or scenery.

5. PEOPLE
Identify every clearly visible person and describe what
they are doing.

6. ENVIRONMENT
Describe the location, surroundings, sky, ground,
buildings, landscape, weather, and atmosphere.

7. VISUAL DETAILS
Mention important colors, shapes, materials, lighting,
textures, signs, flags, vehicles, furniture, animals,
or other clearly visible objects.

8. POSITION
Explain where important objects are located using
terms such as left, right, center, foreground,
middle ground, and background.

Write ONE natural description of approximately
80 to 150 words.

IMPORTANT RULES:

- Describe only things actually visible.
- Do not guess.
- Do not invent people or objects.
- Do not repeat information.
- Do not repeat sentences.
- Do not create 20, 50, or 100 numbered observations.
- Do not copy the instructions.
- Do not stop after describing only the main object.
- Include the background if it is visible.
- If there are no people, say that no people are clearly visible.
- If a detail is uncertain, do not present it as a fact.
- Give one coherent description.
"""


                # ====================================================
                # MESSAGE
                # ====================================================

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image"
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]


                # ====================================================
                # CHAT TEMPLATE
                # ====================================================

                text = processor.apply_chat_template(
                    messages,
                    add_generation_prompt=True
                )


                # ====================================================
                # PROCESS IMAGE
                # ====================================================

                inputs = processor(
                    text=text,
                    images=[image],
                    return_tensors="pt"
                )


                # ====================================================
                # MOVE INPUTS TO MODEL
                # ====================================================

                inputs = {
                    key: value.to(model.device)
                    if hasattr(value, "to")
                    else value
                    for key, value in inputs.items()
                }


                # ====================================================
                # GENERATE
                # ====================================================

                with torch.inference_mode():

                    output_ids = model.generate(
                        **inputs,
                        max_new_tokens=250,
                        do_sample=False,
                        repetition_penalty=1.15,
                        no_repeat_ngram_size=4
                    )


                # ====================================================
                # REMOVE INPUT TOKENS
                # ====================================================

                input_length = (
                    inputs["input_ids"].shape[-1]
                )

                generated_ids = output_ids[
                    :,
                    input_length:
                ]


                # ====================================================
                # DECODE
                # ====================================================

                answer = processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )[0].strip()


                # ====================================================
                # CLEAN RESPONSE
                # ====================================================

                if not answer:

                    st.warning(
                        "The model returned no description."
                    )

                else:

                    # ------------------------------------------------
                    # Remove duplicate lines
                    # ------------------------------------------------

                    lines = answer.splitlines()

                    cleaned_lines = []

                    seen_lines = set()

                    for line in lines:

                        line = line.strip()

                        if not line:
                            continue

                        normalized = line.lower()

                        if normalized in seen_lines:
                            continue

                        seen_lines.add(
                            normalized
                        )

                        cleaned_lines.append(
                            line
                        )


                    answer = " ".join(
                        cleaned_lines
                    )


                    # ------------------------------------------------
                    # Remove excessive repeated sentences
                    # ------------------------------------------------

                    sentences = answer.split(". ")

                    final_sentences = []

                    seen_sentences = set()

                    for sentence in sentences:

                        sentence = sentence.strip()

                        if not sentence:
                            continue

                        normalized = (
                            sentence
                            .lower()
                            .replace(".", "")
                        )

                        if normalized in seen_sentences:
                            continue

                        seen_sentences.add(
                            normalized
                        )

                        final_sentences.append(
                            sentence
                        )


                    answer = ". ".join(
                        final_sentences
                    )


                    if answer and not answer.endswith("."):
                        answer += "."


                    # ====================================================
                    # RESULT
                    # ====================================================

                    st.subheader(
                        "🧠 AI Description"
                    )

                    st.write(
                        answer
                    )


            except Exception as e:

                st.error(
                    "The AI could not analyze the image."
                )

                st.code(
                    str(e)
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Image Analyzer • SmolVLM-256M-Instruct"
)
