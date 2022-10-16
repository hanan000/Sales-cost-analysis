"""Dash dashboard for the supermarket sales cost analysis.

Run from the repository root with::

    python dashboard/index.py

The combined CSV is read from ``dashboard/concat_all_files_.csv`` unless the
``SALES_DATA_PATH`` environment variable points somewhere else.
"""
from __future__ import annotations

import math
import os

import pandas as pd
from dash import Dash, Input, Output, dash_table, dcc, html

import figures
import sales_data as sd

GRAPH_CONFIG = {"displayModeBar": "hover"}
CONTROL_STYLE = {"text-align": "center", "color": "white"}

# Categories shown in the donut chart.
DONUT_GROUPS = ["GIDA", "GIDA DIŞI", "KOZMETIK"]
# Manufacturer featured in the bubble chart.
BUBBLE_MANUFACTURER = "SULTANLAR TIBET*"


def format_money(value: float) -> str:
    return "–" if math.isnan(value) else f"TL{value:,.2f}"


def format_percent(value: float) -> str:
    return "–" if math.isnan(value) else f"{value:,.2f}%"


def _kpi(title: str, value: str) -> list:
    return [
        html.H6(title, style={"textAlign": "center", "color": "white"}),
        html.P(value, style={"textAlign": "center", "color": figures.ACCENT,
                             "fontSize": 15, "margin-top": "-10px"}),
    ]


def _radio(component_id: str, options: list[str], value: str) -> dcc.RadioItems:
    return dcc.RadioItems(id=component_id,
                          options=[{"label": o, "value": o} for o in options],
                          value=value,
                          labelStyle={"display": "inline-block"},
                          style=CONTROL_STYLE,
                          className="dcc_compon")


def _graph(component_id: str, **style) -> dcc.Graph:
    return dcc.Graph(id=component_id, config=GRAPH_CONFIG, style=style or None)


def build_layout(sales: pd.DataFrame) -> html.Div:
    years = sd.available_years(sales)
    locations = sd.available_locations(sales)
    default_location = sd.ALL_LOCATIONS if sd.ALL_LOCATIONS in locations else locations[0]

    header = html.Div([
        html.Div([
            html.H3("Satış Maliyet Analizi",
                    style={"margin-bottom": "4px", "color": "white"}),
        ], className="one-third column", id="title1"),
        html.Div([
            html.P("Yıllar", className="fix_label", style={"color": "white"}),
            dcc.Slider(id="select_years",
                       min=years[0], max=years[-1], step=1, value=years[-1],
                       marks={year: str(year) for year in years},
                       included=False,
                       updatemode="drag",
                       tooltip={"always_visible": True},
                       className="dcc_compon"),
        ], className="one-half column", id="title2"),
        html.Div([
            html.P("Lokasyon", className="fix_label", style={"color": "white"}),
            _radio("radio_items", locations, default_location),
        ], className="one-third column", id="title3"),
    ], id="header", className="row flex-display", style={"margin-bottom": "25px"})

    top_row = html.Div([
        html.Div([
            _radio("radio_items1", [sd.PRODUCT_SUBGROUP, sd.MANUFACTURER],
                   sd.PRODUCT_SUBGROUP),
            _graph("bar_chart_1", height="350px"),
        ], className="create_container2 three columns", style={"height": "400px"}),
        html.Div([_graph("donut_chart", height="350px")],
                 className="create_container2 three columns", style={"height": "400px"}),
        html.Div([_graph("line_chart", height="350px")],
                 className="create_container2 four columns", style={"height": "400px"}),
        html.Div([html.Div(id="text1"), html.Div(id="text2"), html.Div(id="text3")],
                 className="create_container2 two columns"),
    ], className="row flex-display")

    table = dash_table.DataTable(
        id="my_datatable",
        columns=[{"name": c, "id": c} for c in sd.TABLE_COLUMNS],
        virtualization=True,
        style_cell={"textAlign": "left",
                    "min-width": "100px",
                    "backgroundColor": figures.BACKGROUND,
                    "color": "#FEFEFE",
                    "border-bottom": "0.01rem solid #19AAE1"},
        style_header={"backgroundColor": figures.BACKGROUND,
                      "fontWeight": "bold",
                      "font": "Lato, sans-serif",
                      "color": "orange",
                      "border": figures.BACKGROUND},
        style_as_list_view=True,
        style_data={"overflow": "hidden", "color": "white"},
        fixed_rows={"headers": True},
        sort_action="native",
        sort_mode="multi",
    )

    bottom_row = html.Div([
        html.Div([table], className="create_container2 three columns"),
        html.Div([
            _radio("radio_items2", [sd.PRODUCT_GROUP, sd.UNIT], sd.PRODUCT_GROUP),
            _graph("bar_chart_2"),
        ], className="create_container2 three columns"),
        html.Div([_graph("bubble_chart")], className="create_container2 six columns"),
    ], className="row flex-display")

    return html.Div([header, top_row, bottom_row], id="mainContainer",
                    style={"display": "flex", "flex-direction": "column"})


def register_callbacks(app: Dash, sales: pd.DataFrame) -> None:
    year_and_location = [Input("select_years", "value"), Input("radio_items", "value")]

    @app.callback(Output("bar_chart_1", "figure"),
                  *year_and_location, Input("radio_items1", "value"))
    def update_bar_chart_1(year, location, category):
        top = sd.top_n_by(sales, year, location, category)
        return figures.top_n_bar(top, category, year)

    @app.callback(Output("donut_chart", "figure"), *year_and_location)
    def update_donut_chart(year, location):
        totals = sd.sales_by_group(sales, year, location, DONUT_GROUPS)
        return figures.group_donut(totals, year)

    @app.callback(Output("line_chart", "figure"), *year_and_location)
    def update_line_chart(year, location):
        return figures.monthly_trend(sd.monthly_sales(sales, year, location), year)

    @app.callback(Output("text1", "children"), Output("text2", "children"),
                  Output("text3", "children"), Input("select_years", "value"))
    def update_kpis(year):
        kpis = sd.yearly_kpis(sales, year)
        return (_kpi("Bu yıl", format_money(kpis["current"])),
                _kpi("Geçen yıl", format_money(kpis["previous"])),
                _kpi("Büyüme", format_percent(kpis["growth"])))

    @app.callback(Output("my_datatable", "data"), *year_and_location)
    def update_table(year, location):
        return sd.table_records(sales, year, location)

    @app.callback(Output("bar_chart_2", "figure"),
                  *year_and_location, Input("radio_items2", "value"))
    def update_bar_chart_2(year, location, category):
        top = sd.top_n_by(sales, year, location, category)
        return figures.top_n_bar(top, category, year)

    @app.callback(Output("bubble_chart", "figure"), *year_and_location)
    def update_bubble_chart(year, location):
        monthly = sd.monthly_sales(sales, year, location,
                                   manufacturer=BUBBLE_MANUFACTURER)
        return figures.manufacturer_bubbles(monthly, year)


def create_app(sales: pd.DataFrame) -> Dash:
    app = Dash(__name__, meta_tags=[{"name": "viewport",
                                     "content": "width=device-width"}])
    app.title = "Satış Maliyet Analizi"
    app.layout = build_layout(sales)
    register_callbacks(app, sales)
    return app


if __name__ == "__main__":
    data_path = os.environ.get("SALES_DATA_PATH", sd.DEFAULT_DATA_PATH)
    create_app(sd.load_sales(data_path)).run(debug=True)
