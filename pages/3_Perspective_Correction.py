# pages/3_Perspective_Correction.py
import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# ============================================================
# NEW: Perspective correction logic with buffer
# ============================================================
def four_point_transform_with_buffer(img, pts):
    pts = np.array(pts, dtype="float32")
    tl, tr, br, bl = pts

    # Estimate width/height based on opposite sides
    wA = np.linalg.norm(br - bl)
    wB = np.linalg.norm(tr - tl)
    hA = np.linalg.norm(tr - br)
    hB = np.linalg.norm(tl - bl)

    rawW, rawH = int(max(wA, wB)), int(max(hA, hB))

    # Add uniform padding (same logic as batch script)
    top_buffer    = rawH // 14
    bottom_buffer = rawH // 14
    left_buffer   = rawW // 7
    right_buffer  = rawW // 7

    finalW = rawW + left_buffer + right_buffer
    finalH = rawH + top_buffer + bottom_buffer

    # Target coordinates after warping
    dst = np.array([
        [left_buffer,            top_buffer],
        [left_buffer + rawW - 1, top_buffer],
        [left_buffer + rawW - 1, top_buffer + rawH - 1],
        [left_buffer,            top_buffer + rawH - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (finalW, finalH))
    return warped


# ============================================================
# UI SECTION
# ============================================================
st.title("STEP 3 - Perspective Correction")
st.markdown("---")

# ------------------------------------------------------------------
# Safety check
# ------------------------------------------------------------------
if "rotated_bgr" not in st.session_state or "rotated_image" not in st.session_state:
    st.error("No rotated image found. Please go back to Rotate.")
    if st.button("Back to Rotate"):
        st.switch_page("pages/2_Rotate_Image.py")
    st.stop()

img_bgr = st.session_state.rotated_bgr.copy()
pil_img = st.session_state.rotated_image.copy()

if "points" not in st.session_state:
    st.session_state.points = []

# ------------------------------------------------------------------
# Point selection UI (unchanged)
# ------------------------------------------------------------------
MAX_DISPLAY_WIDTH = 800
orig_w, orig_h = pil_img.size
scale = min(MAX_DISPLAY_WIDTH / orig_w, 1.0)
display_img = pil_img.copy()
if scale < 1:
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    display_img = display_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

display_np = np.array(display_img)

# Draw already-clicked points
for i, (x_orig, y_orig) in enumerate(st.session_state.points):
    x = int(x_orig * scale)
    y = int(y_orig * scale)
    cv2.circle(display_np, (x, y), 20, (0, 100, 255), -1)
    cv2.circle(display_np, (x, y), 26, (255, 255, 255), 6)
    cv2.putText(display_np, str(i+1), (x+30, y-20),
                cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 5)
    cv2.putText(display_np, str(i+1), (x+30, y-20),
                cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 0, 0), 2)

# Collect 4 points
if len(st.session_state.points) < 4:
    st.info("Click the four corners in this order: **Top-Left → Top-Right → Bottom-Right → Bottom-Left**")
    value = streamlit_image_coordinates(display_np, key="pts")
    if value:
        x = int(value["x"] / scale)
        y = int(value["y"] / scale)

        # Avoid duplicate clicks
        if not st.session_state.points or (x, y) != st.session_state.points[-1]:
            st.session_state.points.append((x, y))
            st.rerun()

st.image(display_np, caption="Click corners in order", use_container_width=True)

# ------------------------------------------------------------------
# When 4 points are selected → try warping using new logic
# ------------------------------------------------------------------
if len(st.session_state.points) == 4:
    pts = np.array(st.session_state.points, dtype="float32")

    # Try transform matrix first (for point sanity)
    try:
        dst_dummy = np.array([[0,0],[100,0],[100,200],[0,200]], dtype="float32")
        _ = cv2.getPerspectiveTransform(pts, dst_dummy)
    except cv2.error:
        st.error("Invalid points – they are collinear or too close. Please select again.")
        if st.button("Reset points"):
            st.session_state.points = []
            st.rerun()
        st.stop()

    # Actual warp using NEW logic
    with st.spinner("Applying perspective correction..."):
        try:
            warped_bgr = four_point_transform_with_buffer(img_bgr, st.session_state.points)
            warped_rgb = cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2RGB)

            st.session_state.warped_bgr = warped_bgr
            st.session_state.warped_rgb = warped_rgb

            st.success("Perspective correction successful!")
        except Exception as e:
            st.error(f"Warping failed: {e}")
            st.stop()

    # Preview
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.image(pil_img, caption="Rotated", width=400)
    with col2:
        st.image(warped_rgb, caption="Corrected & Ready", width=400)

    if st.button("Redo Perspective Correction", type="secondary"):
        st.session_state.points = []
        for key in ["warped_bgr", "warped_rgb"]:
            st.session_state.pop(key, None)
        st.rerun()


# ------------------------------------------------------------------
# Navigation
# ------------------------------------------------------------------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("← Back to Rotate"):
        st.switch_page("pages/2_Rotate_Image.py")

with col3:
    if st.button("Next →", type="primary"):  # Placeholder for next page
        st.switch_page("pages/4_Metadata_Input.py")  # Uncomment and adjust when next page is ready
        
