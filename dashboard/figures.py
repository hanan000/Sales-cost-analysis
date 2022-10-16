"""Plotly figure builders for the dashboard.

Each builder takes already-aggregated data (see ``sales_data``) and returns a
``go.Figure``, so the charts can be built and inspected without a Dash server.
"""
from __future__ import annotations

import operator
from functools import reduce

import pandas as pd
import plotly.graph_objects as go

from sales_data import MANUFACTURER, MONTH, PRODUCT_GROUP, SALES, YEAR

BACKGROUND = "#1f2c56"
LEGEND_BACKGROUND = "#010915"
ACCENT = "#19AAE1"
AXIS_COLOR = "orange"
DONUT_COLORS = ["#30C9C7", "#7A45D1", "orange"]

# Bubble area scale: monthly sales (TL) per pixel of marker size.
BUBBLE_SIZE_DIVISOR = 250


def _axis(showline: bool, showgrid: bool, showticklabels: bool = True, **extra) -> dict:
    return dict(title="<b></b>", color=AXIS_COLOR, showline=showline,
                showgrid=showgrid, showticklabels=showticklabels,
                linecolor=AXIS_COLOR, linewidth=1, ticks="outside",
                tickfont=dict(family="Arial", color=AXIS_COLOR, size=12),
                **extra)


def _layout(title: str, *, title_y: float = 0.99, title_size: int = 12,
            font_size: int = 12, legend_bgcolor: str = LEGEND_BACKGROUND,
            **extra) -> go.Layout:
    return go.Layout(
        title={"text": title, "y": title_y, "x": 0.5,
               "xanchor": "center", "yanchor": "top",
               "font": {"color": "white", "size": title_size}},
        font=dict(family="sans-serif", color="white", size=font_size),
        hovermode="closest",
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        legend={"orientation": "h", "bgcolor": legend_bgcolor,
                "xanchor": "center", "x": 0.5, "y": -0.7},
        **extra,
    )


def _money(values: pd.Series) -> pd.Series:
    return values.map(lambda x: f"TL{x:,.0f}").astype(object)


def _hover(df: pd.DataFrame, fields: dict[str, str]) -> pd.Series:
    """Build '<b>Label</b>: value<br>' hover text from ``{label: column}``."""
    parts = []
    for label, column in fields.items():
        values = _money(df[column]) if column == SALES else df[column].astype(str)
        parts.append(f"<b>{label}</b>: " + values + "<br>")
    return reduce(operator.add, parts)


def top_n_bar(top: pd.DataFrame, category: str, year: int) -> go.Figure:
    """Horizontal bar chart of the top categories (output of ``top_n_by``)."""
    bar = go.Bar(
        x=top[SALES],
        y=top[category],
        text=top[SALES],
        texttemplate="TL%{text:,.2s}",
        textposition="auto",
        orientation="h",
        marker=dict(color=ACCENT),
        hoverinfo="text",
        hovertext=_hover(top, {"Yıl": YEAR, "Lokasyon": "Lokasyon",
                               category: category, "Satış": SALES}),
    )
    layout = _layout(f"Satışlar {year}", font_size=15,
                     margin=dict(t=40, r=0),
                     xaxis=_axis(showline=True, showgrid=True),
                     yaxis=_axis(showline=False, showgrid=False,
                                 autorange="reversed"))
    return go.Figure(data=[bar], layout=layout)


def group_donut(totals: pd.Series, year: int) -> go.Figure:
    """Donut chart of sales split by product group (output of ``sales_by_group``)."""
    pie = go.Pie(
        labels=list(totals.index),
        values=list(totals.values),
        marker=dict(colors=DONUT_COLORS),
        hoverinfo="label+value+percent",
        textinfo="label+value",
        texttemplate="%{label} <br>TL%{value:,.2f}",
        textposition="auto",
        textfont=dict(size=13),
        hole=0.7,
        rotation=160,
    )
    layout = _layout(f"Satışlar {year}", title_y=0.93, title_size=15,
                     legend_bgcolor=BACKGROUND)
    return go.Figure(data=[pie], layout=layout)


def monthly_trend(monthly: pd.DataFrame, year: int) -> go.Figure:
    """Line chart of monthly sales (output of ``monthly_sales``)."""
    line = go.Scatter(
        x=monthly[MONTH],
        y=monthly[SALES],
        text=monthly[SALES],
        texttemplate="TL%{text:,.2s}",
        textposition="bottom left",
        mode="markers+lines+text",
        line=dict(width=3, color=AXIS_COLOR),
        marker=dict(color=ACCENT, size=10, symbol="circle",
                    line=dict(color=ACCENT, width=2)),
        hoverinfo="text",
        hovertext=_hover(monthly, {"Yıl": YEAR, "Ay": MONTH,
                                   "Lokasyon": "Lokasyon", "Satış": SALES}),
    )
    layout = _layout(f"Satış Trendi {year}",
                     margin=dict(t=5, l=0, r=0),
                     xaxis=_axis(showline=True, showgrid=False),
                     yaxis=_axis(showline=False, showgrid=True,
                                 showticklabels=False))
    return go.Figure(data=[line], layout=layout)


def manufacturer_bubbles(monthly: pd.DataFrame, year: int) -> go.Figure:
    """Bubble chart of one manufacturer's monthly sales per product group.

    ``monthly`` is the output of ``monthly_sales(..., manufacturer=...)``.
    """
    bubbles = go.Scatter(
        x=monthly[MONTH],
        y=monthly[SALES],
        mode="markers",
        marker=dict(color=monthly[SALES],
                    colorscale="HSV",
                    showscale=False,
                    size=monthly[SALES] / BUBBLE_SIZE_DIVISOR,
                    symbol="circle",
                    line=dict(color="MediumPurple", width=2)),
        hoverinfo="text",
        hovertext=_hover(monthly, {"Yıl": YEAR, "Ay": MONTH,
                                   "Üretici Adı": MANUFACTURER,
                                   "Ürün Grubu": PRODUCT_GROUP,
                                   "Satış Tutarı": SALES}),
    )
    layout = _layout(f"Satışlar (Üretici Adı) {year}",
                     margin=dict(t=40, l=0, r=0),
                     xaxis=_axis(showline=True, showgrid=False),
                     yaxis=_axis(showline=False, showgrid=True,
                                 showticklabels=False))
    return go.Figure(data=[bubbles], layout=layout)
