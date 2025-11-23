# pages/1_Upload_Image.py
import streamlit as st
import os
from PIL import Image
import shutil

# Create temp folder
if not os.path.exists("temp_uploads"):
    os.makedirs("temp_uploads")

st.markdown("<h3>STEP 1 - Upload Your Seed Tray Image</h3>", unsafe_allow_html=True)

uploaded = st.file_uploader("Choose an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded:
    # Save image
    img = Image.open(uploaded)
    filepath = f"temp_uploads/{uploaded.name}"
    img.save(filepath)

    # Store in session state
    st.session_state.image_path = filepath
    st.session_state.original_image = img

    st.success(f"Uploaded successfully: {uploaded.name}")
    st.image(img, caption="Your seed tray", width=200)
    
    if st.button("Next", type="primary"):
        st.switch_page("pages/2A_Rotate_Image.py")

        #st.switch_page("pages/2_Rotate_Grid.py")
else:
    st.info("Please upload an image to continue")
