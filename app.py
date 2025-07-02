import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(layout="wide")  # full browser width

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

# (Include your add_logos_to_image() and draw_split_line_with_text() functions here...)

# For brevity, I’ll assume those are copied as-is from your previous code

# === UI ===

st.title("🖼️ Image with Split Bottom Line and Side Texts")

uploaded_image = st.file_uploader("Upload Base Image (jpg/png)", type=["jpg", "jpeg", "png"])

if uploaded_image:

    # Split the page horizontally: controls on left (25%), image on right (75%)
    col1, col2 = st.columns([1, 3])  # 1:3 ratio

    with col1:
        st.header("Settings")

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

        logo_position = st.selectbox("Logo Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=0)
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

    with col2:
        image = Image.open(uploaded_image)
        if image.width != image.height:
            st.warning(
                "⚠️ Image is not square (1:1 ratio). It will be center-cropped automatically to 1600×1600 pixels."
                " Or crop manually here: https://iloveimg.app/crop-image"
            )
        resized_image = resize_and_crop(image, 1600)

        line_height_px = int(resized_image.height * line_height_pct)
        top_margin_in_line = 10

        result = add_logos_to_image(resized_image, logos_to_add, logo_scale=logo_scale / 100, position=logo_position, margin=20, line_height_px=line_height_px)
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
        st.image(result, use_column_width=True)  # This fills col2 width

        buf = io.BytesIO()
        result.convert("RGB").save(buf, format="JPEG")
        buf.seek(0)

        st.download_button("💾 Download Image", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")

else:
    st.info("Please upload a base image to get started.")
