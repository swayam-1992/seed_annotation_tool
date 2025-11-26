# pages/5_Preview_Annotation.py
import streamlit as st
import json
from datetime import datetime
import io
from PIL import Image
import zipfile

st.set_page_config(page_title="Preview Annotation", layout="wide")

# ---------------------------------------------------------
# SAFETY CHECK
# ---------------------------------------------------------
if "annotation_final" not in st.session_state or "metadata" not in st.session_state:
    st.error("No annotation data found. Please complete previous steps.")
    st.stop()

meta = st.session_state.metadata
grid = st.session_state.annotation_final
clean_bytes = st.session_state.clean_bytes

nrows = len(grid)
ncols = len(grid[0])

# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------
COLOR_MAP = {
    "UG": "#ffcccc",  # red
    "G":  "#ccffcc",  # green
    "A":  "#ccccff",  # blue
}

# ---------------------------------------------------------
# BASENAME (YOUR EXACT LOGIC)
# ---------------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = f"{meta['crop']}_({meta['days_after_sowing']}d)_annotated_{timestamp}"

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("<h3>STEP 5 – Preview & Download</h3>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDE-BY-SIDE LAYOUT (Image | Table)
# ---------------------------------------------------------
left, right = st.columns([1, 1])

# ---------------------------------------------------------
# LEFT PANEL: IMAGE
# ---------------------------------------------------------
with left:
    st.image(clean_bytes, use_column_width=True)

# ---------------------------------------------------------
# RIGHT PANEL: TABLE WITH ROW/COL NUMBERS
# ---------------------------------------------------------
with right:
    st.markdown("### 📋 Annotated Table (Preview)")

    # ---- COLUMN HEADER ----
    header_cols = st.columns(ncols + 1)  # extra column for row labels
    header_cols[0].markdown("**Row\\Col**")  # top-left blank/label

    for c in range(ncols):
        header_cols[c + 1].markdown(
            f"<div style='text-align:center; font-weight:700; font-size:18px;'>{c + 1}</div>",
            unsafe_allow_html=True,
        )

    # ---- ROWS WITH ROW NUMBERS ----
    for r in range(nrows):
        cols = st.columns(ncols + 1)

        # Row number on left
        cols[0].markdown(
            f"<div style='text-align:center; font-weight:700; font-size:18px;'>{r + 1}</div>",
            unsafe_allow_html=True,
        )

        # Cell values
        for c in range(ncols):
            label = grid[r][c]
            bgcolor = COLOR_MAP[label]

            cols[c + 1].markdown(
                f"""
                <div style="
                    border:1px solid #666;
                    padding:8px;
                    text-align:center;
                    border-radius:4px;
                    background:{bgcolor};
                    font-size:17px;
                    font-weight:600;
                ">
                    {label}
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("---")

# ---------------------------------------------------------
# BUTTONS (Back + Download ZIP)
# ---------------------------------------------------------
b1, b2 = st.columns(2)

with b1:
    if st.button("⬅ Back to Annotation", type="secondary"):
        st.switch_page("pages/4_Annotation_Grid.py")

with b2:
    # EXACT JSON STRUCTURE YOU PROVIDED
    json_data = {
        "saved_at": datetime.now().isoformat(),
        "metadata": meta,
        "annotation_grid": grid,
    }
    json_bytes = json.dumps(json_data, indent=2).encode()

    # CREATE ZIP IN MEMORY
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(f"{base_name}.json", json_bytes)
        zipf.writestr(f"{base_name}.png", clean_bytes)

    zip_buffer.seek(0)

    st.download_button(
        label="⬇️ Download Image + Annotation (ZIP)",
        data=zip_buffer,
        file_name=f"{base_name}.zip",
        mime="application/zip",
    )

# ---------------------------------------------------------
# RESET / START OVER
# ---------------------------------------------------------
if st.button("Start New Tray"):
    for key in list(st.session_state.keys()):
        st.session_state.pop(key, None)

    st.switch_page("pages/1_Upload_Image.py")
