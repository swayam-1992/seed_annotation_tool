# pages/4_Annotation_Grid.py
import streamlit as st
import json
import os
import shutil
from datetime import datetime
import io

st.set_page_config(layout="wide", page_title="Cell Annotation")

# ---------------------------------------------------------
# CSS: Make dropdowns smaller + reduce row spacing
# ---------------------------------------------------------
st.markdown("""
<style>

.small-selectbox > div > div {
    padding-top: 1px !important;
    padding-bottom: 1px !important;
    min-height: 26px !important;
    font-size: 12px !important;
}

/* Reduce label size */
.small-selectbox label {
    font-size: 11px !important;
    margin-bottom: -4px !important;
}

/* Remove large gaps between selectboxes */
div[data-baseweb="select"] {
    margin-top: -6px !important;
    margin-bottom: -6px !important;
}

/* Reduce space between rows of columns */
.block-container .row-widget.stColumns {
    margin-bottom: -12px !important;
}

/* Optional: prevent content feeling too wide on very large screens */
.block-container {
    max-width: 1400px;
    padding-left: 2rem;
    padding-right: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Safety Check
# ---------------------------------------------------------
if "metadata" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No tray data found! Complete previous steps first.")
    st.stop()

meta = st.session_state.metadata

clean_img = st.session_state.rotated_image
grid_img = clean_img

nrows, ncols = meta["nrows"], meta["ncols"]

# ---------------------------------------------------------
# Labels
# ---------------------------------------------------------
LABELS = {
    "UG": "Ungerminated",
    "G": "Germinated",
    "A": "Abnormal",
}
label_keys = list(LABELS.keys())

INT_TO_LABEL = {0: "UG", 1: "G", 2: "A"}

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

# ---------------------------------------------------------
# SIDE-BY-SIDE LAYOUT
# ---------------------------------------------------------
# Use more balanced columns so the table has enough room
left, right = st.columns([1, 1])

with left:
    # Let Streamlit scale image to column width (aspect ratio preserved automatically)
    st.image(grid_img, caption="Reference Image (Top)", use_column_width=True)
    st.image(grid_img, caption="Reference Image (Bottom)", use_column_width=True)

with right:
    st.markdown("### Annotation Grid")

    for r in range(nrows):
        cols = st.columns(ncols)
        for c in range(ncols):
            current_value = st.session_state.grid[r][c]

            with cols[c]:
                st.markdown('<div class="small-selectbox">', unsafe_allow_html=True)
                new_value = st.selectbox(
                    f"R{r+1}C{c+1}",
                    label_keys,
                    index=label_keys.index(current_value),
                    key=f"cell_{r}_{c}",
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.session_state.grid[r][c] = new_value

# ---------------------------------------------------------
# Continue → Preview Page
# ---------------------------------------------------------
st.markdown("---")

if st.button("Preview Annotation Summary ➜", type="primary"):
    st.session_state.annotation_final = st.session_state.grid

    buf = io.BytesIO()
    clean_img.save(buf, format="PNG")
    st.session_state.clean_bytes = buf.getvalue()

    st.switch_page("pages/5_Preview_Annotation.py")
