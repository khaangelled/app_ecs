import streamlit as st
from PIL import Image
import io

def resize_and_crop(image, size=1600):
    # Resize image so smaller side >= size, keep aspect ratio
    ratio = max(size / image.width, size / image.height)
    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Now center-crop to size x size
    left = (new_width - size) // 2
    top = (new_height - size) // 2
    right = left + size
    bottom = top + size

    cropped = resized.crop((left, top, right, bottom))
    return cropped



def add_logo_to_image(base_image, logo_image, logo_scale=0.2, position="bottom-right", margin=10):
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
    return base.convert("RGB")

resized_image = resize_and_crop(image, size=1600)
st.title("🖼️ Image Logo Overlay App with Custom Position & Resize")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
uploaded_logo = st.file_uploader("Upload your logo (preferably PNG with transparency)", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    # Resize base image to max 1600 px
    resized_image = resize_image(image, max_size=1600)

    # User input: logo position
    position = st.selectbox(
        "Select logo position",
        options=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        index=3,
    )

    # User input: logo size as % of image width
    logo_scale = st.slider(
        "Logo size (as % of image width)", min_value=5, max_value=50, value=20, step=1
    ) / 100

    result = add_logo_to_image(resized_image, logo, logo_scale=logo_scale, position=position)

    st.subheader("🔍 Preview:")
    st.image(result, use_column_width=True)

    # Save final image to memory
    img_buffer = io.BytesIO()
    result.save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    st.download_button(
        label="💾 Download Image with Logo",
        data=img_buffer,
        file_name="image_with_logo.jpg",
        mime="image/jpeg"
    )

