# pages/4_Annotation_Grid.py
import streamlit as st
import json
import os
import shutil
from datetime import datetime
import io

st.set_page_config(layout="wide", page_title="Cell Annotation")

# Safety check
if "metadata" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No tray data found! Complete previous steps first.")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start Over", use_container_width=True):
            st.switch_page("pages/1_Upload_Image.py")
    with c2:
        if st.button("Metadata", use_container_width=True):
            st.switch_page("pages/3_Metadata_Input.py")
    with c3:
        if st.button("Grid Setup", use_container_width=True):
            st.switch_page("pages/2B_Define_Grid.py")
    st.stop()

meta = st.session_state.metadata
clean_img = st.session_state.rotated_image
grid_img = st.session_state.get("gridded_image", clean_img)
nrows, ncols = meta["nrows"], meta["ncols"]

if "grid" not in st.session_state:
    st.session_state.grid = [[1 for _ in range(ncols)] for _ in range(nrows)]

grid = st.session_state.grid

st.markdown("<h3>STEP 4 – Annotate Each Cell</h3>", unsafe_allow_html=True)
st.markdown("**Click any cell to cycle: UG → G → A(S) → A(L) → A(D) → A(O) → UG...**")

# Legend
st.subheader("Annotation Legend")
legend_cols = st.columns(6)
labels = ["[G] Germinated", "[A(S)] Stunted", "[A(L)] Lanky", "[A(D)] Diseased", "[A(O)] Other", "[UG] Ungerminated"]
colors = ["#4dff4d", "#add8ff", "#5fb3ff", "#1e90ff", "#5f5fff", "#ff4d4d"]
for col, label, color in zip(legend_cols, labels, colors):
    with col:
        text_col = "black" if color in ["#4dff4d", "#add8ff", "#5fb3ff"] else "white"
        st.markdown(f"<span style='background:{color};color:{text_col};padding:10px 16px;border-radius:8px;font-weight:bold'>{label}</span>", unsafe_allow_html=True)

# Layout
col_img, col_grid = st.columns([1, 1])

with col_img:
    st.image(grid_img, caption="Reference Image (with Grid Overlay)", width=600)
    st.info("Final downloaded image will be **clean** (no grid lines)")

with col_grid:
    LABELS = {0: "UG", 1: "G", 2: "A(S)", 3: "A(L)", 4: "A(D)", 5: "A(O)"}

    html = f"""
    <style>
        .grid {{display:grid; grid-template-columns:70px repeat({ncols},1fr); gap:5px; background:#222; padding:15px; border-radius:12px;}}
        .header {{background:#333; color:#fff; text-align:center; padding:10px; border-radius:6px; font-weight:bold;}}
        .row-label {{background:#333; color:#fff; writing-mode:vertical-rl; text-orientation:mixed; padding:12px 4px; border-radius:6px; font-weight:bold;}}
        .cell {{text-align:center; cursor:pointer; font-weight:bold; border-radius:8px; padding:12px; transition:all .2s; user-select:none;}}
        .cell:hover {{opacity:0.85; transform:scale(1.05);}}
        .cell:active {{transform:scale(1.3);}}
        .c0 {{background:#ff4d4d; color:white;}}
        .c1 {{background:#4dff4d; color:black;}}
        .c2 {{background:#add8ff; color:black;}}
        .c3 {{background:#5fb3ff; color:black;}}
        .c4 {{background:#1e90ff; color:white;}}
        .c5 {{background:#5f5fff; color:white;}}
    </style>

    <div class="grid">
        <div></div>
    """
    for c in range(ncols):
        html += f"<div class='header'>C{c+1}</div>"
    for r in range(nrows):
        html += f"<div class='row-label'>R{r+1}</div>"
        for c in range(ncols):
            v = grid[r][c]
            html += f"<div class='cell c{v}' onclick='cycle({r},{c})'>{LABELS[v]}</div>"
    html += "</div>"

    js = """
    <script>
        let grid = GRID;
        const ROWS = NROWS, COLS = NCOLS;
        function cycle(r,c){
            let v = grid[r][c];
            v = (v + 1) % 6;
            grid[r][c] = v;
            const idx = r * COLS + c + ROWS;
            const cell = document.querySelectorAll('.cell')[idx - ROWS];
            if(cell){
                cell.className = 'cell c' + v;
                cell.innerText = ['UG','G','A(S)','A(L)','A(D)','A(O)'][v];
            }
            window.parent.postMessage({type:"streamlit:setComponentValue", value:{grid:grid}}, "*");
        }
    </script>
    """
    js = js.replace("GRID", json.dumps(grid)).replace("NROWS", str(nrows)).replace("NCOLS", str(ncols))
    value = st.components.v1.html(html + js, height=800, scrolling=True)
    if value and isinstance(value, dict) and "grid" in value:
        st.session_state.grid = value["grid"]

# Download Section
st.markdown("---")
st.markdown("### Download Your Final Results")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = f"{meta['crop']}_({meta['days_after_sowing']}d)_annotated_{timestamp}"

json_data = {
    "saved_at": datetime.now().isoformat(),
    "metadata": meta,
    "annotation_grid": st.session_state.grid
}
json_bytes = json.dumps(json_data, indent=2).encode('utf-8')

img_buffer = io.BytesIO()
clean_img.save(img_buffer, format="PNG")  # Clean image saved!
img_bytes = img_buffer.getvalue()

c1, c2 = st.columns(2)
with c1:
    st.download_button("Download Clean Image (.png)", data=img_bytes, file_name=f"{base_name}.png", mime="image/png", use_container_width=True)
with c2:
    st.download_button("Download Annotation (.json)", data=json_bytes, file_name=f"{base_name}.json", mime="application/json", use_container_width=True)

st.success("All done! Download both files above.")

if st.button("Finish & Start New Tray", type="secondary", use_container_width=True):
    for key in ["original_image","rotated_image","gridded_image","processed_image","metadata","grid","final_grid_rows","final_grid_cols","final_rotation","image_path","grid_bounds"]:
        st.session_state.pop(key, None)
    if os.path.exists("temp_uploads"):
        shutil.rmtree("temp_uploads")
        os.makedirs("temp_uploads", exist_ok=True)
    st.success("Cleared! Starting fresh...")
    st.rerun()
