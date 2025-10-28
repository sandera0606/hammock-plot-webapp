import streamlit as st
import pandas as pd

@st.dialog("Choose Column to Rename")
def rename_column():
    df = st.session_state.df
    column_to_rename = st.selectbox("Rename Column:", list(df.columns))
    new_name = st.text_input("As:")

    if st.button("Rename Column"):
        # Get the column order
        cols = list(df.columns)
        idx = cols.index(column_to_rename)
        # Replace the old column name with the new one in the same position
        cols[idx] = new_name
        # Rename and reorder
        df = df.rename(columns={column_to_rename: new_name})[cols]
        # Save back to session state
        st.session_state.df = df
        st.rerun()

@st.dialog("Choose Labels to Replace")
def replace_column_values():
    col =  st.selectbox(label="Replace labels from column:", options=list(st.session_state.df))
    old_name = st.selectbox("Replace:", options=list(st.session_state.df[col].unique()) if col else [])
    new_name = st.text_input("With:")
    if st.button("Replace All"):
        st.session_state.df[col] = st.session_state.df[col].replace(old_name, new_name)
        st.rerun()

if "df" not in st.session_state:
    uploaded_file = st.file_uploader(
        label="Upload your data to get started",
        type=["csv"] # add anything else that may be accepted (dta?)
    )
    if uploaded_file is not None:
        # Read the CSV into a pandas DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Store the DataFrame in session_state
        st.session_state.df = df
        st.rerun()
else:
    st.badge("Tools", icon=":material/build:", color="grey")

    if st.button("Rename Column"):
        rename_column()

    if st.button("Replace Labels"):
        replace_column_values()

    st.dataframe(st.session_state.df)

    col1, col2, col3 = st.columns([1, 1, 3])

    # allow user to clear data
    with col1:
        st.download_button(
            label="Save Local",
            data=st.session_state.df.to_csv().encode("utf-8"),
            file_name="hammock-plot-data.csv",
            mime="text/csv",
            icon=":material/download:",
        )

    with col2:
        if st.button("Clear data"):
            del st.session_state["df"]
            st.rerun()