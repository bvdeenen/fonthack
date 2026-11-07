"""Build a WOFF2 font whose digit glyphs are permuted to undo hack.encode().

Usage: uv run --with 'fonttools[woff]' python make_font.py
"""
import io
import zipfile

from fontTools.ttLib import TTFont

from hack import REAL, ENCODED, encode

SRC_ZIP = "manrope-v23-latin.zip"
SRC_NAME = "manrope-v23-latin-regular.woff2"
OUT = "manrope-obf.woff2"
FAMILY = "Manrope Obf"


def load_source() -> TTFont:
    with zipfile.ZipFile(SRC_ZIP) as z:
        return TTFont(io.BytesIO(z.read(SRC_NAME)))


def remap_cmap(font: TTFont) -> None:
    # Snapshot once: subtables may share the same dict object, so remapping
    # each one from its own (already modified) state would apply it twice.
    orig = font.getBestCmap().copy()
    for sub in font["cmap"].tables:
        if not sub.isUnicode():
            continue
        for real, enc in zip(REAL, ENCODED):
            sub.cmap[ord(enc)] = orig[ord(real)]


def rename(font: TTFont) -> None:
    name = font["name"]
    ps = FAMILY.replace(" ", "") + "-Regular"
    for rec in name.names:
        if rec.nameID in (1, 16):
            rec.string = FAMILY
        elif rec.nameID == 4:
            rec.string = FAMILY + " Regular"
        elif rec.nameID in (3, 6):
            rec.string = ps


def verify(path: str) -> None:
    orig = load_source().getBestCmap()
    new = TTFont(path).getBestCmap()
    for real, enc in zip(REAL, ENCODED):
        assert new[ord(enc)] == orig[ord(real)], (real, enc)
    for cp, g in orig.items():
        if chr(cp) not in REAL:
            assert new[cp] == g, chr(cp)
    print(f"verified {path}: {''.join(ENCODED)} renders as {''.join(REAL)}")


def main() -> None:
    font = load_source()
    remap_cmap(font)
    rename(font)
    font.flavor = "woff2"
    font.save(OUT)
    verify(OUT)
    print("example: real 0612345789 -> html", encode("0612345789"))


if __name__ == "__main__":
    main()
