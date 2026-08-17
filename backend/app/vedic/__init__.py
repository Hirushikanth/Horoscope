"""
vedic — pure Vedic domain logic (zero astronomy).

Builds on the ``astronomy`` layer: takes sidereal longitudes and times
and produces the Thirukanitha jathakam domain values — nakshatras,
rashis, the panchangam, divisional charts, whole-sign houses, Vimshottari
dasha, dignity, yogas and doshas. All arithmetic is IEEE 754 float64 and
every module cites its reference document.

Phase B surface: tables, nakshatra, rashi, panchangam, charts, bhavas,
dasha, dignity, yogas, doshas.
"""

from app.vedic.bhavas import Bhava, get_bhava_of_longitude, get_house_number, get_whole_sign_bhavas
from app.vedic.charts import (
    Varga,
    VargaPosition,
    get_dasamsa_position,
    get_dwadasamsa_position,
    get_navamsa_position,
    get_shashtiamsa_position,
    get_trimsamsa_position,
    get_varga_position,
    is_vargottama,
)
from app.vedic.dasha import (
    DashaPeriod,
    VimshottariBalance,
    vimshottari_balance,
    vimshottari_timeline,
)
from app.vedic.dignity import Dignity, DignityAssessment, assess_dignity
from app.vedic.doshas import ChevvaiDoshamReport, assess_chevvai_dosham
from app.vedic.nakshatra import (
    Gana,
    Nadi,
    Rajju,
    Yoni,
    get_nakshatra_gana,
    get_nakshatra_index,
    get_nakshatra_lord,
    get_nakshatra_nadi,
    get_nakshatra_pada_index,
    get_nakshatra_rajju,
    get_nakshatra_yoni,
    is_vedha_pair,
    yonis_are_enemies,
)
from app.vedic.panchangam import (
    Paksha,
    get_daily_almanac,
    get_karana_id,
    get_karana_sequence_index,
    get_tithi_index,
    get_tithi_paksha,
    get_udaya_day,
    get_vara_index,
    get_yoga_index,
)
from app.vedic.rashi import (
    MaitriRelation,
    VashyaGroup,
    get_maitri_relation,
    get_mutual_maitri,
    get_rasi_index,
    get_rasi_lord,
    get_vashya_group,
)
from app.vedic.tables import (
    GRAHA_NAMES,
    KARANA_NAMES,
    RASI_NAMES,
    TITHI_NAMES,
    VARA_NAMES,
    YOGA_NAMES,
    Graha,
    Rasi,
    TrilingualName,
    Vara,
    get_karana_name,
    get_tithi_name,
    get_yoga_name,
)
from app.vedic.yogas import YogaResult, detect_yogas

__all__ = [
    # identity + names
    "Graha",
    "Rasi",
    "Vara",
    "TrilingualName",
    "GRAHA_NAMES",
    "RASI_NAMES",
    "VARA_NAMES",
    "TITHI_NAMES",
    "YOGA_NAMES",
    "KARANA_NAMES",
    "get_tithi_name",
    "get_yoga_name",
    "get_karana_name",
    # nakshatra
    "Gana",
    "Nadi",
    "Rajju",
    "Yoni",
    "get_nakshatra_index",
    "get_nakshatra_pada_index",
    "get_nakshatra_lord",
    "get_nakshatra_gana",
    "get_nakshatra_yoni",
    "get_nakshatra_nadi",
    "get_nakshatra_rajju",
    "is_vedha_pair",
    "yonis_are_enemies",
    # rashi
    "VashyaGroup",
    "MaitriRelation",
    "get_rasi_index",
    "get_rasi_lord",
    "get_vashya_group",
    "get_maitri_relation",
    "get_mutual_maitri",
    # panchangam
    "Paksha",
    "get_tithi_index",
    "get_tithi_paksha",
    "get_yoga_index",
    "get_karana_sequence_index",
    "get_karana_id",
    "get_vara_index",
    "get_udaya_day",
    "get_daily_almanac",
    # charts
    "Varga",
    "VargaPosition",
    "get_varga_position",
    "get_navamsa_position",
    "get_dasamsa_position",
    "get_dwadasamsa_position",
    "get_trimsamsa_position",
    "get_shashtiamsa_position",
    "is_vargottama",
    # bhavas
    "Bhava",
    "get_house_number",
    "get_bhava_of_longitude",
    "get_whole_sign_bhavas",
    # dasha
    "VimshottariBalance",
    "DashaPeriod",
    "vimshottari_balance",
    "vimshottari_timeline",
    # dignity / yogas / doshas
    "Dignity",
    "DignityAssessment",
    "assess_dignity",
    "YogaResult",
    "detect_yogas",
    "ChevvaiDoshamReport",
    "assess_chevvai_dosham",
]
