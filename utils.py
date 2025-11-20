import io
import streamlit as st
import re
import hammock_plot
import pandas as pd
import numpy as np

def prep_data_for_download():
    buf = io.BytesIO()
    st.session_state.fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.session_state.buf = buf

def plot(# General
            var,
            value_order,
            numerical_var_levels,
            display_type,
            missing,
            missing_placeholder,
            label,
            unibar,

            # Highlighting
            hi_var,
            hi_value,
            hi_box,
            hi_missing,
            colors,
            default_color,

            # Layout
            uni_vfill,
            connector_fraction, 
            connector_color,
            uni_hfill, 
            label_options,
            height,
            width,
            min_bar_height,
            alpha,

            # Other
            shape,
            same_scale,
            violin_bw_method):
    hammock = hammock_plot.Hammock(data_df=st.session_state.df)

    try:
        ax = hammock.plot(
            var=var,
            value_order=value_order,
            numerical_var_levels=numerical_var_levels,
            display_type=display_type,
            missing=missing,
            missing_placeholder=missing_placeholder,
            label=label,
            unibar=unibar,
            hi_var=hi_var,
            hi_value=hi_value,
            hi_box=hi_box,
            hi_missing=hi_missing,
            colors=colors,
            default_color=default_color,
            uni_vfill=uni_vfill,
            connector_fraction=connector_fraction,
            connector_color=connector_color,
            uni_hfill=uni_hfill,
            label_options=label_options,
            height=height,
            width=width,
            alpha=alpha,
            min_bar_height=min_bar_height,
            shape=shape,
            same_scale=same_scale,
            display_figure=True,
            save_path=None,
            violin_bw_method=violin_bw_method,
        )
        st.session_state.fig = ax.get_figure()
        prep_data_for_download()
    except Exception as e:
        st.error(str(e))

class Defaults:
    HEIGHT = 10.0
    WIDTH = 15.0
    uni_vfill = 8
    uni_hfill = 30
    CONNECTOR_FRACTION = 100
    DEFAULT_COLOR="#a6cee3"
    HI_COLORS=["#e31a1c", "#fb9a99", "#33a02c", "#b2df8a", "#ff7f00", "#fdbf6f", "#6a3d9a", "#cab2d6", "#b15928", "#1f78b4"]
    ALPHA=70
    MIN_BAR_HEIGHT: float = 0.15
    DISPLAY_TYPE_INDEX: int = 0

def set_default_settings():
    st.session_state.reset_counter = 1 if st.session_state.reset_counter == 0 else 0
    Defaults.HEIGHT = 10.0
    Defaults.WIDTH = 15.0
    Defaults.uni_vfill = 8
    Defaults.uni_hfill = 30
    Defaults.CONNECTOR_FRACTION = 100
    Defaults.DEFAULT_COLOR="#a6cee3"
    Defaults.HI_COLORS=["#e31a1c", "#fb9a99", "#33a02c", "#b2df8a", "#ff7f00", "#fdbf6f", "#6a3d9a", "#cab2d6", "#b15928", "#1f78b4"]
    Defaults.ALPHA=70
    Defaults.MIN_BAR_HEIGHT = 0.15
    st.rerun()

def set_snapshot_settings():
    st.session_state.reset_counter = 1 if st.session_state.reset_counter == 0 else 0
    Defaults.uni_vfill = 99
    Defaults.uni_hfill = 85
    Defaults.CONNECTOR_FRACTION = 0
    st.rerun()

def clean_expression(expr: str) -> str:
    """
    Cleans up a logical expression string by inserting necessary spaces
    around logical operators, comparison operators, and parentheses.
    """
    expr = re.sub(r'(?i)(\w)(and|or|not)(\w)', r'\1 \2 \3', expr)
    expr = re.sub(r'(?i)(\W)(and|or|not)(\w)', r'\1 \2 \3', expr)
    expr = re.sub(r'(?i)(\w)(and|or|not)(\W)', r'\1 \2 \3', expr)
    expr = re.sub(r'(?i)\b(and|or|not)\b', r' \1 ', expr)
    expr = re.sub(r'([<>!=]=?|==)', r' \1 ', expr)
    expr = re.sub(r'([a-zA-Z0-9_])(\()', r'\1 \2', expr)
    expr = re.sub(r'(\))([a-zA-Z0-9_])', r'\1 \2', expr)
    expr = re.sub(r'\s+', ' ', expr)
    return expr.strip()


def is_in_range(x: float, expr: str) -> bool:
    """
    Evaluates whether the given x satisfies the cleaned expression.
    Only 'x' is available inside the eval environment.
    """
    expr = clean_expression(expr)
    try:
        return eval(expr, {"__builtins__": {}}, {"x": x})
    except Exception as e:
        raise ValueError(f"Invalid expression: '{expr}'") from e

def validate_expression(expr: str) -> bool:
    """
    Validates whether an expression string can be parsed and evaluated safely.
    Returns True if it's either:
      - A valid numeric range expression for `is_in_range`
      - A valid regex pattern
    """
    # First, check if it can be evaluated as a numeric range
    try:
        _ = is_in_range(0, expr)
        return True
    except Exception:
        pass

    # Next, check if it's a valid regex
    try:
        re.compile(expr)
        return True
    except re.error:
        return False

def get_uni_type(uni):
    df = st.session_state.df
    temp = df[uni].dropna()
    dtype = temp.dtype

    if pd.api.types.is_integer_dtype(dtype):
        return "numeric"
    elif pd.api.types.is_float_dtype(dtype):
        return "numeric"
    elif pd.api.types.is_categorical_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        return "categorical"
    else:
        raise RuntimeError("Invalid dtype detected - logic error in code. dtype: ", dtype)

def get_formatted_label(datatype, value):
    # if the label is a string
    if datatype == np.str_:
        return value
    # otherwise, it should be a numerical value
    value = float(value)
    if abs(value) >= 1000000 or 0 < abs(value) < 0.01: # threshold for displaying scientific notation
        return f"{value:.2e}"
    if datatype == np.integer:
        return str(int(value))
    if datatype == np.floating:
        return f"{value:.2f}" # round to 2 decimal places

def get_formatted_values(raw_values):
    dtype = raw_values.dtype
    if pd.api.types.is_integer_dtype(dtype):
        dtype = np.integer
    elif pd.api.types.is_float_dtype(dtype):
        dtype = np.floating
        if (raw_values == raw_values.astype(int)).all():
            dtype = np.integer
        else:
            dtype = np.floating
    elif pd.api.types.is_categorical_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        dtype = np.str_
    
    return [get_formatted_label(dtype, value) for value in raw_values]