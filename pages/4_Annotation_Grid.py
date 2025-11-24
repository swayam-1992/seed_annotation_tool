# pages/4_Annotation_Grid.py
import streamlit as st
import json
import os
import shutil
from datetime import datetime
import io

st.set_page_config(layout="wide", page_title="Cell Annotation")

# ---------------------------------------------------------
# Safety Check
# ---------------------------------------------------------
if "metadata" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No tray data found! Complete previous steps first.")
    st.stop()

meta = st.session_state.metadata

clean_img = st.session_state.rotated_image
grid_img = clean_img   # ← Force clean reference image

nrows, ncols = meta["nrows"], meta["ncols"]

# ---------------------------------------------------------
# Labels
# ---------------------------------------------------------
LABELS = {
    "UG": "Ungerminated",
    "G": "Germinated",
    "A(S)": "Stunted",
    "A(L)": "Lanky",
    "A(D)": "Diseased",
    "A(O)": "Other"
}
label_keys = list(LABELS.keys())

INT_TO_LABEL = {0:"UG", 1:"G", 2:"A(S)", 3:"A(L)", 4:"A(D)", 5:"A(O)"}

# ---------------------------------------------------------
# Initialize grid if missing
# ---------------------------------------------------------
if "grid" not in st.session_state:
    st.session_state.grid = [[1 for _ in range(ncols)] for _ in range(nrows)]

# Convert old integer grid → label grid
for r in range(nrows):
    for c in range(ncols):
        val = st.session_state.grid[r][c]
        if isinstance(val, int):
            st.session_state.grid[r][c] = INT_TO_LABEL[val]

# ---------------------------------------------------------
# Title
# ---------------------------------------------------------
st.markdown("<h3>STEP 4 – Annotate Each Cell</h3>", unsafe_allow_html=True)

# Show Image
st.image(grid_img, caption="Reference Image", width=600)

# ---------------------------------------------------------
# Annotation Grid UI (Dropdown per cell)
# ---------------------------------------------------------
st.markdown("### Annotation Grid")

for r in range(nrows):
    cols = st.columns(ncols)
    for c in range(ncols):
        current_value = st.session_state.grid[r][c]
        new_value = cols[c].selectbox(
            f"R{r+1}C{c+1}",
            label_keys,
            index=label_keys.index(current_value),
            key=f"cell_{r}_{c}"
        )
        st.session_state.grid[r][c] = new_value

# ---------------------------------------------------------
# Continue → Preview Page
# ---------------------------------------------------------
st.markdown("---")

if st.button("Preview Annotation Summary ➜", type="primary"):
    st.session_state.annotation_final = st.session_state.grid
    st.session_state.clean_bytes = None

    # Convert image to PNG bytes for preview/download later
    buf = io.BytesIO()
    clean_img.save(buf, format="PNG")
    st.session_state.clean_bytes = buf.getvalue()

    st.switch_page("pages/5_Preview_Annotation.py")
