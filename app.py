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

    # Calculate vertical position for text: always y_start + top_margin_in_line
    y_text_left = y_start + top_margin_in_line
    y_text_right = y_start + top_margin_in_line

    # Text bounding boxes (to check if text fits vertically)
    left_bbox = draw.textbbox((0, 0), left_text, font=left_font)
    left_text_height = left_bbox[3] - left_bbox[1]

    right_bbox = draw.textbbox((0, 0), right_text, font=right_font)
    right_text_height = right_bbox[3] - right_bbox[1]

    # Warn if text might overflow line height (optional)
    if left_text_height + top_margin_in_line > line_height:
        st.warning(f"Left text height ({left_text_height}px) + top margin ({top_margin_in_line}px) exceeds line height ({line_height}px). Increase line height or reduce font size.")
    if right_text_height + top_margin_in_line > line_height:
        st.warning(f"Right text height ({right_text_height}px) + top margin ({top_margin_in_line}px) exceeds line height ({line_height}px). Increase line height or reduce font size.")

    # Text X positions:
    x_text_left = margin  # left text starts margin from left edge
    x_text_right = width // 2 + margin  # right text starts margin from center

    # Draw texts (no background on text itself)
    draw.text((x_text_left, y_text_left), left_text, font=left_font, fill=left_text_color)
    draw.text((x_text_right, y_text_right), right_text, font=right_font, fill=right_text_color)

    return image

# Streamlit UI
st.title("🖼️ Image with Split Bottom Line and Side Texts (Preset Line Colors)")

uploaded_image = st.file_uploader("Upload base image (jpg/png)", type=["jpg","jpeg","png"])
uploaded_logo = st.file_uploader("Upload logo image (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, 1600)

    position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=2)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 30) / 100

    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    st.markdown("### Bottom split line with side texts")

    left_text = st.text_input("Left Text (left half)", "Awesome Product")
    right_text = st.text_input("Right Text (right half)", "Details or subtitle here")

    left_text_color = st.color_picker("Left Text Color", "#FFFFFF")
    right_text_color = st.color_picker("Right Text Color", "#FFFFFF")

    # Preset line color options (name, (left_bg, right_bg))
    color_presets = {
        "Olive & Cream": ("#606c38", "#fefae0"),
        "Red & Yellow": ("#d62828", "#fcbf49"),
        "Yellow & Beige": ("#ffc300", "#ede0d4"),
        "Teal Blues": ("#264653", "#2a9d8f"),
        "Purple & Pink": ("#8338ec", "#ff6f91"),
    }

    preset_name = st.selectbox("Choose bottom line color preset", list(color_presets.keys()))

    left_bg_color, right_bg_color = color_presets[preset_name]

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_size = st.slider("Left Font Size (px)", min_value=10, max_value=200, value=60)
    right_font_size = st.slider("Right Font Size (px)", min_value=10, max_value=200, value=48)

    line_height_pct = st.slider("Bottom line height (% of image height)", 5, 30, 20) / 100

    top_margin_in_line = 10  # fixed 10 px from top of line for text

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

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")
