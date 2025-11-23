# pages/3_Metadata_Input.py
import streamlit as st
from datetime import datetime
from PIL import Image
import PIL.ExifTags as ExifTags

st.set_page_config(layout="wide", page_title="Seed Tray Annotator")
st.markdown("<h3>STEP 3 – Capture & Tray Details</h3>", unsafe_allow_html=True)

# --------------------------------------------------------------
# Safety check – must have rotated image from Step 2A
# --------------------------------------------------------------
if "rotated_image" not in st.session_state:
    st.error("No image found! Please complete Step 2 (Rotate & Grid) first.")
    if st.button("← Back to Rotate Image"):
        st.switch_page("pages/2A_Rotate_Image.py")
    st.stop()

img = st.session_state.rotated_image  # Clean rotated image – NO grid overlay!

# --------------------------------------------------------------
# Try to extract capture date from EXIF
# --------------------------------------------------------------
def extract_exif_date(pil_image):
    try:
        exif = pil_image.getexif()
        if not exif:
            return None
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                try:
                    dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return dt.date()
                except:
                    return None
        return None
    except:
        return None

exif_date = extract_exif_date(img)

# --------------------------------------------------------------
# Layout: Image + Form
# --------------------------------------------------------------
col_img, col_form = st.columns([1, 1.3])

with col_img:
    st.image(img, caption="Your Seed Tray (Rotated – Ready for Annotation)", width=500)
    st.caption("This exact image will be saved (without grid lines)")

with col_form:
    st.header("Photograph & Tray Details")

    # ------------------------------
    # CAPTURE DATE
    # ------------------------------
    st.subheader("Capture Date")
    if exif_date:
        st.success(f"Auto-detected from photo: **{exif_date}**")
        capture_date = exif_date
        st.date_input("Date of Capture", value=capture_date, disabled=True)
    else:
        st.warning("No EXIF date found → Please enter manually")
        capture_date = st.date_input("Date of Capture", datetime.now().date())

    # ------------------------------
    # TRAY LAYOUT (read-only – from Step 2B)
    # ------------------------------
    st.subheader("Tray Layout")
    t1, t2, t3 = st.columns(3)
    with t1:
        nrows = st.number_input("Rows", 1, 200, st.session_state.final_grid_rows, disabled=True)
    with t2:
        ncols = st.number_input("Columns", 1, 200, st.session_state.final_grid_cols, disabled=True)
    with t3:
        shape = st.selectbox("Cavity Shape", ["Circle", "Square", "Hexagon", "Rectangle", "Other"])

    # ------------------------------
    # SEEDLING INFO
    # ------------------------------
    st.subheader("Seedling Details")
    s1, s2 = st.columns(2)
    with s1:
        crop = st.selectbox("Crop", [
            "Tomato", "Cucumber", "Pepper", "Eggplant", "Lettuce",
            "Cabbage", "Broccoli", "Cauliflower", "Onion", "Leek", "Other"
        ], index=0)
    with s2:
        sowing_date = st.date_input("Sowing Date", value=capture_date)

    # ------------------------------
    # Validation
    # ------------------------------
    if sowing_date >= capture_date:
        st.error("Sowing date must be **before** the capture date!")
        st.stop()

    days_after_sowing = (capture_date - sowing_date).days

    if days_after_sowing < 1:
        st.error("Age must be at least 1 day after sowing.")
        st.stop()

    st.success(f"Age at capture: **{days_after_sowing} days after sowing**")

    # ------------------------------
    # FINAL FILENAME PREVIEW (exactly what will be saved in Step 4)
    # ------------------------------
    st.subheader("Final Output Files (Step 4)")
    preview_timestamp = datetime.now().strftime("YYYYMMDD_HHMMSS")
    preview_name = f"{crop}_({days_after_sowing}d)_annotated_{preview_timestamp}"

    st.code(f"images/{preview_name}.png", language="text")
    st.code(f"annotations/{preview_name}.json", language="text")

    st.info(
        "These files will be created when you click **Next → Annotation Grid** "
        "and then **Save Final Annotation**."
    )

    # ------------------------------
    # Save metadata & proceed
    # ------------------------------
    if st.button("Next → Annotation Grid", type="primary", use_container_width=True):
        st.session_state.metadata = {
            "UID_legacy": f"{crop}_{capture_date.strftime('%y%m%d')}_{days_after_sowing}d",  # for backward compat
            "capture_date": capture_date.strftime("%Y-%m-%d"),
            "sowing_date": sowing_date.strftime("%Y-%m-%d"),
            "days_after_sowing": days_after_sowing,
            "crop": crop,
            "nrows": nrows,
            "ncols": ncols,
            "shape": shape,
        }

        # Ensure grid is initialized when entering Step 4
        if "grid" not in st.session_state:
            st.session_state.grid = [[1 for _ in range(ncols)] for _ in range(nrows)]

        st.switch_page("pages/4_Annotation_Grid.py")

# --------------------------------------------------------------
# Optional: Back button
# --------------------------------------------------------------
if st.button("← Back to Grid Positioning"):
    st.switch_page("pages/2B_Define_Grid.py")
