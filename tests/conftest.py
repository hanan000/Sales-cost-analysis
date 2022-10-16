import pandas as pd
import pytest

import sales_data as sd


def _row(manufacturer, group, subgroup, unit, amount, start, location=" Tüm Lokasyonlar"):
    return {
        "Üretici Adı": manufacturer, "Ürün Grubu": group,
        "Ürün Açıklama": f"{subgroup} ürünü", "Ürün Grup": subgroup,
        "Birim": unit, "Satış Miktarı": 1, "Satış Fiyatı": amount,
        "Satış Tutarı": amount, "Birim Maliyeti": amount / 2,
        "Maliyet Tutar": amount / 2, "Kar Oranı": 50.0, "Kar Tutar": amount / 2,
        "Tarih": " 05.04.2021", "Lokasyon": location, "Başlangıç Tarihi": start,
        "Bitiş Tarihi": " 01.01.2019", "Maliyet Yöntemi": " Dönemsel Tartılı Ortalama",
        "KDV Durumu": " Hariç",
    }


@pytest.fixture
def raw_sales() -> pd.DataFrame:
    """A tiny export shaped like the real one, including summary rows and the
    leading-space padding the notebook's export leaves on report fields."""
    rows = [
        _row("SULTANLAR TIBET*", "GIDA", "TOZ ŞEKERLER", "ADET", 100.0, " 2019-01-01"),
        _row("SULTANLAR TIBET*", "GIDA", "TOZ ŞEKERLER", "KG", 50.0, " 2019-03-01"),
        _row("P&G*", "KOZMETIK", "TRAŞ ÜRÜNLERI", "ADET", 30.0, " 2019-02-01"),
        _row("SULTANLAR TIBET*", "GIDA", "ÇAYLAR", "ADET", 200.0, " 2020-01-01"),
        _row("SULTANLAR TIBET*", "GIDA DIŞI", "NALBUR", "ADET", 40.0, " 2020-12-01"),
        _row("VESTEL", "GIDA DIŞI", "DERİN DONDURUCU", "ADET", 60.0, " 2020-02-01"),
        _row("ÜLKER", "GIDA", "BİSKÜVİ", "ADET", 70.0, " 2020-02-01", location=" Kadıköy"),
        # Report summary rows that repeat amounts already counted above.
        _row("VESTEL", None, None, "Toplamlar", 60.0, " 2020-02-01"),
        _row(None, None, None, "Genel Toplam", 9999.0, " 2020-02-01"),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def sales(raw_sales) -> pd.DataFrame:
    return sd.clean_sales(raw_sales)
