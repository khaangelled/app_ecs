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

def hex_to_rgba(hex_color, opacity_percent):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(255 * (opacity_percent / 100))
    return (r, g, b, a)

def add_text_with_background(image, text, font_size_px, position, font_color, bg_rgba, is_bold, offset_y=0, margin=10):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)

    try:
        font_path = "arialbd.ttf" if is_bold else "arial.ttf"
        font = ImageFont.truetype(font_path, font_size_px)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if position == "top-left":
        x = margin
        y = margin + offset_y
    elif position == "top-right":
        x = image.width - text_width - margin
        y = margin + offset_y
    elif position == "bottom-left":
        x = margin
        y = image.height - text_height - margin + offset_y
    elif position == "bottom-right":
        x = image.width - text_width - margin
        y = image.height - text_height - margin + offset_y
    elif position == "center":
        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2 + offset_y
    else:
        x = margin
        y = margin + offset_y

    # Draw background rectangle
    draw.rectangle((x - 5, y - 5, x + text_width + 5, y + text_height + 5), fill=bg_rgba)

    # Draw text
    draw.text((x, y), text, font=font, fill=font_color)

    return image

# Streamlit App
st.title("🖼️ Image Logo Overlay App (Resize & Crop to 1600x1600)")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
uploaded_logo = st.file_uploader("Upload your logo (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, size=1600)

    position = st.selectbox(
        "Select logo position",
        options=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        index=2,
    )
    logo_scale = st.slider(
        "Logo size (as % of image width)",
        min_value=5,
        max_value=50,
        value=30,
        step=1,
    ) / 100

    add_ce = st.checkbox("Add CE text on the image")
    if add_ce:
        ce_position = st.selectbox(
            "Select CE text position",
            options=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
            index=3,
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

    st.markdown("## 📝 Add Two Custom Text Lines")

    # Line 1
    st.markdown("**Line 1 Settings**")
    line1 = st.text_input("Line 1 Text", value="First Line")
    line1_position = st.selectbox("Line 1 Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0, key="line1_pos")
    line1_color = st.color_picker("Line 1 Font Color", value="#FFFFFF", key="line1_color")
    line1_bg_color_hex = st.color_picker("Line 1 Background Color", value="#000000", key="line1_bg")
    line1_bg_opacity = st.slider("Line 1 Background Opacity (%)", 0, 100, 0, key="line1_opacity")
    line1_font_size = st.slider("Line 1 Font Size (px)", 10, 150, 60, key="line1_size")
    line1_bold = st.checkbox("Bold Line 1", value=False, key="line1_bold")

    # Line 2
    st.markdown("**Line 2 Settings**")
    line2 = st.text_input("Line 2 Text", value="Second Line")
    line2_position = st.selectbox("Line 2 Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0, key="line2_pos")
    line2_color = st.color_picker("Line 2 Font Color", value="#FF0000", key="line2_color")
    line2_bg_color_hex = st.color_picker("Line 2 Background Color", value="#000000", key="line2_bg")
    line2_bg_opacity = st.slider("Line 2 Background Opacity (%)", 0, 100, 0, key="line2_opacity")
    line2_font_size = st.slider("Line 2 Font Size (px)", 10, 150, 50, key="line2_size")
    line2_bold = st.checkbox("Bold Line 2", value=False, key="line2_bold")

    # Build result image
    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    if add_ce:
        result = add_ce_text(result, text="CE", text_scale=ce_scale, position=ce_position)

    # Convert colors
    line1_bg_rgba = hex_to_rgba(line1_bg_color_hex, line1_bg_opacity)
    line2_bg_rgba = hex_to_rgba(line2_bg_color_hex, line2_bg_opacity)

    # Add Line 1
    if line1:
        result = add_text_with_background(
            result,
            text=line1,
            font_size_px=line1_font_size,
            position=line1_position,
            font_color=line1_color,
            bg_rgba=line1_bg_rgba,
            is_bold=line1_bold,
            offset_y=0,
        )

    # Add Line 2 below Line 1 if same position
    if line2:
        offset = int(line1_font_size * 1.2) if line1_position == line2_position else 0
        result = add_text_with_background(
            result,
            text=line2,
            font_size_px=line2_font_size,
            position=line2_position,
            font_color=line2_color,
            bg_rgba=line2_bg_rgba,
            is_bold=line2_bold,
            offset_y=offset,
        )

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
