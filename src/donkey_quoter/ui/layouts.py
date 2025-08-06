"""
Reusable layout patterns and containers for the Streamlit application.
"""

from typing import Any

import streamlit as st


def three_column_layout(gap: str = "medium") -> list[Any]:
    """
    Creates a standard 3-column layout.

    Args:
        gap: The gap between columns ("small", "medium", "large")

    Returns:
        List of column objects
    """
    return st.columns(3, gap=gap)


def two_column_layout(ratios: list[int] = None) -> list[Any]:
    """
    Creates a standard 2-column layout.

    Args:
        ratios: Column width ratios, defaults to [1, 1]

    Returns:
        List of column objects
    """
    if ratios is None:
        ratios = [1, 1]
    return st.columns(ratios)


def centered_column_layout(center_ratio: int = 2) -> list[Any]:
    """
    Creates a 3-column layout with centered content.

    Args:
        center_ratio: Ratio for the center column (outer columns are 1)

    Returns:
        List of column objects [left, center, right]
    """
    return st.columns([1, center_ratio, 1])


def bordered_container():
    """
    Creates a container with border styling.

    Returns:
        Streamlit container object
    """
    return st.container(border=True)


def spaced_container(margin_top: str = "1rem"):
    """
    Adds vertical spacing using HTML margin.

    Args:
        margin_top: CSS margin-top value
    """
    st.markdown(
        f"<div style='margin-top: {margin_top};'></div>", unsafe_allow_html=True
    )


def action_button_row(
    buttons: list[dict], gap: str = "medium", equal_width: bool = True
) -> None:
    """
    Creates a row of action buttons with consistent styling.

    Args:
        buttons: List of button configs with keys: label, key, callback, type, disabled
        gap: Gap between columns
        equal_width: Whether buttons should have equal width
    """
    cols = st.columns(len(buttons), gap=gap)

    for _, (col, btn_config) in enumerate(zip(cols, buttons)):
        with col:
            clicked = st.button(
                btn_config["label"],
                key=btn_config["key"],
                use_container_width=equal_width,
                type=btn_config.get("type", "secondary"),
                disabled=btn_config.get("disabled", False),
            )

            if clicked and "callback" in btn_config:
                btn_config["callback"]()


def stats_row(stats: list[dict]) -> None:
    """
    Creates a row of statistics displays.

    Args:
        stats: List of stat configs with keys: value, label, style_class
    """
    cols = st.columns(len(stats))

    for col, stat in zip(cols, stats):
        with col:
            st.markdown(
                f'<div class="stats-card {stat.get("style_class", "")}">'
                f'<div class="stats-number">{stat["value"]}</div>'
                f'<div class="stats-label">{stat["label"]}</div>'
                "</div>",
                unsafe_allow_html=True,
            )


def footer_spacer(height: str = "2rem") -> None:
    """
    Adds spacing before footer content.

    Args:
        height: CSS height value for spacing
    """
    st.markdown(
        "<br>" * int(height.replace("rem", "").replace("px", "")[0]),
        unsafe_allow_html=True,
    )
