import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

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

def add_logos_to_image(base_image, logos, logo_scale=0.15, position="top-left", margin=10, line_height_px=100):
    base = base_image.convert("RGBA")

    logo_imgs = []
    for logo in logos:
        logo_width = int(base.width * logo_scale)
        logo_height = int(logo.height * (logo_width / logo.width))
        resized_logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS).convert("RGBA")
        logo_imgs.append(resized_logo)

    total_height = sum(logo.height for logo in logo_imgs) + (len(logo_imgs) - 1) * 5

    if position == "top-left":
        x = margin
        y = margin
    elif position == "top-right":
        x = base.width - max(logo.width for logo in logo_imgs) - margin
        y = margin
    elif position == "bottom-left":
        x = margin
        y = base.height - line_height_px - total_height - margin
    elif position == "bottom-right":
        x = base.width - max(logo.width for logo in logo_imgs) - margin
        y = base.height - line_height_px - total_height - margin
    elif position == "center":
        x = (base.width - max(logo.width for logo in logo_imgs)) // 2
        y = (base.height - total_height) // 2
    else:
        x = margin
        y = margin

    for logo in logo_imgs:
        base.paste(logo, (x, y), mask=logo)
        y += logo.height + 5

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

    y_text_left = y_start + top_margin_in_line
    y_text_right = y_start + top_margin_in_line

    x_text_left = margin  # left text starts margin from left edge
    x_text_right = width // 2 + margin  # right text starts margin from center

    draw.text((x_text_left, y_text_left), left_text, font=left_font, fill=left_text_color)
    draw.text((x_text_right, y_text_right), right_text, font=right_font, fill=right_text_color)

    return image, line_height

# ---------------- Streamlit app -------------------

st.title("🖼️ Image with Logos & Bottom Text Line")

# Logo active/deactive
enable_logo_made = st.checkbox("Show 'Made in Germany' logo", value=True)
enable_logo_dhl = st.checkbox("Show 'DHL' logo", value=True)

# Base image uploader
uploaded_image = st.file_uploader("Upload base image (jpg/png)", type=["jpg","jpeg","png"])

if uploaded_image:
    image = Image.open(uploaded_image)
    resized_image = resize_and_crop(image, 1600)
    result = resized_image.convert("RGBA")

    # Load fixed logos from local folder (must be in same folder as this script)
    # Provide relative path or absolute path if needed
    logos_folder = "."  # current folder
    logos_to_add = []

    if enable_logo_made:
        made_path = os.path.join(logos_folder, "made_in_germany.png")
        if os.path.isfile(made_path):
            logos_to_add.append(Image.open(made_path))
        else:
            st.warning("'made_in_germany.png' not found in folder.")

    if enable_logo_dhl:
        dhl_path = os.path.join(logos_folder, "dhl.png")
        if os.path.isfile(dhl_path):
            logos_to_add.append(Image.open(dhl_path))
        else:
            st.warning("'dhl.png' not found in folder.")

    # Logo position choice
    logo_position = st.selectbox("Logos Position", ["top-left", "top-right", "bottom-left", "bottom-right", "center"], index=2)
    logo_scale = st.slider("Logos size (% of image width)", 5, 50, 15) / 100  # smaller size default

    # Draw bottom line text settings
    enable_text = st.checkbox("Add Bottom Text Line", value=True)

    if enable_text:
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

        left_font_size = st.slider("Left Font Size (px)", min_value=10, max_value=200, value=60)
        right_font_size = st.slider("Right Font Size (px)", min_value=10, max_value=200, value=50)

        line_height_pct = st.slider("Bottom line height (% of image height)", 5, 30, 7) / 100

    else:
        # Default values if text disabled (to calculate logo position)
        left_text = right_text = ""
        left_text_color = right_text_color = "#FFFFFF"
        left_bg_color = right_bg_color = "#000000"
        left_bold = right_bold = False
        left_font_size = right_font_size = 20
        line_height_pct = 0.07

    # First draw bottom line with text (if enabled)
    result, line_height_px = draw_split_line_with_text(
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
        top_margin_in_line=10,
        is_bold_left=left_bold,
        is_bold_right=right_bold,
    )

    # Then add logos if any enabled
    if logos_to_add:
        result = add_logos_to_image(result, logos_to_add, logo_scale=logo_scale, position=logo_position, margin=20, line_height_px=line_height_px)

    st.markdown("### Preview")
    st.image(result, use_container_width=True)

    # Download button
    buf = io.BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    st.download_button("💾 Download Image with Logo and Text", data=buf, file_name="image_with_text.jpg", mime="image/jpeg")

else:
    st.info("Upload an image to see options and preview.")
