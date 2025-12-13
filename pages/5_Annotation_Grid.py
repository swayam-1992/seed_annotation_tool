# pages/5_Annotation_Grid.py
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Annotation Grid", layout="wide")
st.markdown("<h2 style='text-align: center;'>STEP 5 – Annotate Seedlings (Click Expanded Cells)</h2>", unsafe_allow_html=True)
st.markdown("**Annotation Cycle:** Click anywhere on the expanded view → **G → A → UG → G** (center cell only)")

# ------------------------------------------------------------------
# Safety check
# ------------------------------------------------------------------
if "warped_rgb" not in st.session_state:
    st.error("No corrected image found! Please complete previous steps.")
    if st.button("← Back to Metadata"):
        st.switch_page("pages/4_Metadata_Input.py")
    st.stop()

# Load final corrected image
full_img = Image.fromarray(st.session_state.warped_rgb)
W, H = full_img.size

# Grid settings from metadata
nrows = st.session_state.metadata.get("nrows", 14)
ncols = st.session_state.metadata.get("ncols", 7)

# Total padded grid: 16×9
TOTAL_ROWS, TOTAL_COLS = 16, 9
cell_w = W // TOTAL_COLS
cell_h = H // TOTAL_ROWS

# Crop inner 14×7 region
inner_img = full_img.crop((
    cell_w,           # skip left buffer
    cell_h,           # skip top buffer
    W - cell_w,
    H - cell_h
))
inner_W, inner_H = inner_img.size
cell_w_inner = inner_W // ncols
cell_h_inner = inner_H // nrows

# ------------------------------------------------------------------
# Initialize annotation grid
# ------------------------------------------------------------------
if "grid" not in st.session_state:
    st.session_state.grid = [["G" for _ in range(ncols)] for _ in range(nrows)]

grid = st.session_state.grid

# Annotation cycle
cycle = {"G": "A", "A": "UG", "UG": "G"}

# Color mapping for badge
status_colors = {"G": "lightgreen", "A": "lightblue", "UG": "lightcoral"}

# ------------------------------------------------------------------
# Helper: get single small cell
# ------------------------------------------------------------------
def get_small_cell(r, c):
    left = c * cell_w_inner
    top = r * cell_h_inner
    return inner_img.crop((left, top, left + cell_w_inner, top + cell_h_inner))

# ------------------------------------------------------------------
# Helper: create expanded 3x3 view with single thick yellow border
# ------------------------------------------------------------------
def create_expanded_view(center_r, center_c):
    canvas_w = 3 * cell_w_inner
    canvas_h = 3 * cell_h_inner + 60
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 24)  # smaller font for labels
    except:
        font = ImageFont.load_default()

    # Paste all 9 cells first
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r = center_r + dr
            c = center_c + dc
            if 0 <= r < nrows and 0 <= c < ncols:
                cell = get_small_cell(r, c)
                label = grid[r][c]
            else:
                cell = Image.new("RGB", (cell_w_inner, cell_h_inner), (230, 230, 230))
                label = "-"

            x = (dc + 1) * cell_w_inner
            y = (dr + 1) * cell_h_inner + 60

            canvas.paste(cell, (x, y))

            # Only show the label for the CENTER cell (smaller)
            if dr == 0 and dc == 0:
                draw.text((x + (cell_w_inner - 30)//2, y - 48), label, fill="black", font=font)

    # Draw SINGLE thick yellow border on center AFTER pasting (so it's fully visible)
    dc, dr = 1, 1  # center position in 3x3
    x = dc * cell_w_inner
    y = dr * cell_h_inner + 60
    border_width = 9

    draw.rectangle(
        [x - border_width, y - border_width,
         x + cell_w_inner + border_width - 1, y + cell_h_inner + border_width - 1],
        outline=(255, 255, 0),  # bright yellow
        width=border_width
    )

    return canvas

# ------------------------------------------------------------------
# Main Grid: Show expanded views
# ------------------------------------------------------------------
st.markdown("### 14×7 Expanded Annotation Grid (3×3 Context)")

for r in range(nrows):
    cols = st.columns(ncols)
    for c in range(ncols):
        with cols[c]:
            expanded_img = create_expanded_view(r, c)
            current_label = grid[r][c]

            caption = f"**R{r+1} C{c+1}** → {current_label} (Click to cycle)"

            if st.button(" ", key=f"edit_{r}_{c}", use_container_width=True):
                grid[r][c] = cycle[current_label]
                st.rerun()

            st.image(expanded_img, caption=caption, use_container_width=True)

            # Smaller, cleaner status badge
            st.markdown(
                f"<div style='text-align:center; font-size:1.2rem; font-weight:bold; color:white; background:{status_colors[current_label]}; border-radius:8px; padding:4px; margin:4px 0;'>"
                f"{current_label}</div>",
                unsafe_allow_html=True
            )

# ------------------------------------------------------------------
# Navigation
# ------------------------------------------------------------------
st.markdown("---")
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_left:
    if st.button("← Back to Metadata"):
        st.switch_page("pages/4_Metadata_Input.py")

with col_right:
    if st.button("Next → Export Results", type="primary"):
        st.session_state.final_grid = grid.copy()
        st.switch_page("pages/6_Export.py")