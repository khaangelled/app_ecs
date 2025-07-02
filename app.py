import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

def resize_image_to_min(image, min_size=1600):
    """Resize image so that both width and height are at least min_size."""
    ratio = max(min_size / image.width, min_size / image.height, 1)  # never scale down here
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def crop_image(image, size=1600, x_offset=0, y_offset=0):
    """Crop a square of given size with offsets (x_offset, y_offset)."""
    return image.crop((x_offset, y_offset, x_offset + size, y_offset + size))

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

    # Left half background line
    left_rect = (0, y_start, width // 2, height)
    draw.rectangle(left_rect, fill=left_bg_color)

    # Right half background line
    right_rect = (width // 2, y_start, width, height)
    draw.rectangle(right_rect, fill=right_bg_color)

    try:
        left_font_path = "arialbd.ttf" if is_bold_left else "arial.ttf"
        right_font_path = "arialbd.ttf" if is_bold_right else "arial.ttf"
        left_font = ImageFont.truetype(left_font_path, left_font_size)
        right_font = ImageFont.truetype(right_font_path, right_font_size)
    except:
        left_font = ImageFont.load_default()
        right_font = ImageFont.load_default()

    y_text_left = y_start + top_margin_in_line
    y_text_right = y_start + top_margin_in_line
    x_text_left = margin
    x_text_right = width // 2 + margin

    draw.text((x_text_left, y_text_left), left_text, font=left_font, fill=left_text_color)
    draw.text((x_text_right, y_text_right), right_text, font=right_font, fill=right_text_color)

    return image


# --- Streamlit UI ---
st.title("🖼️ Manual Crop + Logos + Bottom Text Line")

uploaded_image = st.file_uploader("Upload Base Image (jpg/png)", type=["jpg", "jpeg", "png"])

st.markdown("### Activate Logos")
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
    img = Image.open(uploaded_image)
    resized_img = resize_image_to_min(img, 1600)

    # Calculate max offsets for cropping 1600x1600 square inside resized_img
    max_x = max(0, resized_img.width - 1600)
    max_y = max(0, resized_img.height - 1600)

    if max_x > 0:
        x_offset = st.slider("Horizontal crop offset (X)", 0, max_x, max_x // 2)
    else:
        x_offset = 0
        st.write("Horizontal crop offset not available (image width <= crop size)")

    if max_y > 0:
        y_offset = st.slider("Vertical crop offset (Y)", 0, max_y, max_y // 2)
    else:
        y_offset = 0
        st.write("Vertical crop offset not available (image height <= crop size)")

    cropped_img = crop_image(resized_img, 1600, x_offset, y_offset)

    # Continue your logo and text UI here, also indented properly...


    # Logo options
    logo_position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 20) / 100

    # Bottom line text options
    st.markdown("### Bottom split line with side texts")
    left_text = st.text_input("Left Text (left half)", "Awesome Product")
    right_text = st.text_input("Right Text (right half)", "Details or subtitle here")
    left_text_color = st.color_picker("Left Text Color", "#FFFFFF")
    right_text_color = st.color_picker("Right Text Color", "#FFFFFF")

    color_presets = {
        "Green & Beige": ("#52796f", "#a68a64"),
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
    top_margin_in_line = 10  # px

    # Add logos
    result_img = add_logos_to_image(cropped_img, logos_to_add, logo_scale=logo_scale, position=logo_position, margin=20, line_height_px=line_height_px)

    # Draw bottom split line with text
    result_img = draw_split_line_with_text(
        result_img,
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

    st.markdown("### Preview")
    st.image(result_img, use_container_width=True)

    buf = io.BytesIO()
    result_img.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")

else:
    st.info("Please upload a base image to get started.")
