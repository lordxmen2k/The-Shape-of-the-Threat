#!/bin/sh
# Build the front and back covers.
#
# The plates are prepared as 300 DPI JPEGs and the typography is set in
# LaTeX, so the finished cover is vector text over a DCTDecode JPEG. That
# keeps the file small and makes the cover typography identical to the
# book's own.
#
# Usage: ./build/make_covers.sh
set +e
cd "$(dirname "$0")/.."
ROOT=$(pwd)

mkdir -p "$HOME/.fonts"
cp fonts/Outfit-*.ttf fonts/DejaVuSansMono-*.ttf "$HOME/.fonts/" 2>/dev/null || true
fc-cache -f >/dev/null 2>&1 || true

# 0. the source artwork
python3 build/make_cover_source_art.py || exit 1

# 1. the plates
python3 build/make_cover_art.py || exit 1

# 2. the typography
for name in cover_front cover_back; do
  # two runs: the page anchors used by remember picture only resolve on
  # the second pass
  ( cd source && xelatex -interaction=nonstopmode -halt-on-error "$name.tex" >/dev/null \
    && xelatex -interaction=nonstopmode -halt-on-error "$name.tex" >/dev/null ) || {
    echo "FAILED: $name"; exit 1; }
  cp "source/$name.pdf" "figures/$name.pdf"
  # 300 DPI raster copy for anyone who needs one
  pdftoppm -png -r 300 -singlefile "figures/$name.pdf" "figures/$name"
  echo "wrote figures/$name.pdf and figures/$name.png"
done
