# pages/4_Annotation_Grid.py
import streamlit as st
import io   # ← This was missing!

st.set_page_config(layout="wide", page_title="Cell Annotation")

# ---------------------------------------------------------
# CSS – Beautiful colored clickable cells
# ---------------------------------------------------------
st.markdown("""
<style>
.cell {
    width: 100%;
    height: 62px;
    font-size: 20px;
    font-weight: bold;
    border: 3px solid #333;
    border-radius: 10px;
    margin: 4px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}
.cell:hover { transform: scale(1.07); box-shadow: 0 8px 16px rgba(0,0,0,0.3); }

.G  { background-color: #ccffcc; color: #006000; }
.UG { background-color: #ffcccc; color: #800000; }
.A  { background-color: #ccccff; color: #000080; }

.header {
    background: #333 !important;
    color: white !important;
    font-weight: bold;
    font-size: 18px;
    text-align: center;
    padding: 14px 0;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Safety + Data
# ---------------------------------------------------------
if "metadata" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No tray data found! Complete previous steps first.")
    st.stop()

meta = st.session_state.metadata
clean_img = st.session_state.rotated_image
nrows, ncols = meta["nrows"], meta["ncols"]

# Initialize grid
if "grid" not in st.session_state:
    st.session_state.grid = [["G" for _ in range(ncols)] for _ in range(nrows)]

# Convert old integer format if needed
for r in range(nrows):
    for c in range(ncols):
        if isinstance(st.session_state.grid[r][c], int):
            st.session_state.grid[r][c] = {0: "UG", 1: "G", 2: "A"}.get(st.session_state.grid[r][c], "G")

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.markdown("<h3>STEP 4 – Click to Annotate</h3>", unsafe_allow_html=True)
st.markdown("**Green = G Red = UG Blue = A**  (click cycles: G → A → UG → G)")

left, right = st.columns([1, 1.15])

with left:
    st.image(clean_img, use_container_width=True)
    st.image(clean_img, use_container_width=True)

with right:
    # Column headers
    hcols = st.columns([0.25] + [1]*ncols)
    hcols[0].markdown('<div class="header">Row</div>', unsafe_allow_html=True)
    for c in range(ncols):
        hcols[c+1].markdown(f'<div class="header">{c+1}</div>', unsafe_allow_html=True)

    # Grid
    for r in range(nrows):
        cols = st.columns([0.25] + [1]*ncols)
        cols[0].markdown(f'<div class="header">{r+1}</div>', unsafe_allow_html=True)

        for c in range(ncols):
            current = st.session_state.grid[r][c]
            cycle = {"G": "A", "A": "UG", "UG": "G"}
            next_val = cycle[current]

            with cols[c+1]:
                if st.button(" ", key=f"btn_{r}_{c}", use_container_width=True):
                    st.session_state.grid[r][c] = next_val
                    st.rerun()

                # Pure HTML colored cell — always correct color
                st.markdown(
                    f'<div class="cell {current}">{current}</div>',
                    unsafe_allow_html=True
                )

# ---------------------------------------------------------
# Next Page Button
# ---------------------------------------------------------
st.markdown("---")
if st.button("Preview & Download", type="primary", use_container_width=True):
    st.session_state.annotation_final = [row[:] for row in st.session_state.grid]
    
    buf = io.BytesIO()                    # Now works!
    clean_img.save(buf, format="PNG")
    st.session_state.clean_bytes = buf.getvalue()
    
    st.switch_page("pages/5_Preview_Annotation.py")