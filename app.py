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

def hex_to_rgba(hex_color, opacity_percent):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(255 * (opacity_percent / 100))
    return (r, g, b, a)

def draw_text_with_outline(draw, pos, text, font, fill, outline_fill=(0,0,0), outline_width=2):
    x, y = pos
    # Draw outline
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            if dx != 0 or dy != 0:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_fill)
    # Draw main text
    draw.text(pos, text, font=font, fill=fill)

def add_text_with_background(image, text, font_size_px, position, font_color, bg_rgba, is_bold, offset_y=0, margin=20):
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

    # Draw background rectangle with padding
    padding = int(font_size_px * 0.3)
    rect_coords = (x - padding, y - padding, x + text_width + padding, y + text_height + padding)
    draw.rectangle(rect_coords, fill=bg_rgba)

    # Draw text with black outline for contrast
    draw_text_with_outline(draw, (x, y), text, font, fill=font_color, outline_fill=(0,0,0), outline_width=max(1, font_size_px//20))

    return image

# --- Streamlit App ---

st.title("🖼️ Image Logo & Text Overlay (Resizable Text)")

uploaded_image = st.file_uploader("Upload base image (jpg/png)", type=["jpg","jpeg","png"])
uploaded_logo = st.file_uploader("Upload logo image (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, 1600)

    # Logo options
    position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=2)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 30) / 100

    # CE Text toggle
    add_ce = st.checkbox("Add CE text")
    if add_ce:
        ce_position = st.selectbox("CE position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=3)
        ce_scale = st.slider("CE text size (% of image width)", 5, 50, 10) / 100

    # Text Line 1
    st.markdown("### Line 1 Text Settings")
    line1_text = st.text_input("Line 1 Text", "My Brand")
    line1_position = st.selectbox("Line 1 Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    line1_color = st.color_picker("Line 1 Font Color", "#FFFFFF")
    line1_bg = st.color_picker("Line 1 Background Color", "#000000")
    line1_bg_opacity = st.slider("Line 1 Background Opacity (%)", 0, 100, 0)
    line1_scale = st.slider("Line 1 Font Size (% of image width)", 1, 50, 15) / 100
    line1_font_size = int(1600 * line1_scale)
    line1_bold = st.checkbox("Bold Line 1", value=True)

    # Text Line 2
    st.markdown("### Line 2 Text Settings")
    line2_text = st.text_input("Line 2 Text", "Tagline or subtitle")
    line2_position = st.selectbox("Line 2 Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    line2_color = st.color_picker("Line 2 Font Color", "#FF0000")
    line2_bg = st.color_picker("Line 2 Background Color", "#000000")
    line2_bg_opacity = st.slider("Line 2 Background Opacity (%)", 0, 100, 0)
    line2_scale = st.slider("Line 2 Font Size (% of image width)", 1, 50, 12) / 100
    line2_font_size = int(1600 * line2_scale)
    line2_bold = st.checkbox("Bold Line 2", value=False)

    # Compose image
    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    if add_ce:
        result = add_ce_text(result, text="CE", text_scale=ce_scale, position=ce_position)

    # Add line 1 text
    if line1_text.strip():
        bg1 = hex_to_rgba(line1_bg, line1_bg_opacity)
        result = add_text_with_background(
            result,
            line1_text,
            line1_font_size,
            line1_position,
            line1_color,
            bg1,
            line1_bold
        )

    # Add line 2 text, stacked below line 1 if same position
    if line2_text.strip():
        offset = int(line1_font_size * 1.2) if line1_position == line2_position else 0
        bg2 = hex_to_rgba(line2_bg, line2_bg_opacity)
        result = add_text_with_background(
            result,
            line2_text,
            line2_font_size,
            line2_position,
            line2_color,
            bg2,
            line2_bold,
            offset_y=offset
        )

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    # Download
    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("Download image with logo & text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")
