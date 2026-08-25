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
# MODEL CONFIGURATION
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
    "Upload an image and AI will describe the complete visible scene."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("ℹ️ About")

    st.write(
        "This application uses "
        "SmolVLM-256M-Instruct to analyze uploaded images."
    )

    st.write(
        "It looks for people, objects, background, "
        "positions, environment, colors, and other "
        "clearly visible details."
    )

    st.divider()

    st.caption(
        "Model: SmolVLM-256M-Instruct"
    )

    st.caption(
        "Built with Streamlit + Hugging Face Transformers"
    )


# ============================================================
# IMAGE UPLOAD
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
# IMAGE PROCESSING
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


    st.write("")


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
                # IMAGE ANALYSIS PROMPT
                # ====================================================

                prompt = """
Look carefully at the ENTIRE image before answering.

Describe what is actually visible in the scene.

Write ONE clear natural description, not a numbered list.

Make sure to cover:

- People: mention every clearly visible person and what they are doing.
- Main objects: identify the important objects.
- Background: describe objects and scenery behind the main subjects.
- Position: explain important left, right, center, foreground, and background positions.
- Environment: identify the visible setting or surroundings.
- Visual details: mention important colors, shapes, materials, lighting, and other visible details.

Look at the edges and corners of the image as well as the center.

IMPORTANT:
Do not repeat information.
Do not repeat sentences.
Do not create numbered items.
Do not copy or repeat these instructions.
Do not invent objects, people, actions, locations, or details.
Only describe things that can actually be seen.
If there are no people, simply state that no people are visible.
If something is unclear, say that it is unclear.
Keep the final description concise but complete.
"""


                # ====================================================
                # CHAT MESSAGE
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
                # CREATE CHAT TEMPLATE
                # ====================================================

                text = processor.apply_chat_template(
                    messages,
                    add_generation_prompt=True
                )


                # ====================================================
                # PROCESS IMAGE + TEXT
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
                # GENERATE DESCRIPTION
                # ====================================================

                with torch.inference_mode():

                    output_ids = model.generate(
                        **inputs,
                        max_new_tokens=180,
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
                # DECODE RESPONSE
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
                        "The model returned an empty description."
                    )

                else:

                    # Remove accidental repeated paragraphs
                    lines = answer.splitlines()

                    cleaned_lines = []

                    previous_line = ""

                    for line in lines:

                        line = line.strip()

                        if not line:
                            continue

                        if line.lower() == previous_line.lower():
                            continue

                        cleaned_lines.append(line)

                        previous_line = line


                    answer = " ".join(
                        cleaned_lines
                    )


                    # ====================================================
                    # DISPLAY RESULT
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
