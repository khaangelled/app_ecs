import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def resize_image(image, target_size=1600):
    ratio = max(target_size / image.width, target_size / image.height)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized

def crop_with_offset(image, crop_size, offset_x, offset_y):
    left = offset_x
    top = offset_y
    right = left + crop_size
    bottom = top + crop_size
    return image.crop((left, top, right, bottom))

# Other functions (add_logos_to_image and draw_split_line_with_text) remain the same

# --- Streamlit UI ---

st.title("🖼️ Interactive Crop with Slide & Logo/Text Overlay")

uploaded_image = st.file_uploader("Upload Base Image (jpg/png)", type=["jpg", "jpeg", "png"])

use_logo1 = st.checkbox("Activate Logo: Made in Germany", value=True)
use_logo2 = st.checkbox("Activate Logo: DHL Logo", value=True)

logo1 = None
logo2 = None

if use_logo1:
    try:
        logo1 = Image.open("made_in_germany.png")
    except FileNotFoundError:
        st.error("Logo 'made_in_germany.png' not found.")
if use_logo2:
    try:
        logo2 = Image.open("dhl.png")
    except FileNotFoundError:
        st.error("Logo 'dhl.png' not found.")

logos_to_add = [logo for logo in [logo1, logo2] if logo is not None]

if uploaded_image:
    image = Image.open(uploaded_image)
    
    # Resize image first
    target_resize = st.slider("Resize base image to (px)", 500, 3000, 1600)
    resized_img = resize_image(image, target_resize)

    crop_size = st.slider("Crop size (px)", 200, min(resized_img.width, resized_img.height), 1000)

    max_offset_x = resized_img.width - crop_size
    max_offset_y = resized_img.height - crop_size

    st.markdown("### Slide crop area")

    offset_x = st.slider("Horizontal offset (X)", 0, max_offset_x, max_offset_x // 2)
    offset_y = st.slider("Vertical offset (Y)", 0, max_offset_y, max_offset_y // 2)

    cropped_img = crop_with_offset(resized_img, crop_size, offset_x, offset_y)

    # Logo and text options on the same page below sliders (simplified)
    logo_position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 20) / 100

    left_text = st.text_input("Left Text", "Awesome Product")
    right_text = st.text_input("Right Text", "Details or subtitle here")

    left_text_color = st.color_picker("Left Text Color", "#FFFFFF")
    right_text_color = st.color_picker("Right Text Color", "#FFFFFF")

    color_presets = {
        "Green & Geige": ("#52796f", "#a68a64"),
        "Red & Yellow": ("#d62828", "#fcbf49"),
        "Yellow & Beige": ("#ffc300", "#ede0d4"),
        "Teal Blues": ("#264653", "#2a9d8f"),
        "Olive & Cream": ("#606c38", "#fefae0"),
    }
    preset_name = st.selectbox("Bottom line color preset", list(color_presets.keys()))
    left_bg_color, right_bg_color = color_presets[preset_name]

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_size = st.slider("Left Font Size (px)", 10, 200, 60)
    right_font_size = st.slider("Right Font Size (px)", 10, 200, 50)

    line_height_pct = st.slider("Bottom line height (% of image height)", 5, 30, 7) / 100
    line_height_px = int(cropped_img.height * line_height_pct)
    top_margin_in_line = 10

    # Compose final image
    result = add_logos_to_image(cropped_img, logos_to_add, logo_scale=logo_scale, position=logo_position, margin=20, line_height_px=line_height_px)

    result = draw_split_line_with_text(
        result,
        left_text=left_text,
        right_text=right_text,
        left_font_size=left_font_size,
        right_font_size=right_font_size,
        left_text_color=left_text_color,
        right_text_color=right_text_color,
        left_bg_color=left_bg_color,
        right_bg_color=right_bg_color,
        line_height_pct=line_height_pct,
        margin=20,
        top_margin_in_line=top_margin_in_line,
        is_bold_left=left_bold,
        is_bold_right=right_bold,
    )

    st.image(result, use_container_width=True)

    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)
    st.download_button("💾 Download Image", data=buf, file_name="cropped_image.jpg", mime="image/jpeg")

else:
    st.info("Please upload an image to start.")
