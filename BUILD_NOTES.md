# Build notes — The Shape of the Threat

This file records how the book is produced and what was repaired on the way, so that
a later edition can be rebuilt from the same materials and so that a reader who
doubts a number can find where it was computed. It is production documentation and
is deliberately not part of the book.

## Pipeline

```sh
./build.sh            # the book
build/make_covers.sh  # the covers (separate documents)
```

`build.sh` runs, in order:

1. `build/compute_numbers.py` — the single number generator. Eighteen sections: the
   CAPS re-derivation, the size conventions, the thermal channel, the Yarkovsky and
   YORP scaling, the keyhole propagation, the catalogue statistics, the AMAS lead-time
   inversion, the Earth–Moon two-station range, the detection records, the service
   rate, the accountability ladder, the counterfactual cases and the worked cases.
2. the word count, from the book's own LaTeX source with the control words stripped.
3. `build/make_figures.py` — the fourteen charts.
4. `build/make_appendix_tables.py` — the seven appendix tables, written from the
   generator's own JSON output into `source/generated/`.
5. XeLaTeX twice, `makeindex`, XeLaTeX twice.
6. the page count, then `source/generated.tex` is rewritten with the real page and
   word counts, then XeLaTeX twice more.
7. the PDF is copied to `output/The-Shape-of-the-Threat.pdf`.

`python3 build/verify.py` runs the seventeen gates against the finished PDF.
`python3 build/check_numbers.py` asserts that the manuscript's headline numbers still
agree with the generator.

## One generator per artefact

Every figure and every appendix table has exactly one generator, and the generators
are never chained. A second copy of a generator is a race that fires in the wrong
order, and on an earlier book that is exactly what overwrote good figures with broken
ones. `source/generated/` is written only by `build/make_appendix_tables.py`, and
`figures/fig_*.pdf` only by `build/make_figures.py`.

## The number rule

No headline number is transcribed. It is computed by `build/compute_numbers.py`,
rendered into the manuscript at the value the generator produces, and printed in full
in Appendix B. Where a value is rounded, it is rounded in the direction the generator
gives. `build/check_numbers.py` is the mechanical guard: it pulls 48 quantities out
of the generator, formats each the way the book writes it, and asserts that the
string is present in the manuscript.

That check earned its keep on this build. It caught the contrast of a 390 K target
against sunlit regolith at 1.0 AU: the manuscript and the research ledger carried
0.056, but the generator's value is 0.05545, which rounds to 0.055. The error
originated in the ledger and was inherited by the book; both were corrected.

## Repairs made during the build

These are recorded because each was a class of error worth not repeating.

**Heading arguments.** Twenty section headings were missing their closing brace, and
three more had it on a following line with a blank line between, which LaTeX reports
as "Paragraph ended before \@sect was complete". A normalisation pass intended to join
heading arguments onto one line mis-read the closing brace of every heading and
damaged 193 of them; the manuscript was recovered from the damaged state by
`build/repair_headings.py`, and the recovery was checked by comparing every file
against the damaged copy with all braces and whitespace removed: **zero text
differences**. The lesson is that a repair script needs a test that it did not change
the prose, and that script needed one too.

**Table measures.** Several tables were written with fixed column widths that added up
to more than the 4.6-inch measure leaves after the column separations, so the
prose column was squeezed to a few points. `build/fix_tables.py` rebalances the
column specifications; the preamble declares `P` and `Y` column types so that prose
inside a table is set ragged right. Two tables were corrected by hand because no
automatic balance fits them: the CAPS re-derivation table in Appendix A became a
natural-width `tabular`, and the prior-art map in Chapter 32 was rewritten with the
verified identifiers instead of prose descriptions.

**The column parser.** The rebalancer's pattern for a column type required a word
boundary, so two adjacent `X` columns were silently reduced to one. Three tables lost
a column that way. The table now carries a check that compares each table's header
cell count against its column specification; it reports zero mismatches.

**Float heights and the safe area.** Four tables were too tall for a page and three
too wide for the measure; they were set in footnotesize, split, or rebuilt. The
complete generated number set was split into two tables of twenty-three rows each.
The colophon was pushed onto a second page by its own leading space, which left a
blank page behind it; the space was reduced.

**The table of contents against the PDF outline.** The book has seven subsections and
the PDF outline did not carry them, because the bookmark depth followed the contents
depth. The contents depth was set to two and the bookmark depth to three, so the two
now agree at 191 entries.

## What the build does not do

- It does not run `build/fix_tables.py` or `build/repair_headings.py`. Both are
  one-time repairs, not build steps: running them on a healthy tree would modify the
  manuscript for no reason.
- It does not build the covers. `build/make_covers.sh` does that, because the cover is
  a separate LaTeX document with its own geometry and its own two-pass anchor
  resolution.
- It does not check the prose. The gates check the typesetting; `check_numbers.py`
  checks the numbers; nothing here can tell you that a sentence is wrong.

## The cover

The cover artwork is generated, not licensed: `build/make_cover_source_art.py` draws
the original plate, `build/make_cover_art.py` bakes the legibility scrim into a
300 DPI JPEG, and `source/cover_front.tex` and `source/cover_back.tex` set the
typography over it in the book's own fonts. The style was drawn from the fixed pool
of fourteen with a seed derived from the title, and the draw is recorded in
`research/cover_draw.json`: *vintage NASA poster*, seed 1623370500.

The plate is flat by design — no spine, no binding, no page edges, no perspective
tilt — and full bleed at 2:3. There is no watermark and no service attribution
anywhere on it.

## Toolchain

XeLaTeX with `fontspec` and `unicode-math`; `makeindex`; Python 3 with matplotlib,
Pillow and numpy; `pdftotext`, `pdftoppm`, `pdfinfo` and `pdffonts` for the gates.
Fonts in `fonts/`: Outfit for text, DejaVu Sans Mono for code, XCharter Math for the
mathematics.
