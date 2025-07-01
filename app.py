import streamlit as st
from PIL import Image
import io

def add_logo_to_image(base_image, logo_image, scale=0.2, margin=10):
    base = base_image.convert("RGBA")
    logo = logo_image.convert("RGBA")

    # Resize logo to be 20% of base image width
    logo_width = int(base.width * scale)
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height))

    # Position: bottom-right corner
    position = (base.width - logo.width - margin, base.height - logo.height - margin)

    # Overlay logo
    base.paste(logo, position, mask=logo)
    return base.convert("RGB")  # Convert to RGB for saving as JPEG

st.title("🖼️ Image Logo Overlay App")

# Upload base image
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Upload logo
uploaded_logo = st.file_uploader("Upload your logo", type=["png"])

if uploaded_image and uploaded_logo:
    image = Image.open(uploaded_image)
    logo = Image.open(uploaded_logo)

    result = add_logo_to_image(image, logo)

    st.subheader("🔍 Preview:")
    st.image(result, use_column_width=True)

    # Save final image to memory for download
    img_buffer = io.BytesIO()
    result.save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    st.download_button(
        label="💾 Download Image with Logo",
        data=img_buffer,
        file_name="image_with_logo.jpg",
        mime="image/jpeg"
    )
