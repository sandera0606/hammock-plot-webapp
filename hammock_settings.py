import streamlit as st
import numpy as np

from utils import (
    Defaults,
    plot,
    validate_expression,
    get_uni_type,
    set_snapshot_settings,
    set_default_settings,
    get_formatted_values,
)
import ast

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

def display_unibar_specific_settings(uni):
    st.subheader(":gray" + "[" + uni.replace("\n", " ") + "]", divider=True)
    type = get_uni_type(uni)

    st.badge(type)
    values = st.session_state.df[uni].dropna().unique()

    # treat values that are just 0 and 1 as categorical by default
    default_value_order = False
    desired_value_order = []
    if type == "numeric" and (np.array_equal(values, [0, 1]) or np.array_equal(values, [1, 0])):
        default_value_order = True
        desired_value_order = ["0", "1"]

    custom_value_order = st.checkbox("Custom label order?", key=f"value_order_{uni}", value=default_value_order)
    if custom_value_order and type == "numeric":
        st.warning("Warning: numeric variables will be treated as categorical variables")
        type = "categorical"
    
    if custom_value_order:
        options = get_formatted_values(values)
        value_order = st.multiselect(label="Custom label order", options=options, default=desired_value_order)

        if len(value_order) < len(options):
            st.error("Select all options to proceed.")

        st.session_state.value_order[uni] = value_order
    
    if type == "numeric":
        display_type = st.selectbox(label="display type", options=["box", "rugplot", "violin"], index=Defaults.DISPLAY_TYPE_INDEX, key=f"display_type_{uni}")
        use_custom_levels = st.checkbox(label="Custom label levels?", key=f"custom_levels_{uni}")
        if use_custom_levels:
            levels = st.number_input(label="Num. levels (0 for None)", min_value=0, step=1, value=7, key=f"number_input_{uni}")
            st.session_state.numerical_var_levels[uni] = levels
        st.session_state.numerical_display_type[uni] = display_type
    
    custom_labels = st.checkbox(label="Custom label options?", key=f"label_options_{uni}")
    if custom_labels:
        basic_customizations = st.checkbox(label="basic customizations only?", key=f"basic_labels_{uni}", value=True)
        if basic_customizations:
            subcolumns = st.columns(2)
            fontsize = subcolumns[0].number_input(label="fontsize", value=20.0, min_value=0.0, step=1.0, key=f"fontsize_{uni}")
            fontcolor = subcolumns[1].color_picker(label="color", value="#000000", key=f"fontcolor_{uni}")
            st.session_state.label_options[uni] = {"fontsize": fontsize, "color" : fontcolor}
        else:
            custom_options = st.text_input(label="custom options ([learn more](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html))")
            try:
                label_options = ast.literal_eval(custom_options)
                st.session_state.label_options[uni] = label_options
            except Exception as e:
                st.error("custom_options must be formatted as a dictionary")

if "df" not in st.session_state:
    st.write("Upload your data first")
    if st.button("Go back"):
        st.switch_page("upload_modify_df.py")
else:
    st.title("Hammock Plot Settings")
    st.write("View the Hammock plot documentation [here](%s)" % "https://github.com/TianchengY/hammock_plot/blob/main/README.md")

    st.sidebar.subheader("Your data")
    st.sidebar.dataframe(st.session_state.df, hide_index=True) # put the dataframe in the sidebar

    unibars = st.multiselect(label = "Which variables do you want to plot?", options=list(st.session_state.df))
    
    if unibars:
        st.header("Preset Setting Options")
        if "mode" not in st.session_state:
            st.session_state.mode = "hammock"
        cols = st.columns(6)
        if cols[0].button("Hammock", type="primary" if st.session_state["mode"] == "hammock" else "secondary"):
            st.session_state.mode = "hammock"
            set_default_settings()
            # st.session_state.reset_presets = True
            # st.rerun()

        if cols[1].button("Snapshot", type="primary" if st.session_state["mode"] == "snapshot" else "secondary"):
            st.session_state.mode = "snapshot"
            set_snapshot_settings()
            # st.session_state.reset_presets = True
            # st.rerun()

        st.header("Advanced Settings")
        
        # ------------ GENERAL SETTINGS ----------------------
        st.subheader("General")
        col1, col2 = st.columns([1, 1])
        with col1:
            subcol1, subcol2 = st.columns([1, 1])
            height = subcol1.number_input(label="Height", value=Defaults.HEIGHT, step=0.5, key=f"height_{st.session_state.reset_counter}")
            width = subcol2.number_input(label="Width of the plot", value=max(Defaults.WIDTH, len(unibars) * 4/3), step=0.5, key=f"width_{st.session_state.reset_counter}")

            subcol1, subcol2 = st.columns([1, 1])
            default_color = subcol1.color_picker(label="Default colour", value=Defaults.DEFAULT_COLOR, key=f"default_color_{st.session_state.reset_counter}")
            alpha = subcol2.slider(label="Opacity", value=Defaults.ALPHA, min_value=0, max_value=100, format="%d%%") / 100

            subcol1, subcol2 = st.columns([1, 1])
            label = subcol2.checkbox(label="Display labels?", value=True)
            unibar = subcol2.checkbox(label="Display unibars?", value=True)
            
            missing = subcol1.checkbox(label="Display missing values?")
            if missing:
                missing_placeholder = subcol1.text_input(label="Missing value placeholder", value="missing")
            
        
        with col2:
            min_bar_height = st.number_input(label="Minimum bar height", value=Defaults.MIN_BAR_HEIGHT, key=f"min_bar_height_{st.session_state.reset_counter}")
            subcol1, subcol2 = st.columns([1, 1])
            uni_vfill = subcol1.slider(label="Unibar Vertical Fill", key=f"uni_vfill_{st.session_state.reset_counter}", min_value=0, max_value=100, value=Defaults.uni_vfill,format="%d%%") / 100
            uni_hfill = subcol2.slider(label="Unibar Horizontal Fill", key=f"uni_hfill_{st.session_state.reset_counter}", min_value=0, max_value=100, value=Defaults.uni_hfill,format="%d%%") / 100
            if st.session_state["mode"] != "snapshot":
                connector_fraction = subcol1.slider(label="Connector Fraction", key=f"connect_frac_{st.session_state.reset_counter}", value=Defaults.CONNECTOR_FRACTION, min_value=0, max_value=100,format="%d%%") / 100
                custom_connector_color = subcol1.checkbox(label="Separate Connector Color?", key=f"custom_connect_color_{st.session_state.reset_counter}", value=False)
                shape = subcol2.selectbox(label="Connector Shape", key=f"shape_{st.session_state.reset_counter}", options=["rectangle", "parallelogram"])
                connector_color = None if not custom_connector_color else subcol2.color_picker(label="Connector color", value=Defaults.DEFAULT_COLOR, key=f"connect_color_{st.session_state.reset_counter}")
            else:
                connector_fraction = Defaults.CONNECTOR_FRACTION
                shape = "rectangle"
                connector_color = Defaults.DEFAULT_COLOR

        # ------ HIGHLIGHT SETTINGS ---------
        st.subheader("Highlight Settings")
        highlight = st.checkbox("Enable highlighting?")
        if highlight:
            hi_var = st.selectbox(label="Select the variable to highlight", options=list(st.session_state.df))
            col1, col2 = st.columns([1, 1])
            with col1:
                subcols = st.columns(2)
                hi_options = ["specific labels", "expression"]
                hi_type = subcols[0].radio("Highlight type", options=hi_options)
                hi_box = subcols[1].radio("Highlight box", options=["side-by-side", "stacked"])
                if hi_type == hi_options[0]: # highlighting specific labels
                    hi_value = st.multiselect(label="Select labels to highlight", options=(st.session_state.df[hi_var].dropna().unique()))
                else:
                    hi_value = st.text_input(label="Expression (regex/range) to highlight")
                    if hi_value != "" and not validate_expression(hi_value):
                        st.error("Must provide a valid expression (regex/range)")
                if missing:
                    hi_missing = st.checkbox("Highlight missing values?")
                else:
                    hi_missing = False
            with col2:
                num_highlight = len(hi_value) if hi_type == hi_options[0] else 1
                num_highlight += 1 if hi_missing else 0
                hi_colors = []
                cols = st.columns(3)  # create 3 columns

                for i in range(num_highlight):
                    col = cols[i % 3]  # rotate through the 3 columns
                    with col:
                        hi_colors.append(
                            st.color_picker(
                                label=f"Colour #{i+1}",
                                value=Defaults.HI_COLORS[i] if i < len(Defaults.HI_COLORS) else "#00ff00",
                                key = f"hi_colors_{i}_{st.session_state.reset_counter}",
                            )
                        )
                
                for color in hi_colors:
                    if color == default_color:
                        st.error("Warning! Default colour is same as a highlight colour")

        # ------ UNIBAR SPECIFIC SETTINGS ---------
        st.subheader("Unibar-Specific")
        # manage session_state variables
        st.session_state.numerical_var_levels = {}
        st.session_state.numerical_display_type = {}
        st.session_state.label_options = {}
        st.session_state.value_order = {}

        same_scale = st.multiselect(label="Variables to use same scale", options=unibars)
        same_scale_type = get_uni_type(same_scale[0]) if same_scale else None
        for uni in same_scale:
            if same_scale_type != get_uni_type(uni):
                st.error("Variables in same_scale must either all be numerical or all be categorical")
        cols = st.columns(2)
        violin_bw_method = cols[0].selectbox(label="violin plot bw method [(see matplotlib documentation)](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.violinplot.html)", options=["scott", "silverman", "custom float"])
        if violin_bw_method == "custom float":
            violin_bw_method = cols[1].number_input("custom float", min_value=0.0, value=0.5, step=0.1)

        num_rows = len(unibars) // 3 + 1
        grid = [st.columns(3) for row in range(num_rows)]
        for i in range(len(unibars)):
            row = i // 3
            col = i % 3
            square = grid[row][col]
            with square:
                display_unibar_specific_settings(unibars[i])
        
        # -------- PLOT GRAPH -----------
        if st.button("**Plot Hammock!**", type="primary", use_container_width=True):
            with st.spinner("Plotting hammock... this may take a while"):
                plot(
                    var=unibars,
                    value_order=st.session_state.value_order,
                    numerical_var_levels=st.session_state.numerical_var_levels,
                    numerical_display_type=st.session_state.numerical_display_type,
                    missing=missing,
                    missing_placeholder=missing_placeholder if missing else None,
                    label=label,
                    unibar=unibar,

                    hi_var=hi_var if highlight else None,
                    hi_value=hi_value if highlight else None,
                    hi_box=hi_box if highlight else None,
                    hi_missing=hi_missing if highlight else False,
                    colors=hi_colors if highlight else [],
                    default_color=default_color,
                    uni_vfill=uni_vfill,
                    connector_fraction=connector_fraction,
                    connector_color = connector_color,
                    uni_hfill=uni_hfill,
                    label_options=st.session_state.label_options,
                    height=height,
                    width=width,
                    min_bar_height=min_bar_height,
                    alpha=alpha,
                    shape=shape,
                    same_scale=same_scale,
                    violin_bw_method=violin_bw_method,
                )
    else:
        st.markdown(":gray[Select unibars to proceed]")
        

    if "fig" in st.session_state:
        if not unibars:
            del st.session_state["fig"]
            del st.session_state["buf"]
            st.rerun()
        st.header("Your plot")
        st.pyplot(st.session_state.fig) # display fig in streamlit
        st.download_button(
            label="Download as PNG",
            data=st.session_state.buf,
            file_name="my_plot.png",
            mime="image/png",
            icon=":material/download:",
        )
        if st.button("Clear plot"):
            del st.session_state["fig"]
            del st.session_state["buf"]
            st.rerun()