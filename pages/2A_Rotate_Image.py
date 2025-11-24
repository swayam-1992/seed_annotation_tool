# pages/2A_Rotate_Image.py
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Rotate Image", layout="wide")
st.markdown("<h3>STEP 2 – Rotate Seed Tray Image</h3>", unsafe_allow_html=True)

if "original_image" not in st.session_state:
    st.error("No image found! Go back to Step 1.")
    if st.button("← Back to Upload"):
        st.switch_page("pages/1_Upload_Image.py")
    st.stop()

img = st.session_state.original_image.copy()

st.subheader("Choose correct orientation")
col1, col2 = st.columns([1, 3])

with col1:
    rotation = st.radio(
        "Rotate Image",
        options=[0, 90, 180, 270],
        format_func=lambda x: f"{x}°",
        index=0,
        key="rotation_choice"
    )
    if st.button("Next", type="primary", use_container_width=True):
        rotated = img.rotate(-rotation, expand=True)
        st.session_state.rotated_image = rotated
        st.session_state.final_rotation = rotation
    
        # Default grid values (required for metadata page)
        st.session_state.final_grid_rows = 14   # or whatever default you prefer
        st.session_state.final_grid_cols = 7    # or whatever default you prefer
    
        st.success(f"Rotation {rotation}° saved!")
        st.switch_page("pages/3_Metadata_Input.py")   # ← CHANGED HERE

with col2:
    rotated_preview = img.rotate(-rotation, expand=True)
    st.image(rotated_preview, width=400, caption=f"Preview: {rotation}° rotation")

st.info("Tip: Make sure Row 1 is at the top and Column 1 is on the left.")
