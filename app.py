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

    # Load fonts
    try:
        left_font = ImageFont.truetype("arialbd.ttf" if is_bold_left else "arial.ttf", left_font_size)
        right_font = ImageFont.truetype("arialbd.ttf" if is_bold_right else "arial.ttf", right_font_size)
    except:
        left_font = ImageFont.load_default()
        right_font = ImageFont.load_default()

    # Calculate vertical position for text (center vertically in line)
    # Using textbbox to get height:
    left_bbox = draw.textbbox((0, 0), left_text, font=left_font)
    left_text_height = left_bbox[3] - left_bbox[1]

    right_bbox = draw.textbbox((0, 0), right_text, font=right_font)
    right_text_height = right_bbox[3] - right_bbox[1]

    y_text_left = y_start + (line_height - left_text_height) // 2
    y_text_right = y_start + (line_height - right_text_height) // 2

    # Text X positions:
    x_text_left = margin  # left text starts with margin from left edge
    x_text_right = width // 2 + margin  # right text starts margin from center

    # Draw texts (no background)
    draw.text((x_text_left, y_text_left), left_text, font=left_font, fill=left_text_color)
    draw.text((x_text_right, y_text_right), right_text, font=right_font, fill=right_text_color)

    return image

# Streamlit app
st.title("🖼️ Image with Split Bottom Line and Side Texts")

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

    left_bg_color = st.color_picker("Left Line Background Color", "#0033cc")
    right_bg_color = st.color_picker("Right Line Background Color", "#cc3300")

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_pct = st.slider("Left Font Size (% of image height)", 5, 25, 15)
    right_font_pct = st.slider("Right Font Size (% of image height)", 5, 25, 12)

    left_font_size = int(1600 * (left_font_pct / 100))
    right_font_size = int(1600 * (right_font_pct / 100))

    line_height_pct = st.slider("Bottom line height (% of image height)", 5, 30, 15) / 100

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
        is_bold_left=left_bold,
        is_bold_right=right_bold
    )

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")
