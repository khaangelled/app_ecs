import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def resize_and_crop(image, size=1600):
    ratio = max(size / image.width, size / image.height)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    left = (new_width - size) // 2
    top = (new_height - size) // 2
    right = left + size
    bottom = top + size

    cropped = resized.crop((left, top, right, bottom))
    return cropped

def add_logo_to_image(base_image, logo_image, logo_scale=0.3, position="bottom-left", margin=10):
    base = base_image.convert("RGBA")
    logo = logo_image.convert("RGBA")

    logo_width = int(base.width * logo_scale)
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    if position == "top-left":
        pos = (margin, margin)
    elif position == "top-right":
        pos = (base.width - logo.width - margin, margin)
    elif position == "bottom-left":
        pos = (margin, base.height - logo.height - margin)
    elif position == "bottom-right":
        pos = (base.width - logo.width - margin, base.height - logo.height - margin)
    elif position == "center":
        pos = ((base.width - logo.width) // 2, (base.height - logo.height) // 2)
    else:
        pos = (base.width - logo.width - margin, base.height - logo.height - margin)

    base.paste(logo, pos, mask=logo)
    return base

def add_ce_text(base_image, text="CE", text_scale=0.1, position="bottom-left", margin=10):
    base = base_image.convert("RGBA")
    draw = ImageDraw.Draw(base)

    font_size = int(base.width * text_scale)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if position == "top-left":
        pos = (margin, margin)
    elif position == "top-right":
        pos = (base.width - text_width - margin, margin)
    elif position == "bottom-left":
        pos = (margin, base.height - text_height - margin)
    elif position == "bottom-right":
        pos = (base.width - text_width - margin, base.height - text_height - margin)
    elif position == "center":
        pos = ((base.width - text_width) // 2, (base.height - text_height) // 2)
    else:
        pos = (margin, base.height - text_height - margin)

    outline_range = max(1, font_size // 15)
    for dx in range(-outline_range, outline_range + 1):
        for dy in range(-outline_range, outline_range + 1):
            if dx != 0 or dy != 0:
                draw.text((pos[0] + dx, pos[1] + dy), text, font=font, fill=(0, 0, 0, 180))

    draw.text(pos, text, font=font, fill=(255, 255, 255, 200))

    return base

st.title("🖼️ Image Logo Overlay App (Resize & Crop to 1600x1600)")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
uploaded_logo = st.file_uploader("Upload your logo (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, size=1600)

    # Logo options with defaults: bottom-left and 30%
    position = st.selectbox(
        "Select logo position",
        options=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        index=2,  # bottom-left default
    )
    st.markdown("**Best position:** bottom-left")

    logo_scale = st.slider(
        "Logo size (as % of image width)",
        min_value=5,
        max_value=50,
        value=30,  # default 30%
        step=1,
    ) / 100
    st.markdown("**Recommended logo size:** 30% of image width")

    # CE text toggle and options
    add_ce = st.checkbox("Add CE text on the image")

    if add_ce:
        ce_position = st.selectbox(
            "Select CE text position",
            options=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
            index=3,  # default bottom-right for CE text
            key="ce_pos",
        )

        ce_scale = st.slider(
            "CE text size (as % of image width)",
            min_value=5,
            max_value=50,
            value=10,
            step=1,
            key="ce_scale",
        ) / 100

    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    if add_ce:
        result = add_ce_text(result, text="CE", text_scale=ce_scale, position=ce_position)

    st.subheader("🔍 Preview:")
    st.image(result, use_container_width=True)

    img_buffer = io.BytesIO()
    result.convert("RGB").save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    st.download_button(
        label="💾 Download Image with Logo",
        data=img_buffer,
        file_name="image_with_logo.jpg",
        mime="image/jpeg",
    )
