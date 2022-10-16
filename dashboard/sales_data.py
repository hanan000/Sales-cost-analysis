"""Loading, cleaning and aggregating the supermarket sales data.

The input is the combined CSV produced by ``sales-cost-analysis.ipynb``
(``concat_all_files_.csv``). Every function here is pure pandas so it can be
tested without running the Dash app.
"""
from __future__ import annotations

import calendar
import math
from pathlib import Path

import pandas as pd

# Column names (the source reports are in Turkish).
SALES = "Satış Tutarı"
YEAR = "Yıl"
MONTH = "Ay"
MONTH_NO = "Ay No"
LOCATION = "Lokasyon"
START_DATE = "Başlangıç Tarihi"
UNIT = "Birim"
MANUFACTURER = "Üretici Adı"
PRODUCT_GROUP = "Ürün Grubu"  # top-level category, e.g. GIDA, KOZMETIK
PRODUCT_SUBGROUP = "Ürün Grup"  # finer category, e.g. TOZ ŞEKERLER

ALL_LOCATIONS = "Tüm Lokasyonlar"

# The exported reports contain subtotal / grand-total rows mixed in with the
# item rows. They repeat amounts that are already counted, so they are dropped.
SUMMARY_ROW_UNITS = ("Toplamlar", "Genel Toplam")

# Report-header columns that were copied onto every row and carry padding.
_TEXT_COLUMNS = (LOCATION, START_DATE, "Tarih", "Bitiş Tarihi",
                 "Maliyet Yöntemi", "KDV Durumu")

TABLE_COLUMNS = [
    "Üretici Adı", "Ürün Grubu", "Ürün Açıklama", "Ürün Grup", "Birim",
    "Satış Miktarı", "Satış Fiyatı", "Satış Tutarı", "Birim Maliyeti",
    "Maliyet Tutar", "Kar Oranı", "Kar Tutar", "Tarih", "Lokasyon",
    "Başlangıç Tarihi", "Bitiş Tarihi", "Maliyet Yöntemi", "KDV Durumu",
]

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "concat_all_files_.csv"


def load_sales(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Read the combined sales CSV and return a cleaned frame."""
    return clean_sales(pd.read_csv(path, low_memory=False))


def clean_sales(raw: pd.DataFrame) -> pd.DataFrame:
    """Drop summary rows, normalise text and add year / month columns."""
    sales = raw[~raw[UNIT].isin(SUMMARY_ROW_UNITS)].copy()

    for column in _TEXT_COLUMNS:
        if column in sales.columns:
            sales[column] = sales[column].astype("string").str.strip()

    sales[SALES] = pd.to_numeric(sales[SALES], errors="coerce")
    dates = pd.to_datetime(sales[START_DATE], format="ISO8601", errors="coerce")
    sales = sales[dates.notna()].copy()
    dates = dates[dates.notna()]
    sales[START_DATE] = dates
    sales[YEAR] = dates.dt.year.astype(int)
    sales[MONTH_NO] = dates.dt.month.astype(int)
    sales[MONTH] = sales[MONTH_NO].map(lambda m: calendar.month_name[m])
    return sales


def available_years(sales: pd.DataFrame) -> list[int]:
    return sorted(int(year) for year in sales[YEAR].dropna().unique())


def available_locations(sales: pd.DataFrame) -> list[str]:
    return list(sales[LOCATION].dropna().unique())


def filter_sales(sales: pd.DataFrame, year: int, location: str | None = None) -> pd.DataFrame:
    """Rows for one year, optionally restricted to one location."""
    mask = sales[YEAR] == year
    if location is not None:
        mask &= sales[LOCATION] == location
    return sales[mask]


def top_n_by(sales: pd.DataFrame, year: int, location: str, column: str,
             n: int = 5) -> pd.DataFrame:
    """The ``n`` values of ``column`` with the highest sales, largest first."""
    totals = (filter_sales(sales, year, location)
              .groupby([YEAR, column, LOCATION])[SALES].sum().reset_index())
    return totals.nlargest(n, columns=SALES).reset_index(drop=True)


def sales_by_group(sales: pd.DataFrame, year: int, location: str,
                   groups: list[str], column: str = PRODUCT_GROUP) -> pd.Series:
    """Total sales for each of ``groups`` (zero when a group has no sales)."""
    totals = filter_sales(sales, year, location).groupby(column)[SALES].sum()
    return totals.reindex(groups, fill_value=0.0)


def monthly_sales(sales: pd.DataFrame, year: int, location: str,
                  manufacturer: str | None = None) -> pd.DataFrame:
    """Sales per month in calendar order (January first)."""
    rows = filter_sales(sales, year, location)
    keys = [YEAR, MONTH_NO, MONTH, LOCATION]
    if manufacturer is not None:
        rows = rows[rows[MANUFACTURER] == manufacturer]
        keys = [YEAR, MONTH_NO, MONTH, MANUFACTURER, PRODUCT_GROUP]
    return (rows.groupby(keys)[SALES].sum().reset_index()
            .sort_values(MONTH_NO).reset_index(drop=True))


def yearly_kpis(sales: pd.DataFrame, year: int) -> dict[str, float]:
    """Sales for ``year``, the previous year and year-over-year growth (%).

    ``previous`` and ``growth`` are NaN when there is no earlier year.
    """
    yearly = sales.groupby(YEAR)[SALES].sum()
    current = float(yearly.get(year, 0.0))
    previous = float(yearly.get(year - 1, math.nan))
    if math.isnan(previous) or previous == 0:
        growth = math.nan
    else:
        growth = (current - previous) / previous * 100
    return {"current": current, "previous": previous, "growth": growth}


def table_records(sales: pd.DataFrame, year: int, location: str) -> list[dict]:
    """Rows for the data table, with dates rendered as ISO strings."""
    rows = filter_sales(sales, year, location)[TABLE_COLUMNS].copy()
    rows[START_DATE] = rows[START_DATE].dt.strftime("%Y-%m-%d")
    rows = rows.astype(object).where(rows.notna(), None)  # NaN/NA -> JSON null
    return rows.to_dict("records")
