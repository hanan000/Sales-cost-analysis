import plotly.graph_objects as go

import figures
import sales_data as sd


def test_top_n_bar(sales):
    top = sd.top_n_by(sales, 2020, sd.ALL_LOCATIONS, sd.PRODUCT_SUBGROUP)
    fig = figures.top_n_bar(top, sd.PRODUCT_SUBGROUP, 2020)
    assert isinstance(fig, go.Figure)
    bar = fig.data[0]
    assert bar.orientation == "h"
    assert list(bar.y) == list(top[sd.PRODUCT_SUBGROUP])
    assert fig.layout.title.text == "Satışlar 2020"
    assert "<b>Satış</b>: TL200<br>" in bar.hovertext[0]


def test_group_donut(sales):
    totals = sd.sales_by_group(sales, 2019, sd.ALL_LOCATIONS, ["GIDA", "KOZMETIK"])
    fig = figures.group_donut(totals, 2019)
    pie = fig.data[0]
    assert list(pie.labels) == ["GIDA", "KOZMETIK"]
    assert list(pie.values) == [150.0, 30.0]
    assert pie.hole == 0.7


def test_monthly_trend_keeps_calendar_order(sales):
    monthly = sd.monthly_sales(sales, 2019, sd.ALL_LOCATIONS)
    fig = figures.monthly_trend(monthly, 2019)
    assert list(fig.data[0].x) == ["January", "February", "March"]
    assert fig.layout.title.text == "Satış Trendi 2019"


def test_manufacturer_bubbles_scale_with_sales(sales):
    monthly = sd.monthly_sales(sales, 2020, sd.ALL_LOCATIONS,
                               manufacturer="SULTANLAR TIBET*")
    fig = figures.manufacturer_bubbles(monthly, 2020)
    marker = fig.data[0].marker
    assert list(marker.size) == [200 / figures.BUBBLE_SIZE_DIVISOR,
                                 40 / figures.BUBBLE_SIZE_DIVISOR]
    assert "<b>Üretici Adı</b>: SULTANLAR TIBET*" in fig.data[0].hovertext[0]


def test_figures_handle_empty_selection(sales):
    top = sd.top_n_by(sales, 2021, sd.ALL_LOCATIONS, sd.MANUFACTURER)
    fig = figures.top_n_bar(top, sd.MANUFACTURER, 2021)
    assert len(fig.data[0].x) == 0
