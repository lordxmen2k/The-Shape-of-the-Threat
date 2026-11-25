# The Shape of the Threat: Characterising Near-Earth Objects for Impact Accountability, and the Case for a Lunar Surface Array

Gerald Enrique Nelson Mc Kenzie — Tico Internet LLC
2026 First Edition · Apache License 2.0 · DOI 10.5281/zenodo.24517244

A PhD-level reference on the gap between what a near-Earth object catalogue records
and what a planetary-defence decision needs — and on the narrow, quantified case for
a fixed lunar surface array to close part of it.

## Contents

```
source/          the LaTeX manuscript
  preamble.tex   identity, design tokens, page furniture, table column types
  main.tex       the document spine: covers, front matter, body, back matter
  frontmatter.tex, body.tex, backmatter.tex
  chapters/      ch01.tex .. ch33.tex
  generated/     the appendix tables, written by the generator at build time
  cover_front.tex, cover_back.tex
figures/         the cover plates and the book's fourteen figures
build/           the number generator, the figure and cover scripts, the
                 verification gates
research/        the source ledger and the raw registry records behind it
output/          the finished PDF
```

## Building

```sh
./build.sh
```

Requires XeLaTeX, `makeindex`, Python 3 with matplotlib, Pillow and numpy, and the
fonts in `fonts/`.

The covers are built separately, because they are separate documents:

```sh
build/make_covers.sh
```

The verification gates run against the finished PDF, not against the build log:

```sh
python3 build/verify.py
```

## The argument

A near-Earth object catalogue entry carries a designation, orbital elements, an
absolute magnitude, sometimes an albedo, and a probability of impact that is usually
negligible. It carries no size, no mass, no shape, no spin state and no bulk density,
and therefore no energy and no hazard class. The impact energy that NASA CNEOS Sentry
publishes for a threatened object is stated to be good to within a factor of three,
and that is because the mass is unmeasured. The gap is not a detection gap: as of
22 November 2026 the catalogue held 43,212 known near-Earth objects, 11,725 of them
larger than about 140 metres, and the dangerous ones are already mostly found. On the
published characterisation figures, roughly 1,759 of those 11,725 objects have any
physical account at all and about 9,966 have none. **The gap for the hazard-relevant
class is accounting, not discovery.**

The book works the chain that closes that gap — shape to size to mass to energy to
hazard class — from first principles, and carries its own arithmetic rather than only
citing other people's. It re-derives the CAPS concept study's own baseline table
independently, to within 0.71 per cent on the maximum-baseline column, and shows that
the table's design point resolves a 50-metre object at 0.2 AU across 0.70 fringe
spacings: the instrument it describes is an astrometric centroider, not a shape
imager. It then states what shape imaging actually requires — four samples across the
diameter, which for a 140-metre object at 0.1 AU is a 321-metre baseline and for a
60-metre object at 0.5 AU is 3,740 metres — and draws the consequence. **The Moon is
the only site where a kilometre-scale stable baseline can be built and held still,
because at that length on the ground the same baseline is simultaneously an
atmospheric, a metrological and a thermal-expansion problem.**

The newest result in the book is the counterfactual: the claim that the lunar approach
would have measurably helped is tested against the historical record rather than
against a model of it. The record is in the NASA/JPL Small-Body Database and Close
Approach services. 2024 YR4 was catalogued on the night it passed at 828,775 km.
2019 OK was announced three days before it passed at 71,355 km. Both were found late
because they arrived from the Sun-ward side, not because the instruments were
inadequate. The honest answer is that the lunar station does not improve discovery;
what it does is convert a detection into an account. Three gains are measurable: the
Sun-ward discovery window, reconstructed from the published lunar lead times; the
optical range to a non-cooperative target on the Earth–Moon baseline, which is good
to 8.7 metres at YR4's discovery-night distance and to about 13 centimetres at a
1.5-kilometre baseline; and the size, at the same encounters.

The lunar claim is correspondingly narrowed, and the book states where it loses. The
mid-infrared channel loses to Sun–Earth L1 on cost and complexity, because sunlit
lunar regolith at 390 K radiates directly into the band in which asteroid thermal
emission is measured; the book therefore carries no mid-infrared channel. The station
cannot survey: at 37.4 campaigns a year it covers 10.9 per cent of the annual
arrival rate of the 140-metre class and would take 313 years to clear the known
population. It is a targeted service, selected by a rule, and the rule returns the
platform for a named target rather than an architecture.

**The deliverable is a platform selection rule with an error budget behind it, and a
bounded novelty claim:** the lunar interferometer is twenty-three years old and
heavily worked, and the contribution is the re-derived shape-imaging requirement, the
Earth–Moon two-station range, and the first quantitative argument for where in the
planetary-defence architecture a lunar platform earns its place.

## The numbers

Every headline number in the book is produced by one generator,
`build/compute_numbers.py`, and re-derived at build time. Nothing is transcribed
from a draft. The generated number set is printed in full in Appendix B, and the
following check asserts that the manuscript's headline numbers still agree with the
generator:

```sh
python3 build/check_numbers.py
```

## Verification

`build/verify.py` runs seventeen gates against the built PDF: no LaTeX errors, no
warnings, no undefined references, no missing characters, no overfull box above
25 pt, no blank page, no word outside the safe area, no folio overlap, fonts
embedded and no Type 3, a trim size of 6 × 9 inches, a PDF outline that matches the
table of contents, every caption present in the rendered document, a populated index,
the DOI rendered in the document, and two checks that the index marks have not eaten
a word or strayed into a formula.

## Licence

Apache License 2.0. See `LICENSE`.
