import math

from dash import Dash

import index
import sales_data as sd


def _find(component, component_id):
    if getattr(component, "id", None) == component_id:
        return component
    children = getattr(component, "children", None)
    if not isinstance(children, (list, tuple)):
        children = [children] if children is not None else []
    for child in children:
        found = _find(child, component_id)
        if found is not None:
            return found
    return None


def test_create_app_builds_layout(sales):
    app = index.create_app(sales)
    assert isinstance(app, Dash)
    for component_id in ["select_years", "radio_items", "bar_chart_1", "donut_chart",
                         "line_chart", "text1", "my_datatable", "bar_chart_2",
                         "bubble_chart"]:
        assert _find(app.layout, component_id) is not None, component_id
    assert len(app.callback_map) == 7


def test_controls_default_to_data(sales):
    layout = index.build_layout(sales)
    slider = _find(layout, "select_years")
    assert (slider.min, slider.max, slider.value) == (2019, 2020, 2020)
    assert set(slider.marks) == {2019, 2020}
    locations = _find(layout, "radio_items")
    # The default must be one of the options (the original padded value was not).
    assert locations.value == sd.ALL_LOCATIONS
    assert sd.ALL_LOCATIONS in [o["value"] for o in locations.options]


def test_kpi_formatting():
    assert index.format_money(1234.5) == "TL1,234.50"
    assert index.format_percent(45.30896) == "45.31%"
    assert index.format_money(math.nan) == "–"
    assert index.format_percent(math.nan) == "–"
