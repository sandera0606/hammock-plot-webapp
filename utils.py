import io
import streamlit as st
import re
import hammock_plot
import pandas as pd

def plot(# General
            var,
            value_order,
            numerical_var_levels,
            numerical_display_type,
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
            uni_fraction,
            connector_fraction, 
            space, 
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
    ax = hammock.plot(
        var=var,
        value_order=value_order,
        numerical_var_levels=numerical_var_levels,
        numerical_display_type=numerical_display_type,
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
        uni_fraction=uni_fraction,
        # connector_fraction=connector_fraction, # not up to date with the current package
        space=space,
        label_options=label_options,
        height=height,
        width=width,
        alpha=alpha,
        min_bar_height=min_bar_height,
        shape=shape,
        same_scale=same_scale,
        display_figure=True,
        save_path=None,
        # violin_bw_method=violin_bw_method, # not up to date with the current package
    )
    st.session_state.fig = ax.get_figure()

def prep_data_for_download():
    buf = io.BytesIO()
    st.session_state.fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.session_state.buf = buf

class Defaults:
    HEIGHT = 10.0
    WIDTH = 15.0
    UNI_FRACTION = 0.08
    SPACE = 0.3
    CONNECTOR_FRACTION = 1.0
    DEFAULT_COLOR="#a6cee3"
    HI_COLORS=["#e31a1c", "#fb9a99", "#33a02c", "#b2df8a", "#ff7f00", "#fdbf6f", "#6a3d9a", "#cab2d6", "#b15928", "#1f78b4"]
    ALPHA=0.7
    MIN_BAR_HEIGHT: float = 0.15

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