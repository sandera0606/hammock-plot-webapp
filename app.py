import streamlit as st

pages = [
    st.Page("upload_modify_df.py", title="Upload/Modify Your Data"),
    st.Page("hammock_settings.py", title="Hammock Plot Settings"),
]

pg = st.navigation(pages)

pg.run()