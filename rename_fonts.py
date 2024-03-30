import gc
import os
import logging
from tqdm import tqdm
from typing import List

import fontforge as ff
from fontforge import font as FontType
from otf2otc import run as run_otf2otc

_FONT_COPYRIGHT = "© 2014-2021 Adobe (http://www.adobe.com/)."
_FONT_VERSION = "Version 2.004;hotconv 1.0.118;makeotfexe 2.5.65603"
_FONT_TRADEMARK = "Noto is a trademark of Google Inc."
_FONT_MANUFACTURER = "Adobe"
_FONT_DESIGNER = "Ryoko NISHIZUKA 西塚涼子 (kana, bopomofo &amp; ideographs); Paul D. Hunt (Latin, Greek &amp; Cyrillic); Sandoll Communications 산돌커뮤니케이션, Soo-young JANG 장수영 &amp; Joo-yeon KANG 강주연 (hangul elements, letters &amp; syllables)"
_FONT_DESCRIPTION = "Dr. Ken Lunde (project architect, glyph set definition &amp; overall production); Masataka HATTORI 服部正貴 (production &amp; ideograph elements)"
_FONT_VENDOR_URL = "http://www.google.com/get/noto/"
_FONT_DESIGNER_URL = "http://www.adobe.com/type/"
_FONT_LICENSE_DESCRIPTION = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This Font Software is distributed on an &quot;AS IS&quot; BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the SIL Open Font License for the specific language, permissions and limitations governing your use of this Font Software."
_FONT_LICENSE_INFO = "http://scripts.sil.org/OFL"


_STYLES = ["Regular", "Thin", "Light", "Medium", "Bold", "Black"]
_REGIONS = ["JP", "KR", "SC", "TC", "HK"]

_INPUT_DIR = "./input"
_OUTPUT_DIR = "./output"
_TTF_OUTPUT_DIR = os.path.join(_OUTPUT_DIR, "ttf")
_TTC_OUTPUT_DIR = os.path.join(_OUTPUT_DIR, "ttc")

logger = logging.getLogger(__file__)


def open_font(path: str):
    """
    Loads the given font.
    """
    return ff.open(path)


def remove_gasp(font: FontType):
    """
    Removes gasp for the given font.
    """
    font.gasp = ()


def set_font_name(font: FontType, region: str, style: str):
    """
    Renames the font names.
    """
    # PostscriptName.
    region_lc = region.lower()
    font.fontname = f"NotoSansCJK{region_lc}-{style}"
    # Style is dropped in FullName for Regular.
    font.fullname = (
        f"Noto Sans CJK {region}"
        if style == "Regular"
        else f"Noto Sans CJK {region} {style}"
    )
    if style in ["Regular", "Bold"]:
        font.familyname = f"Noto Sans CJK {region}"
        font_subfamily = style
        font_preferredfamily = None
        font_preferredsubfamily = None
    else:
        font.familyname = f"Noto Sans CJK {region} {style}"
        # For styles other than Regular and Bold, their SubFamily should always be 'Regular'.
        font_subfamily = "Regular"
        font_preferredfamily = f"Noto Sans CJK {region}"
        font_preferredsubfamily = style

    font.version = _FONT_VERSION
    font.copyright = _FONT_COPYRIGHT
    font_unique_id = f"2.004;GOOG;NotoSansCJK{region_lc}-{style};ADOBE"
    font_sfnt_name_list = [
        ("English (US)", "Family", font.familyname),
        ("English (US)", "Fullname", font.fullname),
        ("English (US)", "UniqueID", font_unique_id),
        ("English (US)", "SubFamily", font_subfamily),
        ("English (US)", "Version", font.version),
        ("English (US)", "Copyright", font.copyright),
        ("English (US)", "Trademark", _FONT_TRADEMARK),
        ("English (US)", "Manufacturer", _FONT_MANUFACTURER),
        ("English (US)", "Designer", _FONT_DESIGNER),
        # ('English (US)', 'Description', _FONT_DESCRIPTION),
        # ('English (US)', 'VendorURL', _FONT_VENDOR_URL),
        # ('English (US)', 'DesignerURL', _FONT_DESIGNER_URL),
        # ('English (US)', 'LicenseDescription', _FONT_LICENSE_DESCRIPTION),
        # ('English (US)', 'LicenseInfo', _FONT_LICENSE_INFO),
    ]

    if font_preferredfamily is not None and font_preferredsubfamily is not None:
        font_sfnt_name_list.append(
            ("English (US)", "Preferred Family", font_preferredfamily)
        )
        font_sfnt_name_list.append(
            ("English (US)", "Preferred Styles", font_preferredsubfamily)
        )

    font.sfnt_names = tuple(font_sfnt_name_list)


def make_ttc(ttf_paths: List[str], output_ttc_path: str):
    """
    Merges a list of ttf files into one ttc file.
    """
    args: List[str] = []
    args.append("-o")
    args.append(output_ttc_path)
    for ttf_path in ttf_paths:
        args.append(ttf_path)

    run_otf2otc(args)


def rename_fonts():
    """
    Renames the fonts.
    """
    for style in tqdm(_STYLES):
        ttf_paths: List[str] = []
        font_path = os.path.join(_INPUT_DIR, f"{style}.ttf")
        logger.info("Loading font from: {}.".format(font_path))
        if not os.path.isfile(font_path):
            logger.error(
                "Cannot find font file {}. Skipping style {}.".format(font_path, style)
            )
            continue

        font = open_font(font_path)
        remove_gasp(font)

        for region in _REGIONS:
            set_font_name(font, region=region, style=style)
            pass

            output_font_path = os.path.join(
                _TTF_OUTPUT_DIR, f"NotoSansCJK{region.lower()}-{style}.ttf"
            )
            ttf_paths.append(output_font_path)
            font.generate(output_font_path)

        del font
        gc.collect()

        ttc_path = os.path.join(_TTC_OUTPUT_DIR, f"NotoSansCJK-{style}.ttc")
        logger.info(
            "Generating ttc file for style {}. Ttc file will be "
            "exported to: {}.".format(style, ttc_path)
        )
        make_ttc(ttf_paths, ttc_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        filemode="w",
        format="%(levelname)s:%(asctime)s:%(message)s",
        datefmt="%Y-%d-%m %H:%M:%S",
    )

    os.makedirs(_INPUT_DIR, exist_ok=True)
    os.makedirs(_TTF_OUTPUT_DIR, exist_ok=True)
    os.makedirs(_TTC_OUTPUT_DIR, exist_ok=True)

    rename_fonts()
