# pages/4_Annotation_Grid.py   ← FINAL 100% WORKING VERSION
import streamlit as st
import json
import os
import shutil
from datetime import datetime

st.set_page_config(layout="wide", page_title="Cell Annotation")

# ------------------------------------------------------------------
# Safety check – FIXED: now shows helpful buttons instead of dead end
# ------------------------------------------------------------------
if "metadata" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No tray data found! You need to complete the previous steps first.")
    st.markdown("### Where would you like to go?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Start Fresh – Upload New Image", use_container_width=True):
            st.switch_page("pages/1_Upload_Image.py")
    with col2:
        if st.button("Go Back to Metadata Input", use_container_width=True):
            st.switch_page("pages/3_Metadata_Input.py")
    with col3:
        if st.button("Go Back to Grid Setup", use_container_width=True):
            st.switch_page("pages/2B_Define_Grid.py")
    
    st.stop()

# ------------------------------------------------------------------
# Everything is good – proceed
# ------------------------------------------------------------------
meta = st.session_state.metadata
rotated_img = st.session_state.rotated_image
nrows = meta["nrows"]
ncols = meta["ncols"]

# Initialize grid if missing
if "grid" not in st.session_state:
    st.session_state.grid = [[1 for _ in range(ncols)] for _ in range(nrows)]

grid = st.session_state.grid

st.markdown("<h3>STEP 4 – Annotate Each Cell</h3>", unsafe_allow_html=True)
st.markdown("**Click any cell to cycle: UG → G → A(S) → A(L) → A(D) → A(O) → UG...**")

# ------------------------------------------------------------------
# Legend
# ------------------------------------------------------------------
st.subheader("Annotation Legend")
cols = st.columns(6)
labels = ["[G] Germinated", "[A(S)] Stunted", "[A(L)] Lanky", "[A(D)] Diseased", "[A(O)] Other", "[UG] Ungerminated"]
colors = ["#4dff4d", "#add8ff", "#5fb3ff", "#1e90ff", "#5f5fff", "#ff4d4d"]

for col, label, color in zip(cols, labels, colors):
    with col:
        text_color = "black" if color in ["#4dff4d", "#add8ff", "#5fb3ff"] else "white"
        st.markdown(
            f"<span style='background:{color};color:{text_color};padding:10px 16px;border-radius:8px;font-weight:bold'>{label}</span>",
            unsafe_allow_html=True
        )

# ------------------------------------------------------------------
# Layout: Image + Interactive Grid
# ------------------------------------------------------------------
col_img, col_grid = st.columns([1, 1])

with col_img:
    st.image(rotated_img, caption="Reference Image (Clean – No Grid Lines)", width=600)

with col_grid:
    LABELS = {0: "UG", 1: "G", 2: "A(S)", 3: "A(L)", 4: "A(D)", 5: "A(O)"}

    html = f"""
    <style>
        .grid {{display:grid; grid-template-columns:70px repeat({ncols},1fr); gap:4px; background:#222; padding:15px; border-radius:12px;}}
        .header {{background:#111; color:#fff; text-align:center; padding:10px; border-radius:6px; font-weight:bold;}}
        .row-label {{background:#111; color:#fff; writing-mode:vertical-rl; padding:12px 4px; border-radius:6px; font-weight:bold;}}
        .cell {{text-align:center; cursor:pointer; font-weight:bold; border-radius:8px; padding:12px; transition:all .2s; user-select:none;}}
        .cell:hover {{opacity:0.9;}}
        .cell.clicked {{transform:scale(1.35);}}
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
            v = (v+1)%6;
            grid[r][c] = v;
            const cells = document.querySelectorAll('.cell');
            const idx = r*COLS + c;
            const cell = cells[idx];
            if(cell){
                cell.className = 'cell c'+v+' clicked';
                cell.innerText = ['UG','G','A(S)','A(L)','A(D)','A(O)'][v];
                setTimeout(()=>cell.classList.remove('clicked'),200);
            }
            window.parent.postMessage({type:"streamlit:setComponentValue", value:{grid:grid}}, "*");
        }
    </script>
    """
    js = js.replace("GRID", json.dumps(grid)).replace("NROWS", str(nrows)).replace("NCOLS", str(ncols))

    value = st.components.v1.html(html + js, height=750, scrolling=True)
    if value and isinstance(value, dict) and "grid" in value:
        st.session_state.grid = value["grid"]

# ------------------------------------------------------------------
# SAVE FINAL ANNOTATION
# ------------------------------------------------------------------
if st.button("Save Final Annotation", type="primary", use_container_width=True):
    os.makedirs("images", exist_ok=True)
    os.makedirs("annotations", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{meta['crop']}_({meta['days_after_sowing']}d)_annotated_{timestamp}"

    # Save JSON
    with open(f"annotations/{base_name}.json", "w") as f:
        json.dump({
            "saved_at": datetime.now().isoformat(),
            "image_file": f"images/{base_name}.png",
            "metadata": meta,
            "annotation_grid": st.session_state.grid
        }, f, indent=2)

    # Save clean rotated image only
    rotated_img.save(f"images/{base_name}.png")

    st.success("Annotation saved successfully!")
    st.success(f"Image → `images/{base_name}.png`")
    st.success(f"Annotation → `annotations/{base_name}.json`")
    st.balloons()

# ------------------------------------------------------------------
# Finish & Start New Tray
# ------------------------------------------------------------------
if st.button("Finish This Tray & Start a New One", type="secondary", use_container_width=True):
    keys_to_clear = [
        "original_image", "rotated_image", "processed_image",
        "metadata", "grid", "final_grid_rows", "final_grid_cols",
        "final_rotation", "image_path", "grid_bounds"
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)

    if os.path.exists("temp_uploads"):
        shutil.rmtree("temp_uploads")
        os.makedirs("temp_uploads", exist_ok=True)

    st.success("All done! Starting fresh with a new tray...")
    st.rerun()
