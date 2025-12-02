import streamlit as st
import numpy as np
from streamlit_adjustable_columns import adjustable_columns

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

if "run_plot_soon" not in st.session_state:
    st.session_state.run_plot_soon = False

if "unibars" not in st.session_state:
    st.session_state.unibars = []

if "missing" not in st.session_state:
    st.session_state.missing = False

if "mode" not in st.session_state:
    st.session_state.mode = "hammock"

def run_plot_on_refresh():
    if not st.session_state.run_plot_soon:
        st.session_state.run_plot_soon = True

def display_unibar_specific_settings(uni):
    st.markdown(
        f"""
        <h3 style="
            text-decoration: underline;
            color:#67a4c6ff;
            margin-top: 0.5rem;
        ">
            {uni.replace(chr(10), ' ').replace('_', ' ')}
        </h3>
        """,
        unsafe_allow_html=True
    )
    type = get_uni_type(uni)

    st.badge(type)
    values = st.session_state.df[uni].dropna().unique()

    # treat values that are just 0 and 1 as categorical by default
    default_value_order = False
    desired_value_order = []

    if type != "numeric":
        st.checkbox(label="Categorical", value=True, disabled=True, key=f"categorical_{uni}")

    if type == "numeric":
        force_categorical = False
        if (np.array_equal(values, [0, 1]) or np.array_equal(values, [1, 0])):
            force_categorical = True
        force_categorical = st.checkbox(label="Categorical", value=force_categorical, key=f"force_categorical_{uni}")
        if force_categorical:
            desired_value_order = get_formatted_values(values)
            st.session_state.value_order[uni] = desired_value_order
            type = "categorical"

    
        if type == "numeric":
            use_custom_levels = st.checkbox(label="Custom label levels?", key=f"custom_levels_{uni}")
            if use_custom_levels:
                levels = st.number_input(label="Num. levels (0 for None)", min_value=0, step=1, value=7, key=f"number_input_{uni}")
                st.session_state.numerical_var_levels[uni] = levels 
            uni_display_type = st.selectbox(label="display type", options=["box", "rugplot", "violin"], index=Defaults.DISPLAY_TYPE_INDEX, key=f"display_type_{uni}")
            

    if type != "numeric":
        custom_value_order = st.checkbox("Custom label order?", key=f"value_order_{uni}")
    
        if custom_value_order:
            options = get_formatted_values(values)
            value_order = st.multiselect(label="Custom label order", options=options, help="Order of the values in the unibar, from bottom to top.")

            if len(value_order) < len(options):
                st.error("Select all options to proceed.")

            st.session_state.value_order[uni] = value_order
            type = "categorical"
        
        uni_display_type = st.selectbox(label="display type", options=["stacked bar", "bar chart"], index=Defaults.DISPLAY_TYPE_INDEX, key=f"display_type_{uni}")       
    
    st.session_state.display_type[uni] = uni_display_type
    
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
    
    missing = st.checkbox(label="Plot missing values?")
    if unibars != st.session_state.unibars or missing != st.session_state.missing:
        run_plot_on_refresh()
        st.session_state.unibars = unibars
        st.session_state.missing=missing
    
    if not unibars or len(unibars) == 0:
        st.markdown(":gray[Select unibars to proceed]")
    else:
        container = st.container(border=True)
        with container:
            plotcol, customcol = adjustable_columns([2, 1], labels=["Graph", "Settings"])
            with customcol:
                presets, highlight_settings, general, uni_spec = st.tabs(["Preset", "Highlighting", "Advanced", "Unibar-Specific"])
                with presets:
                    st.header("Preset Setting Options")
                    st.text("Sets all settings to preset options. Refreshes the plot.")
                    if st.button("Hammock", type="primary" if st.session_state["mode"] == "hammock" else "secondary", key=f"hammock_{st.session_state.reset_counter}", use_container_width=True):
                        mode = "hammock"
                        if mode != st.session_state.mode:
                            run_plot_on_refresh()
                            st.session_state.mode = mode
                        set_default_settings()
                        # st.session_state.reset_presets = True
                        # st.rerun()

                    if st.button("Snapshot", type="primary" if st.session_state["mode"] == "snapshot" else "secondary", key=f"snapshot{st.session_state.reset_counter}", use_container_width=True):
                        mode = "snapshot"
                        if mode != st.session_state.mode:
                            run_plot_on_refresh()
                            st.session_state.mode = mode
                        set_snapshot_settings()
                        # st.session_state.reset_presets = True
                        # st.rerun()

                    # load default settings
                    fig_height = Defaults.HEIGHT
                    fig_width = max(Defaults.WIDTH, len(unibars) * 4/3)
                    default_color = Defaults.DEFAULT_COLOR
                    alpha = Defaults.ALPHA
                    label = True
                    unibar = True
                    missing_placeholder = "missing"
                    min_bar_height = Defaults.MIN_BAR_HEIGHT
                    uni_vfill = Defaults.uni_vfill
                    uni_hfill = Defaults.uni_hfill
                    connector_fraction = Defaults.CONNECTOR_FRACTION
                    shape = "rectangle"
                    connector_color = None
                    same_scale = []
                    violin_bw_method = "scott"

                    # manage session_state variables
                    st.session_state.numerical_var_levels = {}
                    st.session_state.display_type = {}
                    st.session_state.label_options = {}
                    st.session_state.value_order = {}

                    # initialize numerical display type defaults
                    for uni in unibars:
                        type = get_uni_type(uni)
                        values = st.session_state.df[uni].dropna().unique()
                        if type == "numeric" and (np.array_equal(values, [0, 1]) or np.array_equal(values, [1, 0])):
                            st.session_state.value_order[uni] = ["0", "1"]
                        if type == "numeric":
                            st.session_state.display_type[uni] = "box"
                # ------ HIGHLIGHT SETTINGS ---------
                with highlight_settings:
                    st.header("Highlighting")
                    highlight = st.checkbox("Enable highlighting?", value=False, key=f"highlight_{st.session_state.reset_counter}")
                    if highlight:
                        hi_var = st.selectbox(label="Select the variable to highlight", options=list(st.session_state.df))
                        subcols = st.columns(2)
                        hi_options = ["specific labels", "expression"]
                        hi_type = subcols[0].radio("Highlight type", options=hi_options)
                        hi_box = subcols[1].radio("Highlight box", options=["side-by-side", "stacked"])
                        if hi_type == hi_options[0]: # highlighting specific labels
                            hi_value = st.multiselect(label="Select labels to highlight", options=(st.session_state.df[hi_var].dropna().unique()))
                        else:
                            hi_value = st.text_input(label="Expression (regex/range) to highlight", help="e.g. x>1 and (x>5 or x<4)")
                            if hi_value != "" and not validate_expression(hi_value):
                                st.error("Must provide a valid expression (regex/range)")
                        if missing:
                            hi_missing = st.checkbox("Highlight missing values?")
                        else:
                            hi_missing = False
                        num_highlight = len(hi_value) if hi_type == hi_options[0] else 1
                        num_highlight += 1 if hi_missing else 0
                        hi_colors = []
                        cols = st.columns(4)  # create 3 columns

                        for i in range(num_highlight):
                            col = cols[i % 4]  # rotate through the 3 columns
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
                with general:
                    # ------------ GENERAL SETTINGS ----------------------
                    st.subheader("General")
                    subcol1, subcol2 = st.columns([1, 1])
                    fig_height = subcol1.number_input(label="Height", value=fig_height, step=0.5, key=f"height_{st.session_state.reset_counter}",
                                                help="Height of the plot")
                    fig_width = subcol2.number_input(label="Width", value=fig_width, step=0.5, key=f"width_{st.session_state.reset_counter}",
                                                help="Width of the plot")
                    
                    min_bar_height = st.number_input(label="Minimum bar height",
                                                        value=min_bar_height,
                                                        key=f"min_bar_height_{st.session_state.reset_counter}",
                                                        help="Bars representing only a tiny fraction of the data may be so narrow that they are invisible in a plot. This parameter ensures that no bars can be thinner than the minimum.")

                    subcol1, subcol2 = st.columns([1, 1])
                    default_color = subcol1.color_picker(label="Default colour", value=default_color, key=f"default_color_{st.session_state.reset_counter}",
                                                        help="The default, unhighlighted colour of the plot")
                    alpha = subcol1.slider(label="Opacity", value=alpha, min_value=0, max_value=100, format="%d%%")

                    label = subcol2.checkbox(label="Display labels?", value=label, help="Whether or not to display the text labels")
                    unibar = subcol2.checkbox(label="Display unibars?", value=unibar, help="Whether or not to display unibars")

                    if not label and not unibar:
                        uni_hfill = 0
                    
                    if missing:
                        missing_placeholder = subcol1.text_input(label="Missing value label", value=missing_placeholder,
                                                                help="The label for missing values")
                        
                    subcol1, subcol2 = st.columns([1, 1])
                    uni_vfill = subcol1.slider(label="Unibar Vertical Fill",
                                            key=f"uni_vfill_{st.session_state.reset_counter}",
                                            min_value=0, max_value=100,
                                            value=uni_vfill, format="%d%%",
                                            help="Fraction of vertical space that should be populated by data. Adjusts the height of the data points.")
                    uni_hfill = subcol2.slider(label="Unibar Horizontal Fill",
                                            key=f"uni_hfill_{st.session_state.reset_counter}",
                                            min_value=0, max_value=100, 
                                            value=uni_hfill, format="%d%%",
                                            help="Fraction of horizontal space allocated to labels/univ. bars rather than to connecting boxes.",
                                            disabled=not(label or unibar))
                    if st.session_state["mode"] != "snapshot":
                        connector_fraction = subcol1.slider(label="Connector Fraction",
                                                            key=f"connect_frac_{st.session_state.reset_counter}",
                                                            value=connector_fraction,
                                                            min_value=0, max_value=100,format="%d%%",
                                                            help="Fraction of the uni_vfill height used for drawing connectors between unibars. Controls how tall the connectors are relative to the bar height.")
                        custom_connector_color = subcol1.checkbox(label="Separate Connector Color?", key=f"custom_connect_color_{st.session_state.reset_counter}", value=False)
                        shape = subcol2.selectbox(label="Connector Shape",
                                                key=f"shape_{st.session_state.reset_counter}",
                                                options=["rectangle", "parallelogram"],
                                                help="Shape of the connectors.")
                        connector_color = None if not custom_connector_color else subcol2.color_picker(label="Connector color", value=default_color, key=f"connect_color_{st.session_state.reset_counter}")
                
                with uni_spec:
                    # ------ UNIBAR SPECIFIC SETTINGS ---------
                    st.subheader("Unibar-Specific")
                    
                    same_scale = st.multiselect(label="Variables to use same scale", options=unibars)
                    same_scale_type = get_uni_type(same_scale[0]) if same_scale else None
                    for uni in same_scale:
                        if same_scale_type != get_uni_type(uni):
                            st.error("Variables in same_scale must either all be numerical or all be categorical")
                    violin_bw_method = st.selectbox(label="violin plot bw method [(see matplotlib documentation)](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.violinplot.html)", options=["scott", "silverman", "custom float"])
                    if violin_bw_method == "custom float":
                        violin_bw_method = st.number_input("custom float", min_value=0.0, value=0.5, step=0.1)
                    
                    for unibar in unibars:
                        display_unibar_specific_settings(unibar)
            
            def run_plot():
                with st.spinner("Plotting hammock... this may take a while"):
                    plot(
                        var=unibars,
                        value_order=st.session_state.value_order,
                        numerical_var_levels=st.session_state.numerical_var_levels,
                        display_type=st.session_state.display_type,
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
                        uni_vfill=uni_vfill / 100,
                        connector_fraction=connector_fraction / 100,
                        connector_color = connector_color,
                        uni_hfill=uni_hfill / 100,
                        label_options=st.session_state.label_options,
                        height=fig_height,
                        width=fig_width,
                        min_bar_height=min_bar_height,
                        alpha=alpha / 100,
                        shape=shape,
                        same_scale=same_scale,
                        violin_bw_method=violin_bw_method,
                    )
            with plotcol:
                # -------- PLOT GRAPH -----------
                if st.session_state.run_plot_soon:
                    st.session_state.run_plot_soon = False
                    run_plot()
                if st.button("**Apply Custom Settings**", type="primary", use_container_width=True, help="Refresh when you update settings"):
                    run_plot()
                if "fig" in st.session_state:
                    if not unibars:
                        del st.session_state["fig"]
                        del st.session_state["buf"]
                        st.rerun()
                    st.image(st.session_state.buf, use_container_width=True) # display fig in streamlit
                    
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        st.download_button(
                            label="Download as PNG",
                            data=st.session_state.buf,
                            file_name="my_plot.png",
                            mime="image/png",
                            icon=":material/download:",
                            use_container_width=True,
                        )
                    with subcol2: 
                        if st.button("Clear plot", use_container_width=True):
                            del st.session_state["fig"]
                            del st.session_state["buf"]
                            st.rerun()