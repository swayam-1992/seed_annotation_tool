# pages/4_Metadata_Input.py
import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import PIL.ExifTags as ExifTags

st.set_page_config(layout="wide", page_title="Seed Tray Annotator")

# ---------------------------------------------------------
# Clean layout styling
# ---------------------------------------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3>STEP 4 – Photograph & Tray Details</h3>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Safety check: Must have perspective-corrected image
# ---------------------------------------------------------
if "warped_rgb" not in st.session_state:
    st.error("No corrected image found! Please complete Perspective Correction first.")
    if st.button("Back to Perspective Correction"):
        st.switch_page("pages/3_Perspective_Correction.py")
    st.stop()

# Final corrected image (RGB PIL Image)
img_display = Image.fromarray(st.session_state.warped_rgb)

# ---------------------------------------------------------
# Try to read EXIF date from the ORIGINAL uploaded image (warping removes EXIF)
# ---------------------------------------------------------
def extract_exif_date_from_original():
    if "original_image" in st.session_state:
        try:
            exif = st.session_state.original_image.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S").date()
        except Exception:
            pass
    return None

exif_date = extract_exif_date_from_original()

# ---------------------------------------------------------
# Main layout: image + form
# ---------------------------------------------------------
col_img, col_form = st.columns([1, 1.2], gap="large")

with col_img:
    st.image(img_display, caption="Final Corrected Seed Tray – Ready for Annotation", use_container_width=True)

with col_form:
    st.subheader("Date of Photograph Capture")
    if exif_date:
        st.success(f"Auto-detected from original photo: **{exif_date}**")
        capture_date = st.date_input("Capture Date", value=exif_date, key="capture_auto")
    else:
        st.warning("No EXIF date found → Please enter manually")
        capture_date = st.date_input("Capture Date", value=datetime.today().date(), key="capture_manual")

    st.subheader("Tray Layout")
    t1, t2 = st.columns(2)
    with t1:
        nrows = st.number_input("Rows", min_value=1, value=14, step=1)
    with t2:
        ncols = st.number_input("Columns", min_value=1, value=7, step=1)

    shape = st.selectbox("Cavity Shape", ["Circle", "Square", "Rectangle", "Hexagon", "Other"])

    st.subheader("Seedling Details")
    s1, s2 = st.columns(2)
    with s1:
        crop = st.selectbox(
            "Crop",
            ["Tomato", "Cucumber", "Hot Pepper", "Cabbage", "Lettuce", "Eggplant", "Other"],
            index=0
        )
    with s2:
        # Default sowing date = 14 days before capture
        default_sowing = capture_date - timedelta(days=14)
        sowing_date = st.date_input("Date of Sowing", value=default_sowing)

    # -----------------------------------------------------
    # Validations
    # -----------------------------------------------------
    if sowing_date >= capture_date:
        st.error("Sowing date must be BEFORE the capture date!")
        st.stop()

    days_after_sowing = (capture_date - sowing_date).days
    if days_after_sowing < 1:
        st.error("Seedlings must be at least 1 day old.")
        st.stop()

    st.success(f"Age at capture: **{days_after_sowing} days after sowing**")

    # -----------------------------------------------------
    # Output filename preview
    # -----------------------------------------------------
    st.subheader("Final Output Files (Preview)")
    timestamp = capture_date.strftime("%Y%m%d")
    filename_base = f"{crop}_{days_after_sowing}d_{timestamp}"
    st.code(f"images/{filename_base}_annotated.png")
    st.code(f"annotations/{filename_base}.json")

    # -----------------------------------------------------
    # Save everything and go to annotation grid
    # -----------------------------------------------------
    if st.button("Next → Start Annotation Grid", type="primary", use_container_width=True):
        st.session_state.metadata = {
            "capture_date": capture_date.strftime("%Y-%m-%d"),
            "sowing_date": sowing_date.strftime("%Y-%m-%d"),
            "days_after_sowing": days_after_sowing,
            "crop": crop,
            "nrows": int(nrows),
            "ncols": int(ncols),
            "shape": shape,
            "filename_base": filename_base,
        }

        # Initialize empty annotation grid (G = Germinated/Healthy by default)
        st.session_state.grid = [["G" for _ in range(int(ncols))] for _ in range(int(nrows))]

        # Change this to whatever your next page is called
        st.switch_page("pages/5_Annotation_Grid.py")
