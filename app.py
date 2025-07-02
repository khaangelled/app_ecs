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

def add_text_bottom_split(image,
                          line1_text, line2_text,
                          line1_font_size, line2_font_size,
                          line1_color, line2_color,
                          line1_bg_rgba, line2_bg_rgba,
                          is_bold_line1, is_bold_line2,
                          margin=20,
                          spacing=10):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image)

    try:
        font1 = ImageFont.truetype("arialbd.ttf" if is_bold_line1 else "arial.ttf", line1_font_size)
        font2 = ImageFont.truetype("arialbd.ttf" if is_bold_line2 else "arial.ttf", line2_font_size)
    except:
        font1 = ImageFont.load_default()
        font2 = ImageFont.load_default()

    width, height = image.size
    half_width = width // 2

    # Get text sizes
    bbox1 = draw.textbbox((0, 0), line1_text, font=font1)
    text1_w = bbox1[2] - bbox1[0]
    text1_h = bbox1[3] - bbox1[1]

    bbox2 = draw.textbbox((0, 0), line2_text, font=font2)
    text2_w = bbox2[2] - bbox2[0]
    text2_h = bbox2[3] - bbox2[1]

    # Y position aligned at bottom with margin
    y = height - margin - max(text1_h, text2_h)

    # Line 1: left aligned in left half, with margin from left edge
    x1 = margin

    # Line 2: left aligned in right half, starting at half_width + margin
    x2 = half_width + margin

    # Padding around text bg rectangles
    padding1 = int(line1_font_size * 0.3)
    padding2 = int(line2_font_size * 0.3)

    # Draw backgrounds
    rect1 = (x1 - padding1, y - padding1,
             min(x1 + text1_w + padding1, half_width - margin), y + text1_h + padding1)
    draw.rectangle(rect1, fill=line1_bg_rgba)

    rect2 = (x2 - padding2, y - padding2,
             min(x2 + text2_w + padding2, width - margin), y + text2_h + padding2)
    draw.rectangle(rect2, fill=line2_bg_rgba)

    # Draw texts
    draw.text((x1, y), line1_text, font=font1, fill=line1_color)
    draw.text((x2, y), line2_text, font=font2, fill=line2_color)

    return image


# --- Streamlit app ---

st.title("🖼️ Image with Split Bottom Text")

uploaded_image = st.file_uploader("Upload base image (jpg/png)", type=["jpg","jpeg","png"])
uploaded_logo = st.file_uploader("Upload logo image (PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    resized_image = resize_and_crop(image, 1600)

    position = st.selectbox("Logo position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=2)
    logo_scale = st.slider("Logo size (% of image width)", 5, 50, 30) / 100

    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    st.markdown("### Text overlay (Bottom split left/right half)")

    product_name = st.text_input("Product Name (Left half)", "Awesome Product")
    product_info = st.text_input("Product Info (Right half)", "Details or subtitle here")

    line1_color = st.color_picker("Line 1 Text Color", "#FFFFFF")
    line1_bg_color = st.color_picker("Line 1 Background Color", "#000000")
    line1_bg_opacity = st.slider("Line 1 Background Opacity (%)", 0, 100, 40)

    line2_color = st.color_picker("Line 2 Text Color", "#FFFFFF")
    line2_bg_color = st.color_picker("Line 2 Background Color", "#000000")
    line2_bg_opacity = st.slider("Line 2 Background Opacity (%)", 0, 100, 30)

    line1_bold = st.checkbox("Bold Line 1", value=True)
    line2_bold = st.checkbox("Bold Line 2", value=False)

    line1_font_size_pct = st.slider("Line 1 Font Size (% of image width)", 5, 40, 20)
    line2_font_size_pct = st.slider("Line 2 Font Size (% of image width)", 3, 35, 14)

    line1_font_size = int(1600 * (line1_font_size_pct / 100))
    line2_font_size = int(1600 * (line2_font_size_pct / 100))

    line1_bg_rgba = hex_to_rgba(line1_bg_color, line1_bg_opacity)
    line2_bg_rgba = hex_to_rgba(line2_bg_color, line2_bg_opacity)

    result = add_text_bottom_split(
        result,
        line1_text=product_name,
        line2_text=product_info,
        line1_font_size=line1_font_size,
        line2_font_size=line2_font_size,
        line1_color=line1_color,
        line2_color=line2_color,
        line1_bg_rgba=line1_bg_rgba,
        line2_bg_rgba=line2_bg_rgba,
        is_bold_line1=line1_bold,
        is_bold_line2=line2_bold
    )

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")
