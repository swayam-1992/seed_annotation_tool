# pages/6_Export.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime
import zipfile
from io import BytesIO

st.set_page_config(page_title="Export Results", layout="wide")
st.markdown("<h2 style='text-align: center;'>STEP 6 – Review & Export</h2>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Safety check
# ------------------------------------------------------------------
required_keys = ["original_image", "warped_bgr", "warped_rgb", "metadata", "final_grid"]
missing = [k for k in required_keys if k not in st.session_state]
if missing:
    st.error(f"Missing data: {', '.join(missing)}. Please complete previous steps.")
    if st.button("← Back to Annotation"):
        st.switch_page("pages/5_Annotation_Grid.py")
    st.stop()

original_img = st.session_state.original_image  # PIL
warped_bgr = st.session_state.warped_bgr.copy()  # cv2 BGR
warped_rgb = st.session_state.warped_rgb.copy()  # np RGB (clean)
metadata = st.session_state.metadata
grid = st.session_state.final_grid

nrows = metadata["nrows"]
ncols = metadata["ncols"]

# Total padded grid: 16x9
TOTAL_ROWS, TOTAL_COLS = 16, 9
H, W = warped_bgr.shape[:2]
cell_h = H // TOTAL_ROWS
cell_w = W // TOTAL_COLS

# ------------------------------------------------------------------
# Create overlaid (preview) image with colored borders
# ------------------------------------------------------------------
overlaid_bgr = warped_bgr.copy()
border_colors = {
    "G": (0, 255, 0),    # Green
    "A": (255, 165, 0),  # Orange
    "UG": (0, 0, 255)    # Red
}

for rr, r in enumerate(range(nrows)):
    for cc, c in enumerate(range(ncols)):
        label = grid[rr][cc]
        color = border_colors.get(label, (128, 128, 128))
        y1 = (r + 1) * cell_h
        y2 = y1 + cell_h
        x1 = (c + 1) * cell_w
        x2 = x1 + cell_w
        cv2.rectangle(overlaid_bgr, (x1, y1), (x2 - 1, y2 - 1), color, 6)

overlaid_rgb = cv2.cvtColor(overlaid_bgr, cv2.COLOR_BGR2RGB)

# Clean corrected image (for download)
clean_corrected_pil = Image.fromarray(warped_rgb)

# ------------------------------------------------------------------
# UI: Show overlaid preview + inputs
# ------------------------------------------------------------------
col_img, col_form = st.columns([2, 1])

with col_img:
    st.subheader("Preview: Annotated Perspective-Corrected Image")
    st.image(overlaid_rgb, caption="Overlay with colored borders (G=Green, A=Orange, UG=Red) – for preview only", use_container_width=True)

with col_form:
    st.subheader("Additional Details")
    
    # Germination count input
    default_germ_count = sum(row.count("G") for row in grid)
    germ_count = st.number_input(
        "Germination Count",
        min_value=0,
        max_value=nrows * ncols,
        value=default_germ_count,
        help="Total number of germinated seedlings (pre-filled from 'G' labels)"
    )
    
    st.subheader("Export Summary")
    st.json(metadata, expanded=False)
    st.markdown("**Annotation Grid Preview**")
    matrix_html = "<table style='width:100%; border-collapse: collapse; font-size: 0.9rm;'>"
    for row in grid:
        matrix_html += "<tr>"
        for cell in row:
            color = {"G": "#90EE90", "A": "#FFD700", "UG": "#FFB6C1"}.get(cell, "#CCCCCC")
            matrix_html += f"<td style='border:1px solid #ddd; padding:4px; text-align:center; background:{color};'>{cell}</td>"
        matrix_html += "</tr>"
    matrix_html += "</table>"
    st.markdown(matrix_html, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Filename base exactly like the reference example
# ------------------------------------------------------------------
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = f"{metadata['crop']}_({metadata['days_after_sowing']}d)_annotated_{timestamp_str}"

# ------------------------------------------------------------------
# Prepare JSON exactly like your sample
# ------------------------------------------------------------------
json_data = {
    "saved_at": datetime.now().isoformat(),
    "metadata": {
        "UID_legacy": f"{metadata['crop']}_{metadata['capture_date'][2:].replace('-', '')}_{metadata['days_after_sowing']}d",
        "capture_date": metadata["capture_date"],
        "sowing_date": metadata["sowing_date"],
        "days_after_sowing": metadata["days_after_sowing"],
        "crop": metadata["crop"],
        "nrows": nrows,
        "ncols": ncols,
        "shape": metadata["shape"]
    },
    "annotation_grid": grid,
    "germination_count": int(germ_count)
}

json_str = json.dumps(json_data, indent=2)

# ------------------------------------------------------------------
# Bundle into ZIP: original, clean corrected, JSON
# ------------------------------------------------------------------
zip_buffer = BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    # Original image
    orig_buffer = BytesIO()
    original_img.save(orig_buffer, format="PNG")
    zipf.writestr(f"{base_name}.png", orig_buffer.getvalue())
    
    # Clean perspective-corrected image (NO overlay)
    corrected_buffer = BytesIO()
    clean_corrected_pil.save(corrected_buffer, format="PNG")
    zipf.writestr(f"{base_name}_perspectivecorrected.png", corrected_buffer.getvalue())  # ← Clean corrected image (no suffix)
    
    # JSON
    zipf.writestr(f"{base_name}.json", json_str)

zip_buffer.seek(0)

# ------------------------------------------------------------------
# Download Button
# ------------------------------------------------------------------
st.markdown("---")
st.markdown("**Note:** The downloaded corrected image is **clean** (no borders). The overlay above is for preview only.")

if st.download_button(
    label="Download Export Bundle (ZIP: Original + Clean Corrected + JSON)",
    data=zip_buffer,
    file_name=f"{base_name}.zip",
    mime="application/zip",
    type="primary",
    use_container_width=True
):
    st.success("Export bundle downloaded successfully! (Contains clean corrected image)")

# Navigation
col_left, _ = st.columns(2)
with col_left:
    if st.button("← Back to Annotation"):
        st.switch_page("pages/5_Annotation_Grid.py")