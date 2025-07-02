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

def add_text_bottom_single_line(image,
                                left_text, right_text,
                                left_font_size, right_font_size,
                                left_color, right_color,
                                left_bg_rgba, right_bg_rgba,
                                is_bold_left, is_bold_right,
                                margin=20):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)

    try:
        left_font = ImageFont.truetype("arialbd.ttf" if is_bold_left else "arial.ttf", left_font_size)
        right_font = ImageFont.truetype("arialbd.ttf" if is_bold_right else "arial.ttf", right_font_size)
    except:
        left_font = ImageFont.load_default()
        right_font = ImageFont.load_default()

    width, height = image.size
    half_width = width // 2

    # Measure text sizes
    left_bbox = draw.textbbox((0, 0), left_text, font=left_font)
    left_text_w = left_bbox[2] - left_bbox[0]
    left_text_h = left_bbox[3] - left_bbox[1]

    right_bbox = draw.textbbox((0, 0), right_text, font=right_font)
    right_text_w = right_bbox[2] - right_bbox[0]
    right_text_h = right_bbox[3] - right_bbox[1]

    max_text_height = max(left_text_h, right_text_h)

    # Vertical position: from bottom, margin + max text height
    y = height - margin - max_text_height

    # LEFT TEXT: align left starting at margin
    left_x = margin

    # RIGHT TEXT: align right starting at right edge minus margin
    right_x = width - margin - right_text_w

    # But right text must not overlap left half, so minimum right_x is center + margin
    if right_x < half_width + margin:
        right_x = half_width + margin

    # Draw backgrounds with padding
    padding_left = int(left_font_size * 0.3)
    padding_right = int(right_font_size * 0.3)

    left_bg_rect = (
        left_x - padding_left,
        y - padding_left,
        min(left_x + left_text_w + padding_left, half_width - margin),
        y + left_text_h + padding_left
    )
    right_bg_rect = (
        right_x - padding_right,
        y - padding_right,
        min(right_x + right_text_w + padding_right, width - margin),
        y + right_text_h + padding_right
    )

    draw.rectangle(left_bg_rect, fill=left_bg_rgba)
    draw.rectangle(right_bg_rect, fill=right_bg_rgba)

    # Draw texts
    draw.text((left_x, y), left_text, font=left_font, fill=left_color)
    draw.text((right_x, y), right_text, font=right_font, fill=right_color)

    return image

# --- Streamlit app ---
st.title("🖼️ Image with Bottom Split Single Line Text")

uploaded_image = st.file_uploader("Upload base image (jpg/png)", type=["jpg","jpeg","png"])
uploaded_logo = st.file_uploader("Upload logo image (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, 1600)

    position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=2)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 30) / 100

    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    st.markdown("### Text overlay (Single line at bottom, left and right halves)")

    left_text = st.text_input("Left Text (Left half)", "Awesome Product")
    right_text = st.text_input("Right Text (Right half)", "Details or subtitle here")

    left_color = st.color_picker("Left Text Color", "#FFFFFF")
    left_bg_color = st.color_picker("Left Text Background Color", "#000000")
    left_bg_opacity = st.slider("Left Background Opacity (%)", 0, 100, 40)

    right_color = st.color_picker("Right Text Color", "#FFFFFF")
    right_bg_color = st.color_picker("Right Text Background Color", "#000000")
    right_bg_opacity = st.slider("Right Background Opacity (%)", 0, 100, 30)

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_size_pct = st.slider("Left Font Size (% of image width)", 5, 40, 20)
    right_font_size_pct = st.slider("Right Font Size (% of image width)", 3, 35, 14)

    left_font_size = int(1600 * (left_font_size_pct / 100))
    right_font_size = int(1600 * (right_font_size_pct / 100))

    left_bg_rgba = hex_to_rgba(left_bg_color, left_bg_opacity)
    right_bg_rgba = hex_to_rgba(right_bg_color, right_bg_opacity)

    result = add_text_bottom_single_line(
        result,
        left_text=left_text,
        right_text=right_text,
        left_font_size=left_font_size,
        right_font_size=right_font_size,
        left_color=left_color,
        right_color=right_color,
        left_bg_rgba=left_bg_rgba,
        right_bg_rgba=right_bg_rgba,
        is_bold_left=left_bold,
        is_bold_right=right_bold
    )

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")
