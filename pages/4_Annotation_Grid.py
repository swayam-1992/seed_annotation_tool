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
grid_img = clean_img   # ← Force clean image even if gridded_image existed before

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
# Page Title
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
# Prepare Download
# ---------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = f"{meta['crop']}_({meta['days_after_sowing']}d)_annotated_{timestamp}"

json_data = {
    "saved_at": datetime.now().isoformat(),
    "metadata": meta,
    "annotation_grid": st.session_state.grid
}

json_bytes = json.dumps(json_data, indent=2).encode("utf-8")

# Clean image (PNG)
img_buffer = io.BytesIO()
clean_img.save(img_buffer, format="PNG")
img_bytes = img_buffer.getvalue()

# ---------------------------------------------------------
# Download Buttons
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### Download Your Final Results")

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "Download Clean Image (.png)",
        img_bytes,
        file_name=f"{base_name}.png",
        mime="image/png"
    )

with c2:
    st.download_button(
        "Download Annotation (.json)",
        json_bytes,
        file_name=f"{base_name}.json",
        mime="application/json"
    )

# ---------------------------------------------------------
# Finish and Reset
# ---------------------------------------------------------
if st.button("Finish & Start New Tray", type="secondary"):
    for key in [
        "original_image", "rotated_image", "gridded_image", "processed_image",
        "metadata", "grid", "final_grid_rows", "final_grid_cols",
        "final_rotation", "image_path", "grid_bounds"
    ]:
        st.session_state.pop(key, None)

    if os.path.exists("temp_uploads"):
        shutil.rmtree("temp_uploads")
        os.makedirs("temp_uploads", exist_ok=True)

    st.success("Cleared! Starting fresh...")
    st.rerun()
