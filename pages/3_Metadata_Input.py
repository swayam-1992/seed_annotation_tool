# pages/3_Metadata_Input.py
import streamlit as st
from datetime import datetime
from PIL import Image
import PIL.ExifTags as ExifTags

st.set_page_config(layout="wide", page_title="Seed Tray Annotator")
st.markdown("<h3>STEP 4 – Photograph & Tray Details</h3>", unsafe_allow_html=True)

# Safety check
if "rotated_image" not in st.session_state:
    st.error("No image found! Please complete Step 2 first.")
    if st.button("Back to Rotate Image"):
        st.switch_page("pages/2A_Rotate_Image.py")
    st.stop()

img_clean = st.session_state.rotated_image
img_display = st.session_state.get("gridded_image", img_clean)  # Show gridded if available

# EXIF date extraction
def extract_exif_date(pil_image):
    try:
        exif = pil_image.getexif()
        if not exif: return None
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                try:
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").date()
                except:
                    return None
        return None
    except:
        return None

exif_date = extract_exif_date(img_clean)

# Layout
col_img, col_form = st.columns([1, 1.3])

with col_img:
    st.image(img_display, caption="Your Seed Tray (with Grid Overlay)", width=550)
    st.caption("Final saved image will be **clean** (no grid lines)")

with col_form:
    #st.header("Photograph & Tray Details")

    st.subheader("Date of photograph capture")
    if exif_date:
        st.success(f"Auto-detected: **{exif_date}**")
        capture_date = exif_date
        st.date_input("Date of Capture", value=capture_date, disabled=True)
    else:
        st.warning("No EXIF date → Enter manually")
        capture_date = st.date_input("Date of Capture", datetime.now().date())

    st.subheader("Tray Layout")
    t1, t2, t3 = st.columns(3)
    with t1:
        nrows = st.number_input("Rows", value=st.session_state.final_grid_rows, disabled=True)
    with t2:
        ncols = st.number_input("Columns", value=st.session_state.final_grid_cols, disabled=True)
    with t3:
        shape = st.selectbox("Cavity Shape", ["Circle", "Square", "Hexagon", "Rectangle", "Other"])

    st.subheader("Seedling Details")
    s1, s2 = st.columns(2)
    with s1:
        crop = st.selectbox("Crop", [
            "Cucumber", "Hot Pepper", "Tomato",
            "Cabbage", "Other"
        ])
    with s2:
        sowing_date = st.date_input("Date of sowing", value=capture_date)

    if sowing_date >= capture_date:
        st.error("Sowing date must be **before** capture date!")
        st.stop()

    days_after_sowing = (capture_date - sowing_date).days
    if days_after_sowing < 1:
        st.error("Seedlings must be at least 1 day old.")
        st.stop()

    st.success(f"Age at capture: **{days_after_sowing} days after sowing**")

    st.subheader("Final Output Files")
    preview_name = f"{crop}_({days_after_sowing}d)_annotated_YYYYMMDD_HHMMSS"
    st.code(f"images/{preview_name}.png", language="text")
    st.code(f"annotations/{preview_name}.json", language="text")

    if st.button("Next → Annotation Grid", type="primary", use_container_width=True):
        st.session_state.metadata = {
            "UID_legacy": f"{crop}_{capture_date.strftime('%y%m%d')}_{days_after_sowing}d",
            "capture_date": capture_date.strftime("%Y-%m-%d"),
            "sowing_date": sowing_date.strftime("%Y-%m-%d"),
            "days_after_sowing": days_after_sowing,
            "crop": crop,
            "nrows": nrows,
            "ncols": ncols,
            "shape": shape,
        }

        if "grid" not in st.session_state:
            st.session_state.grid = [[1 for _ in range(ncols)] for _ in range(nrows)]

        st.switch_page("pages/4_Annotation_Grid.py")

if st.button("Back to Grid Positioning"):
    st.switch_page("pages/2B_Define_Grid.py")
