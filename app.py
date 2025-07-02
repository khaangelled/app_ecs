import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def manual_crop(image, size=1600, x_offset=0, y_offset=0):
    # Resize image first so that smallest side is at least size
    ratio = max(size / image.width, size / image.height)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Clamp offsets so crop box stays inside resized image
    max_x = new_width - size
    max_y = new_height - size
    x_offset = min(max(x_offset, 0), max_x)
    y_offset = min(max(y_offset, 0), max_y)

    cropped = resized.crop((x_offset, y_offset, x_offset + size, y_offset + size))
    return cropped

def add_logos_to_image(base_image, logos, logo_scale=0.3, position="top-left", margin=20, line_height_px=0):
    base = base_image.convert("RGBA")

    logo_imgs = []
    for logo in logos:
        logo_w = int(base.width * logo_scale)
        logo_h = int(logo.height * (logo_w / logo.width))
        resized_logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        logo_imgs.append(resized_logo)

    total_height = sum(logo.height for logo in logo_imgs) + margin * (len(logo_imgs) - 1)

    if position in ["bottom-left", "bottom-right"]:
        y_start = base.height - line_height_px - total_height - margin
    elif position == "center":
        y_start = (base.height - total_height) // 2
    else:
        y_start = margin

    if position in ["top-left", "bottom-left"]:
        x_pos = margin
    elif position in ["top-right", "bottom-right"]:
        max_logo_width = max(logo.width for logo in logo_imgs)
        x_pos = base.width - max_logo_width - margin
    else:
        x_pos = (base.width - max(logo.width for logo in logo_imgs)) // 2

    y = y_start
    for logo in logo_imgs:
        logo = logo.convert("RGBA")  # Ensure alpha channel for mask
        base.paste(logo, (x_pos, y), mask=logo)
        y += logo.height + margin

    return base

def draw_split_line_with_text(image,
                              left_text, right_text,
                              left_font_size, right_font_size,
                              left_text_color, right_text_color,
                              left_bg_color, right_bg_color,
                              line_height_pct=0.15,
                              margin=20,
                              top_margin_in_line=10,
                              is_bold_left=False,
                              is_bold_right=False):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)

    width, height = image.size

    line_height = int(height * line_height_pct)
    y_start = height - line_height

    # Draw left half background line
    left_rect = (0, y_start, width // 2, height)
    draw.rectangle(left_rect, fill=left_bg_color)

    # Draw right half background line
    right_rect = (width // 2, y_start, width, height)
    draw.rectangle(right_rect, fill=right_bg_color)

    # Load fonts (try bold if requested)
    try:
        left_font_path = "arialbd.ttf" if is_bold_left else "arial.ttf"
        right_font_path = "arialbd.ttf" if is_bold_right else "arial.ttf"
        left_font = ImageFont.truetype(left_font_path, left_font_size)
        right_font = ImageFont.truetype(right_font_path, right_font_size)
    except:
        left_font = ImageFont.load_default()
        right_font = ImageFont.load_default()

    # Vertical position for text: fixed top margin inside line
    y_text_left = y_start + top_margin_in_line
    y_text_right = y_start + top_margin_in_line

    # Text X positions:
    x_text_left = margin  # left text starts margin from left edge
    x_text_right = width // 2 + margin  # right text starts margin from center

    # Draw texts (no background on text itself)
    draw.text((x_text_left, y_text_left), left_text, font=left_font, fill=left_text_color)
    draw.text((x_text_right, y_text_right), right_text, font=right_font, fill=right_text_color)

    return image

# --- Streamlit UI ---

st.title("🖼️ Manual Crop + Logos + Bottom Text Line")

uploaded_image = st.file_uploader("Upload your base image (jpg/png)", type=["jpg", "jpeg", "png"])

use_logo1 = st.checkbox("Activate Logo: Made in Germany", value=True)
use_logo2 = st.checkbox("Activate Logo: DHL Logo", value=True)

logo1 = None
logo2 = None

if use_logo1:
    try:
        logo1 = Image.open("made_in_germany.png")
    except FileNotFoundError:
        st.error("Logo 'made_in_germany.png' not found in the app folder.")
if use_logo2:
    try:
        logo2 = Image.open("dhl.png")
    except FileNotFoundError:
        st.error("Logo 'dhl.png' not found in the app folder.")

logos_to_add = [logo for logo in [logo1, logo2] if logo is not None]

if uploaded_image:
    image = Image.open(uploaded_image)

    st.markdown(f"**Original image size:** {image.width} x {image.height}")

    crop_size = 1600

    # First resize ratio to get large enough image for cropping
    ratio = max(crop_size / image.width, crop_size / image.height)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)

    # Show resized size info
    st.markdown(f"**Image will be resized to:** {new_width} x {new_height}")

    # Crop offset sliders
    max_x = new_width - crop_size
    max_y = new_height - crop_size

    x_offset = st.slider("Horizontal crop offset (X)", 0, max_x, max_x // 2)
    y_offset = st.slider("Vertical crop offset (Y)", 0, max_y, max_y // 2)

    # Perform manual crop
    cropped_img = manual_crop(image, size=crop_size, x_offset=x_offset, y_offset=y_offset)

    st.image(cropped_img, caption="Cropped Preview", use_container_width=True)

    # Logo options
    logo_position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 20) / 100

    # Bottom line and text inputs
    st.markdown("### Bottom split line with side texts")

    left_text = st.text_input("Left Text (left half)", "Awesome Product")
    right_text = st.text_input("Right Text (right half)", "Details or subtitle here")

    left_text_color = st.color_picker("Left Text Color", "#FFFFFF")
    right_text_color = st.color_picker("Right Text Color", "#FFFFFF")

    color_presets = {
        "Green & Geige": ("#52796f", "#a68a64"),
        "Red & Yellow": ("#d62828", "#fcbf49"),
        "Yellow & Beige": ("#ffc300", "#ede0d4"),
        "Teal Blues": ("#264653", "#2a9d8f"),
        "Olive & Cream": ("#606c38", "#fefae0"),
    }

    preset_name = st.selectbox("Choose bottom line color preset", list(color_presets.keys()))
    left_bg_color, right_bg_color = color_presets[preset_name]

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_size = st.slider("Left Font Size (px)", 10, 200, 60)
    right_font_size = st.slider("Right Font Size (px)", 10, 200, 50)

    line_height_pct = st.slider("Bottom line height (% of image height)", 5, 30, 7) / 100
    line_height_px = int(cropped_img.height * line_height_pct)
    top_margin_in_line = 10

    # Add logos
    result = add_logos_to_image(cropped_img, logos_to_add, logo_scale=logo_scale, position=logo_position, margin=20, line_height_px=line_height_px)

    # Draw bottom line + text
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

    st.markdown("### Final Preview")
    st.image(result, use_container_width=True)

    # Download button
    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)
    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")

else:
    st.info("Please upload a base image to get started.")
