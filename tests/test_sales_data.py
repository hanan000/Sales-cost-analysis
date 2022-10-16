import math

import sales_data as sd


def test_load_sales_reads_csv(tmp_path, raw_sales):
    path = tmp_path / "sales.csv"
    raw_sales.to_csv(path, index=False, encoding="utf-8-sig")
    sales = sd.load_sales(path)
    assert len(sales) == 7
    assert sales[sd.SALES].sum() == 550.0


def test_clean_sales_drops_summary_rows(sales):
    assert not sales[sd.UNIT].isin(sd.SUMMARY_ROW_UNITS).any()
    assert sales[sd.SALES].sum() == 550.0


def test_clean_sales_strips_padding_and_adds_date_parts(sales):
    assert set(sales[sd.LOCATION]) == {sd.ALL_LOCATIONS, "Kadıköy"}
    first = sales.iloc[0]
    assert (first[sd.YEAR], first[sd.MONTH_NO], first[sd.MONTH]) == (2019, 1, "January")


def test_available_years_and_locations(sales):
    assert sd.available_years(sales) == [2019, 2020]
    assert sd.available_locations(sales) == [sd.ALL_LOCATIONS, "Kadıköy"]


def test_top_n_by_is_sorted_and_limited(sales):
    top = sd.top_n_by(sales, 2020, sd.ALL_LOCATIONS, sd.MANUFACTURER, n=2)
    assert list(top[sd.MANUFACTURER]) == ["SULTANLAR TIBET*", "VESTEL"]
    assert list(top[sd.SALES]) == [240.0, 60.0]


def test_top_n_by_respects_location(sales):
    top = sd.top_n_by(sales, 2020, "Kadıköy", sd.MANUFACTURER)
    assert list(top[sd.MANUFACTURER]) == ["ÜLKER"]


def test_sales_by_group_fills_missing_groups_with_zero(sales):
    totals = sd.sales_by_group(sales, 2020, sd.ALL_LOCATIONS,
                               ["GIDA", "GIDA DIŞI", "KOZMETIK"])
    assert totals.to_dict() == {"GIDA": 200.0, "GIDA DIŞI": 100.0, "KOZMETIK": 0.0}


def test_monthly_sales_is_in_calendar_order(sales):
    monthly = sd.monthly_sales(sales, 2020, sd.ALL_LOCATIONS)
    assert list(monthly[sd.MONTH]) == ["January", "February", "December"]


def test_monthly_sales_for_one_manufacturer(sales):
    monthly = sd.monthly_sales(sales, 2019, sd.ALL_LOCATIONS,
                               manufacturer="SULTANLAR TIBET*")
    assert list(monthly[sd.MONTH]) == ["January", "March"]
    assert set(monthly[sd.MANUFACTURER]) == {"SULTANLAR TIBET*"}


def test_yearly_kpis(sales):
    kpis = sd.yearly_kpis(sales, 2020)
    assert kpis["current"] == 370.0
    assert kpis["previous"] == 180.0
    assert math.isclose(kpis["growth"], (370 - 180) / 180 * 100)


def test_yearly_kpis_first_year_has_no_comparison(sales):
    kpis = sd.yearly_kpis(sales, 2019)
    assert kpis["current"] == 180.0
    assert math.isnan(kpis["previous"]) and math.isnan(kpis["growth"])


def test_table_records_are_json_friendly(sales):
    records = sd.table_records(sales, 2019, sd.ALL_LOCATIONS)
    assert len(records) == 3
    assert list(records[0]) == sd.TABLE_COLUMNS
    assert records[0][sd.START_DATE] == "2019-01-01"
