# app.py
import streamlit as st

st.set_page_config(page_title="Seed Tray Annotation Tool", layout="centered")

st.title("Seed Tray Annotation Tool")
st.markdown("""
### Perform and save your annotation in 5 STEPS
""")

if st.button("Next ➜"):
    st.switch_page("pages/1_Upload_Image.py")

# ----------------------------------------------------
# IMPORTANT FOR DESKTOP EXECUTABLE
# ----------------------------------------------------
if __name__ == "__main__":
    import os
    # Launch Streamlit app from inside PyInstaller bundle
    os.system("streamlit run app.py --server.headless true")
