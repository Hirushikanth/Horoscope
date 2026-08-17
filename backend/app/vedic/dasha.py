"""
dasha.py — Vimshottari Dasa: Mahadasa / Antardasa / Pratyantardasa.

The Vimshottari is the standard planetary-period timeline, built
entirely from the Moon's Janma Nakshatra. The 120-year cycle divides
unevenly among the nine grahas in a fixed order; the balance of the
first Mahadasa at birth is the fraction of the birth nakshatra yet to be
traversed, scaled by the lord's years.

The year length is switchable: the docs note that Tamil practice
commonly treats 1 year = 360 days, while modern software (and the
previous app engine) uses 365.25 days. 365.25 is the default; 360 is
available via ``year_length_days``.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §11 (Vimshottari)
    - docs/south-indian-horoscope.md                 §3.7 (dasa-bhukti)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from app.vedic.nakshatra import NAKSHATRA_SPAN_DEG, get_nakshatra_index
from app.vedic.tables import Graha

#: Vimshottari lord order — also the repeating nakshatra-lord sequence.
VIMSHOTTARI_SEQUENCE: tuple[Graha, ...] = (
    Graha.KETU,
    Graha.SUKRA,
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.CHEVVAI,
    Graha.RAHU,
    Graha.GURU,
    Graha.SANI,
    Graha.BUDHA,
)

#: Full Mahadasa years of each graha (the cycle totals 120 years).
VIMSHOTTARI_YEARS: dict[Graha, np.float64] = {
    Graha.KETU: np.float64(7.0),
    Graha.SUKRA: np.float64(20.0),
    Graha.SURYA: np.float64(6.0),
    Graha.CHANDRA: np.float64(10.0),
    Graha.CHEVVAI: np.float64(7.0),
    Graha.RAHU: np.float64(18.0),
    Graha.GURU: np.float64(16.0),
    Graha.SANI: np.float64(19.0),
    Graha.BUDHA: np.float64(17.0),
}

#: Sum of the full Mahadasa years — one complete Vimshottari cycle.
VIMSHOTTARI_TOTAL_YEARS: np.float64 = np.float64(120.0)

#: Default year length in days (365.25 — modern software convention).
DEFAULT_YEAR_LENGTH_DAYS: np.float64 = np.float64(365.25)
#: Tamil traditional year length in days.
TAMIL_YEAR_LENGTH_DAYS: np.float64 = np.float64(360.0)


@dataclass(frozen=True)
class VimshottariBalance:
    """Balance of the first Mahadasa at birth.

    Attributes:
        lord: Graha ruling the birth nakshatra — the first Mahadasa lord.
        balance_years: Fraction of the lord's full years remaining at
            birth, in year units.
        fraction_remaining: Fraction of the nakshatra yet to be
            traversed by the Moon (0–1).
    """

    lord: Graha
    balance_years: np.float64
    fraction_remaining: np.float64


@dataclass(frozen=True)
class DashaPeriod:
    """One Vimshottari period on the timeline.

    Attributes:
        graha: The period's graha.
        category: ``mahadasha``, ``antardasha`` or ``pratyantardasha``.
        parent_index: Index of the parent period in the returned list
            (``None`` for mahadashas).
        years: Duration in year units (of the configured year length).
        days: Duration in days (``years × year_length_days``).
        start_jd: Start Julian day (UT1 scale).
        end_jd: End Julian day (UT1 scale).
    """

    graha: Graha
    category: Literal["mahadasha", "antardasha", "pratyantardasha"]
    parent_index: int | None
    years: np.float64
    days: np.float64
    start_jd: np.float64
    end_jd: np.float64


def vimshottari_balance(moon_sidereal_lon: np.float64) -> VimshottariBalance:
    """Balance of the first Mahadasa at birth.

    The Moon's Janma Nakshatra fixes the first Mahadasa lord; the
    balance is the un-travelled fraction of the nakshatra scaled by the
    lord's full years:

        Balance = [(13°20′ − travelled) / 13°20′] × lord_years

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §11
    """
    nakshatra_index = get_nakshatra_index(moon_sidereal_lon)
    lord = VIMSHOTTARI_SEQUENCE[nakshatra_index % 9]
    travelled = np.float64(moon_sidereal_lon) % NAKSHATRA_SPAN_DEG
    fraction_remaining = (NAKSHATRA_SPAN_DEG - travelled) / NAKSHATRA_SPAN_DEG
    balance_years = fraction_remaining * VIMSHOTTARI_YEARS[lord]
    return VimshottariBalance(
        lord=lord,
        balance_years=balance_years,
        fraction_remaining=fraction_remaining,
    )


def _subperiod_duration(parent_years: np.float64, sub_lord: Graha) -> np.float64:
    """Duration (in year units) of a sub-period within a parent period.

    Each Antardasa is proportional to the Mahadasa: ``MD × lord_years /
    120``; each Pratyantardasa likewise to its Antardasa.
    """
    return parent_years * VIMSHOTTARI_YEARS[sub_lord] / VIMSHOTTARI_TOTAL_YEARS


def vimshottari_timeline(
    start_jd: np.float64,
    moon_sidereal_lon: np.float64,
    *,
    depth: int = 3,
    year_length_days: float = 365.25,
    minimum_span_years: float = 120.0,
) -> list[DashaPeriod]:
    """Vimshottari timeline starting at the birth instant.

    Parameters:
        start_jd: Birth Julian day (UT1 scale) — where the balance
            period begins.
        moon_sidereal_lon: Moon's sidereal longitude at birth.
        depth: 1 = mahadashas only, 2 = + antardashas, 3 = +
            pratyantardashas.
        year_length_days: Length of one year in days — 365.25 (default)
            or 360 (Tamil traditional).
        minimum_span_years: Mahadashas are generated until the timeline
            spans at least this many years (120 covers a full cycle).

    Returns:
        Chronological list of ``DashaPeriod`` covering the full cycle.
    """
    if depth not in (1, 2, 3):
        raise ValueError(f"depth must be 1, 2 or 3, got {depth}")
    year_length = np.float64(year_length_days)

    balance = vimshottari_balance(moon_sidereal_lon)
    start_lord_index = VIMSHOTTARI_SEQUENCE.index(balance.lord)

    # Mahadasas: balance period first, then full periods, until the span
    # reaches the minimum. The cycle order continues from the balance lord.
    md_periods: list[tuple[Graha, np.float64, int]] = []
    cumulative_years = np.float64(0.0)
    offset = 0
    while cumulative_years < np.float64(minimum_span_years):
        lord_index = (start_lord_index + offset) % 9
        lord = VIMSHOTTARI_SEQUENCE[lord_index]
        years = balance.balance_years if offset == 0 else VIMSHOTTARI_YEARS[lord]
        md_periods.append((lord, years, offset))
        cumulative_years += years
        offset += 1

    periods: list[DashaPeriod] = []
    md_cursor_jd = np.float64(start_jd)

    for lord, years, md_offset in md_periods:
        md_index = len(periods)
        md_days = years * year_length
        md = DashaPeriod(
            graha=lord,
            category="mahadasha",
            parent_index=None,
            years=years,
            days=md_days,
            start_jd=md_cursor_jd,
            end_jd=md_cursor_jd + md_days,
        )
        periods.append(md)
        md_cursor_jd = md.end_jd

        if depth >= 2:
            ad_cursor_jd = md.start_jd
            for ad_offset in range(9):
                ad_lord = VIMSHOTTARI_SEQUENCE[(start_lord_index + md_offset + ad_offset) % 9]
                ad_years = _subperiod_duration(years, ad_lord)
                ad_days = ad_years * year_length
                ad_index = len(periods)
                ad = DashaPeriod(
                    graha=ad_lord,
                    category="antardasha",
                    parent_index=md_index,
                    years=ad_years,
                    days=ad_days,
                    start_jd=ad_cursor_jd,
                    end_jd=ad_cursor_jd + ad_days,
                )
                periods.append(ad)
                ad_cursor_jd = ad.end_jd

                if depth >= 3:
                    pd_cursor_jd = ad.start_jd
                    for pd_offset in range(9):
                        pd_lord = VIMSHOTTARI_SEQUENCE[
                            (start_lord_index + md_offset + ad_offset + pd_offset) % 9
                        ]
                        pd_years = _subperiod_duration(ad_years, pd_lord)
                        pd_days = pd_years * year_length
                        pd = DashaPeriod(
                            graha=pd_lord,
                            category="pratyantardasha",
                            parent_index=ad_index,
                            years=pd_years,
                            days=pd_days,
                            start_jd=pd_cursor_jd,
                            end_jd=pd_cursor_jd + pd_days,
                        )
                        periods.append(pd)
                        pd_cursor_jd = pd.end_jd

    return periods


def balance_years_to_days(balance_years: np.float64, year_length_days: float) -> np.float64:
    """Convert fractional balance years to days for the chosen year length."""
    return np.float64(balance_years) * np.float64(year_length_days)
