import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(layout="wide")  # Use full browser width

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

def add_logos_to_image(base_image, logos_with_positions, logo_scale=0.3, margin=20, line_height_px=0):
    base = base_image.convert("RGBA")
    
    for logo, position in logos_with_positions:
        logo_w = int(base.width * logo_scale)
        logo_h = int(logo.height * (logo_w / logo.width))
        resized_logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Calculate x, y based on position
        if position in ["bottom-left", "bottom-right"]:
            y = base.height - line_height_px - resized_logo.height - margin
        elif position == "center":
            y = (base.height - resized_logo.height) // 2
        else:  # top positions
            y = margin

        if position in ["top-left", "bottom-left"]:
            x = margin
        elif position in ["top-right", "bottom-right"]:
            x = base.width - resized_logo.width - margin
        else:
            x = (base.width - resized_logo.width) // 2

        # Use alpha channel as mask if present
        if resized_logo.mode == "RGBA":
            mask = resized_logo.split()[-1]
        else:
            mask = None

        base.paste(resized_logo, (x, y), mask=mask)

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
    left_rect = (0, y_start, width // 2, height)
    draw.rectangle(left_rect, fill=left_bg_color)
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

st.title("🖼️ Image with Split Bottom Line and Side Texts (Preset Line Colors)")

uploaded_image = st.file_uploader("Upload Base Image (jpg/png)", type=["jpg", "jpeg", "png"])

with st.sidebar:
    st.header("Options")

    use_logo1 = st.checkbox("Activate Logo: Made in Germany", value=True)
    use_logo2 = st.checkbox("Activate Logo: DHL Logo", value=True)
    use_logo3 = st.checkbox("Activate Logo: ECS Logo", value=True)

    logo1 = None
    logo2 = None
    logo3 = None
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
    if use_logo3:
        try:
            logo3 = Image.open("ECS.png")
        except FileNotFoundError:
            st.error("Logo 'ECS.png' not found.")

    # Logo position for Made in Germany and DHL logos (together)
    logo_position = st.selectbox("Logo Position (Made in Germany & DHL)", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
    logo_scale = st.slider("Logo Size %", 5, 50, 20)

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
    preset_name = st.selectbox("Bottom Line Color Preset", list(color_presets.keys()))

    left_bg_color, right_bg_color = color_presets[preset_name]

    left_bold = st.checkbox("Bold Left Text", value=True)
    right_bold = st.checkbox("Bold Right Text", value=False)

    left_font_size = st.slider("Left Font Size (px)", 10, 200, 60)
    right_font_size = st.slider("Right Font Size (px)", 10, 200, 50)

    line_height_pct = st.slider("Bottom Line Height %", 5, 30, 7) / 100

# Layout: two columns - left for uploader + options, right for preview
col1, col2 = st.columns([1, 2])

with col1:
    if uploaded_image:
        image = Image.open(uploaded_image)
        if image.width != image.height:
            st.warning(
                "⚠️ Image is not square (1:1 ratio). It will be center-cropped automatically to 1600×1600 pixels."
                " Or crop manually here: https://iloveimg.app/crop-image"
            )

with col2:
    if uploaded_image:
        resized_image = resize_and_crop(image, 1600)

        line_height_px = int(resized_image.height * line_height_pct)
        top_margin_in_line = 10

        # Logos for Made in Germany and DHL together at the selected position
        logos_side = []
        if logo1 is not None:
            logos_side.append(logo1)
        if logo2 is not None:
            logos_side.append(logo2)

        logos_with_positions = []
        for logo in logos_side:
            logos_with_positions.append((logo, logo_position))

        # Add ECS logo separately at bottom-left (if enabled)
        if logo3 is not None:
            logos_with_positions.append((logo3, "bottom-left"))

        result = add_logos_to_image(resized_image, logos_with_positions, logo_scale=logo_scale/100, margin=20, line_height_px=line_height_px)
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

        st.markdown("## Preview")
        st.image(result, use_container_width=True)

        buf = io.BytesIO()
        result.convert("RGB").save(buf, format="JPEG")
        buf.seek(0)
        st.download_button("💾 Download Image", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")

    else:
        st.info("Please upload a base image to get started.")
