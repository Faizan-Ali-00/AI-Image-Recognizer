import streamlit as st
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="AI Image Analyzer",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ AI Image Analyzer")

st.write(
    "Upload an image and let AI describe what is happening in it."
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "HuggingFaceTB/SmolVLM-256M-Instruct"


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
# IMAGE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)


# ============================================================
# ANALYZE
# ============================================================

if uploaded_file:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    st.image(
        image,
        caption="Uploaded Image",
        width="stretch"
    )
    image.thumbnail((768, 768))

    if st.button(
        "🔍 Analyze Image",
        width="stretch"
    ):

        with st.spinner(
            "AI is analyzing the image..."
        ):

            try:

                model, processor = load_model()


                # ====================================================
                # PROMPT
                # ====================================================

                prompt = """
Analyze the entire image from top to bottom and left to right.

Give me a complete description of everything that can be clearly seen.

Your response MUST contain these sections:

1. PEOPLE
Describe every visible person and what they are doing.
If there are no people, say "No people visible."

2. MAIN OBJECTS
Describe every important object in the foreground and middle of the image.

3. BACKGROUND
Carefully describe what is behind the main objects.
Include furniture, walls, doors, windows, shelves, buildings,
trees, vehicles, screens, decorations, or other visible objects.

4. POSITION
Explain where important objects are located:
left, right, center, front, behind, above, below, etc.

5. ENVIRONMENT
Describe the overall setting, such as a room, office, street,
kitchen, bedroom, outdoor area, or other clearly visible location.

6. DETAILS
Mention colors, shapes, materials, lighting, and other clearly
visible details.

IMPORTANT RULES:
- Examine the WHOLE image, not only the main objects.
- Look at the background before answering.
- Do not ignore objects near the edges of the image.
- Do not repeat these instructions.
- Do not invent anything that cannot be seen.
- If something is unclear, say that it is unclear.
- If a section has nothing visible, explicitly say so.
- Write a natural, detailed description.
"""

                # ====================================================
                # INPUT
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
                # APPLY CHAT TEMPLATE
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
                        max_new_tokens=7000,
                        do_sample=False
                    )


                # ====================================================
                # REMOVE INPUT TOKENS
                # ====================================================

                input_length = (
                    inputs["input_ids"].shape[1]
                )

                generated_ids = output_ids[
                    :, input_length:
                ]


                # ====================================================
                # DECODE
                # ====================================================

                answer = processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )[0].strip()


                # ====================================================
                # DISPLAY
                # ====================================================

                st.subheader(
                    "🧠 AI Description"
                )

                if answer:

                    st.write(answer)

                else:

                    st.warning(
                        "The model returned an empty description."
                    )


            except Exception as e:

                st.error(
                    "The AI could not analyze the image."
                )

                st.code(
                    str(e)
                )