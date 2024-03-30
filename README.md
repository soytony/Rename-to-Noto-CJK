# Rename to Noto CJK
Rename the font info in the metadata of your fonts, so they becomes a
substitute for the original Noto CJK fonts.


# Prerequisites

You should have fontforge installed.

```bash
apt install fontforge
apt install python3-fontforge
```

# Usage

Put your multi-weight ttf files under `input` folder, and rename them to
something like `${STYLE}.ttf`, where `${STYLE}` can be anything from `["Regular",
"Thin", "Light", "Medium", "Bold", "Black"]`.

Run `python3 rename_fonts.py`. The renamed fonts will be saved to `./output` folder.
