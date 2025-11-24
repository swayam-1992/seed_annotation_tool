# pages/2B_Define_Grid.py
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Define Grid", layout="wide")
st.markdown("<h3>STEP 3 – Add Grid Layer</h3>", unsafe_allow_html=True)

# Must have rotated image from Step 2A
if "rotated_image" not in st.session_state:
    st.error("Please complete Step 2A (Rotate) first!")
    if st.button("Back to Rotate"):
        st.switch_page("pages/2A_Rotate_Image.py")
    st.stop()

rotated = st.session_state.rotated_image.copy()
img_w, img_h = rotated.size

# ============================================================
# TWO-COLUMN LAYOUT
# ============================================================
left_col, right_col = st.columns([1.3, 1])

# ------------------------------------------------------------
# RIGHT COLUMN — SETTINGS PANEL
# ------------------------------------------------------------
with right_col:
    st.subheader("Grid Settings")
    c1, c2 = st.columns(2)
    rows = c1.number_input("Rows", 1, 50, 14, 1)
    cols = c2.number_input("Columns", 1, 50, 7, 1)

    c3, c4 = st.columns(2)
    color = c3.color_picker("Grid Color", "#00FF00")
    thickness = c4.slider("Line Thickness", 1, 10, 2)
    font_size = st.slider("Label Size", 8, 40, 18)

    st.markdown("---")
    st.subheader("Grid Position (Drag Sliders)")

    left_col_ui, right_col_ui = st.columns(2)
    x_pct = left_col_ui.slider("Left (%)", 0, 100, 5, 1)
    w_pct = right_col_ui.slider("Right (%)", 10, 200, 90, 1)

    top_col_ui, bottom_col_ui = st.columns(2)
    y_pct = top_col_ui.slider("Top (%)", 0, 100, 5, 1)
    h_pct = bottom_col_ui.slider("Bottom (%)", 10, 200, 90, 1)

# ------------------------------------------------------------
# GRID CALCULATIONS
# ------------------------------------------------------------
left = int(x_pct / 100 * img_w)
top = int(y_pct / 100 * img_h)
width = min(img_w - left, int(w_pct / 100 * img_w))
height = min(img_h - top, int(h_pct / 100 * img_h))
right = left + width
bottom = top + height

# ------------------------------------------------------------
# DRAW GRID
# ------------------------------------------------------------
result = rotated.copy()
draw = ImageDraw.Draw(result)

# Vertical lines
for i in range(1, cols):
    x = left + int(i * width / cols)
    draw.line([(x, top), (x, bottom)], fill=color, width=thickness)

# Horizontal lines
for r in range(1, rows):
    y = top + int(r * height / rows)
    draw.line([(left, y), (right, y)], fill=color, width=thickness)

# Outer border
draw.rectangle([left, top, right-1, bottom-1], outline=color, width=thickness+3)

# Labels
try:
    font = ImageFont.truetype("arial.ttf", font_size)
except:
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

cell_w, cell_h = width / cols, height / rows

for r in range(rows):
    for c in range(cols):
        x = left + c * cell_w + 4
        y = top + r * cell_h + 4
        label = f"[{r+1},{c+1}]"

        if hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0,0), label, font=font)
            w_box = bbox[2] - bbox[0]
            h_box = bbox[3] - bbox[1]
        else:
            w_box, h_box = draw.textsize(label, font=font)

        draw.rectangle([x-3, y-3, x+w_box+3, y+h_box+3], fill="white")
        draw.text((x, y), label, fill="black", font=font)

# ------------------------------------------------------------
# LEFT COLUMN — IMAGE PREVIEW
# ------------------------------------------------------------
with left_col:
    st.image(result, width=400, caption="Live Grid Preview")

# ------------------------------------------------------------
# SAVE BOTH VERSIONS & NEXT
# ------------------------------------------------------------
if st.button("Next → Metadata", type="primary", use_container_width=True):
    # Save the version WITH grid (for display in Step 3 & 4)
    st.session_state.gridded_image = result
    
    # Keep clean rotated image for final save
    st.session_state.final_grid_rows = rows
    st.session_state.final_grid_cols = cols
    st.session_state.grid_bounds = (left, top, right, bottom)

    st.success("Grid saved! Moving to metadata...")
    st.switch_page("pages/3_Metadata_Input.py")

st.info("Tip: Adjust sliders until grid perfectly matches your tray cavities.")
