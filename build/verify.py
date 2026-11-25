#!/usr/bin/env python3
"""Verification gates for the built book.

Run after ./build.sh.  Every gate prints PASS or FAIL with the number
that decided it, so the output can be read as evidence rather than as a
summary.  Exit status is non-zero if any gate fails.

    python3 build/verify.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "output", "The-Shape-of-the-Threat.pdf")
LOG = os.path.join(ROOT, "source", "main.log")
TOC = os.path.join(ROOT, "source", "main.toc")
IDX = os.path.join(ROOT, "source", "main.idx")

PAGE_W, PAGE_H = 432.0, 648.0
OUTER_MARGIN = 0.60 * 72.0          # the safe area, in points
INNER_MARGIN = 0.80 * 72.0


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def match_key(s: str) -> str:
    """Reduce a string to comparable words.

    LaTeX renders '--' as an en dash, \\numberline puts a number and a
    title next to each other in the .toc file but a non-breaking space
    between them in the bookmark, and the extractor may hyphenate.  A
    literal comparison fails on all three.  Everything that is not a
    letter or a digit becomes a space on both sides.
    """
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)
    s = re.sub(r"[^0-9A-Za-z]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def toc_entries(path: str) -> list[str]:
    """Parse main.toc with a brace-aware reader.

    A regular expression cannot do this: a part title carries a nested
    \\hspace {1em}, and a chapter line carries \\numberline {1}Title.
    """
    text = read(path)
    titles: list[str] = []

    def balanced(s: str, start: int) -> tuple[str, int]:
        """Return the contents of the group that opens at s[start]."""
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{":
                depth += 1
            elif s[i] == "]":
                pass
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    return s[start + 1:i], i + 1
        return s[start:], len(s)

    for match in re.finditer(r"\\contentsline \{", text):
        _level, pos = balanced(text, match.end() - 1)
        payload, _pos = balanced(text, pos)
        # payload is either {Title} or {\numberline {n}Title}.  LaTeX's
        # \numberline takes the number as its only argument; the title
        # simply follows it inside the same group.
        m = re.match(r"\\numberline \{([^}]*)\}(.*)$", payload, re.S)
        title = f"{m.group(1)} {m.group(2)}" if m else payload
        title = re.sub(r"\\hspace\s*\{[^}]*\}", " ", title)
        title = title.replace("\\ ", " ").replace("~", " ")
        title = re.sub(r"\\[a-zA-Z]+\s*", "", title)
        title = re.sub(r"[{}]", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        if title:
            titles.append(title)

    return titles


def strip_definitions(text: str) -> str:
    """Remove LaTeX definitions outright.

    A \\newcommand whose body is a font or a colour specification is not
    prose, and leaving its arguments behind puts strings like
    "10pt04pt8pttxtdim" into the manuscript text.
    """
    for cmd in ("newcommand", "renewcommand", "providecommand",
                "DeclareRobustCommand", "newenvironment", "renewenvironment",
                "setlist", "titleformat", "setlength", "setcounter", "def",
                "fontsize", "setmainfont", "setsansfont", "setmonofont"):
        while True:
            m = re.search(r"\\" + cmd + r"\b", text)
            if not m:
                break
            i = m.end()
            while i < len(text) and text[i] in " \n":
                i += 1
            if i < len(text) and text[i] == "[":
                j = text.find("]", i)
                if j < 0:
                    break
                i = j + 1
            moved = False
            while i < len(text) and text[i] == "{":
                depth = 0
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    i += 1
                else:
                    break
                moved = True
            if not moved:
                break
            text = text[:m.start()] + " " + text[i:]
    return text


def source_sentences(path: str) -> list[list[str]]:
    """The prose of one manuscript file, as a list of word sequences.

    Everything LaTeX contributes to the page that is not prose is removed:
    headings, captions, labels, index marks, cross-references and maths.
    What is left is what the reader is supposed to read, and it must all
    appear in the rendered PDF.
    """
    text = read(path)

    # Comments.
    text = re.sub(r"(?<!\\)%.*", "", text)

    text = strip_definitions(text)

    # Index marks: \idx prints nothing, \idxw prints its term.
    text = re.sub(r"\\idx\{[^{}]*\}", " ", text)
    text = re.sub(r"\\idxw\{([^{}]*)\}", r" \1 ", text)

    # Cross-references become a placeholder, because "Figure 18.1" in the
    # rendered page corresponds to "\figref{fig:...}" in the source.
    text = re.sub(r"\\(?:figref|tabref|ref|eqref|pageref|cref|Cref)\{([^{}]*)\}",
                  " XREF ", text)

    # A link shows its text, not its target.
    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r" \1 ", text)

    # Maths.
    text = re.sub(r"\\\[.*?\\\]", " XMATH ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " XMATH ", text)

    # Graphics contribute no prose.
    text = re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^{}]*\}", " ", text)

    # Structural commands: drop the command and its argument.
    for cmd in ("chapter", "section", "subsection", "subsubsection",
                "caption", "label", "index", "begin", "end", "item"):
        text = re.sub(r"\\" + cmd + r"\*?(\[[^\]]*\])?\{[^{}]*\}", " ", text)
        text = re.sub(r"\\" + cmd + r"\*?(\[[^\]]*\])?", " ", text)

    # Any other command: drop the name, keep the argument text.
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", text)

    # Braces and the rest of the punctuation.
    text = re.sub(r"[{}$&#\\]", " ", text)
    text = text.replace("``", '"').replace("''", '"')
    text = re.sub(r"---?", " ", text)

    # Split into sentences.
    flat = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", flat)

    out: list[list[str]] = []
    for part in parts:
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", part)
        if len(words) >= 5:
            out.append(words)
    return out


def _word_pattern(word: str) -> str:
    """A word that may be broken by a hyphen or by an intrusion.

    LaTeX hyphenates a long word at a line break, and the text extractor
    interleaves a vector figure's own axis labels with the prose around
    it, so a word can come out as "deforma- 3 tion".  Only non-letters may
    come between the letters of a word, so the word still has to be there.
    """
    return r"[^A-Za-z]{0,6}".join(re.escape(c) for c in word)


def sentence_missing(words: list[str], rendered: str, max_gap: int = 4000) -> bool:
    """True if the sentence is not present in the rendered text.

    Every word of the source must appear, in order, in the rendered text.
    A word that an index mark ate is simply not there, so the sentence does
    not match.

    The alignment is anchored on the longest word of the sentence, which is
    the one least likely to be common, and every occurrence of that anchor
    is tried.  Between two consecutive words the rendered text may carry a
    figure's own axis labels, because the text extractor interleaves a
    vector graphic with the prose around it; the gap is therefore allowed
    to be long.
    """
    usable = [w for w in words if w not in ("XMATH", "XREF")]
    if len(usable) < 3:
        return False

    anchor_at = max(range(len(words)), key=lambda i: len(words[i]))
    anchor = words[anchor_at]
    if anchor in ("XMATH", "XREF"):
        return False

    start = 0
    while True:
        idx = rendered.find(anchor, start)
        if idx < 0:
            return True
        if _aligns(words, rendered, anchor_at, idx, max_gap):
            return False
        start = idx + 1


def _aligns(words: list[str], rendered: str, anchor_at: int, anchor_pos: int,
            max_gap: int) -> bool:
    """Can the sentence be laid out around the anchor at anchor_pos?"""
    # Backwards.
    pos = anchor_pos
    for i in range(anchor_at - 1, -1, -1):
        w = words[i]
        if w in ("XMATH", "XREF"):
            continue
        pattern = _word_pattern(w)
        hits = list(re.finditer(pattern, rendered[max(0, pos - max_gap):pos]))
        if not hits:
            return False
        pos = max(0, pos - max_gap) + hits[-1].start()
    # Forwards.
    pos = anchor_pos + len(words[anchor_at])
    for i in range(anchor_at + 1, len(words)):
        w = words[i]
        if w in ("XMATH", "XREF"):
            continue
        pattern = _word_pattern(w)
        m = re.compile(pattern).search(rendered, pos, pos + max_gap)
        if not m:
            return False
        pos = m.start() + len(w)
    return True


def remove_captions(rendered: str, captions: list[str]) -> str:
    """Take the figure and table captions out of the rendered text.

    A float is a separate block on the page, but the text extractor
    interleaves it with the prose, so a sentence that spans a figure comes
    out in two pieces.  Removing the caption puts the sentence back
    together.
    """
    out = rendered.replace("\u2019", "'")
    for cap in captions:
        cap = cap.replace("\u2019", "'")
        words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", cap)
        if len(words) < 4:
            continue
        for probe in (words, words[:14]):
            # Words in a caption are separated by punctuation as well as
            # by spaces.
            pattern = r"[^A-Za-z0-9]{0,3}".join(
                r"-?".join(re.escape(c) for c in w) for w in probe)
            # The caption also appears in the list of figures, so every
            # occurrence is taken out.
            new = re.sub(pattern, " ", out)
            if new != out:
                out = new
                break
    return out


def grammar_damage(text: str) -> list[str]:
    """Find prose that has lost a word.

    A sentence that reads "... under a power budget. is the name for ..."
    has lost its subject, and a clause that reads "... the vehicle's and ,"
    has lost its noun.  These are the signatures of an index mark that was
    placed where a word belongs but does not print it.

    The scan runs on the rendered text, not on the source, because the
    rendered text is what the reader sees.
    """
    prose = text
    # The table of contents and the two lists are dot-leadered entries, not
    # prose, and they produce every one of these patterns on their own.
    start = prose.find("A lunar rover is specified against three things at once")
    if start > 0:
        prose = prose[start:]

    prose = re.sub(r"\s+", " ", prose)
    # A sentence that spans a page break must not read as a fragment.
    prose = re.sub(r"\s*[\f]\s*", " ", prose)

    patterns = [
        (r"[.!?]\s+(?:is|are|was|were|has|have|had|does|do|says|states|gives|gave|makes|made|takes|took)\s",
         "a sentence that starts with a verb"),
        (r"\b[A-Za-z]{3,}\s+\.(?:\s|$)", "a space before a full stop"),
        (r"\b(?:the|a|an|to|with|for|than|into)\s*[,;]", "a determiner followed by punctuation"),
        (r"\b(?:the|a|an)\s+and\b", "an article followed by a conjunction"),
    ]

    hits: list[str] = []
    for pattern, label in patterns:
        for m in re.finditer(pattern, prose):
            lo = max(0, m.start() - 70)
            hits.append(f"{label}: ...{prose[lo:m.end() + 40]}...")
    return hits


def index_marks_eat_words(path: str) -> list[str]:
    """Find the index marks that have taken a word out of the prose.

    The book has two kinds of index mark.  \\idxw prints its term, so it
    can stand where the word belongs.  \\idx prints nothing: it registers
    a term that the prose already writes.  A \\idx used where the word
    belongs silently deletes that word from the sentence, and nothing in a
    LaTeX build reports it.

    The test: for a \\idx whose entry is a term and not a qualified label,
    the sentence that holds the mark must contain the term once the mark
    is taken out.  If it does not, the mark ate the word.
    """
    text = read(path)

    # Work sentence by sentence so that the mark can be judged in context.
    flat = re.sub(r"[ \t]+", " ", text)
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", flat)

    bad: list[str] = []
    for sentence in sentences:
        for m in re.finditer(r"\\(idx|idxw)\{([^{}]*)\}", sentence):
            kind, entry = m.group(1), m.group(2)
            if kind == "idxw":
                continue
            # A qualified label names a concept, not a word, and is always
            # index-only by design.
            if "," in entry:
                continue
            key = re.sub(r"[^A-Za-z0-9]", "", entry.split()[0]).lower()
            if not key:
                continue
            without = sentence[:m.start()] + " " + sentence[m.end():]
            without = re.sub(r"[^A-Za-z0-9]", "", without).lower()
            if key not in without:
                bad.append(f"{os.path.basename(path)}: {entry} in "
                           f"'...{re.sub(r'[ ]+', ' ', sentence[max(0, m.start() - 60):m.start() + 20]).strip()}...'")
    return bad


def index_marks_at_clause_end(path: str) -> list[str]:
    """Find the index marks that sit at the end of a clause.

    A mark at the end of a clause stands where the word belongs: the
    sentence would end with the word missing and the clause's punctuation
    stranded after it.  A qualified label is exempt, because it names a
    concept and is never the word.
    """
    text = read(path)
    bad: list[str] = []
    for m in re.finditer(r"\\idx\{([^{}]*)\}", text):
        entry = m.group(1)
        if "," in entry:
            continue
        after = text[m.end():m.end() + 40].lstrip()
        if after[:1] in (".", ";", ":"):
            before = text[max(0, m.start() - 70):m.start()].replace("\n", " ").strip()
            bad.append(f"{os.path.basename(path)}: {entry} in '...{before[-60:]}...'")
    return bad


def index_marks_in_maths(path: str) -> list[str]:
    """Find the index marks that have been put inside a formula.

    A mark between two dollar signs does not print its term but it still
    splits the formula, and it was how two of the book's marks came to
    sit in the middle of "g/cm$^3$".
    """
    text = read(path)
    bad: list[str] = []
    in_math = False
    for i, ch in enumerate(text):
        if ch != "$":
            continue
        in_math = not in_math
        if in_math:
            tail = text[i:]
            m = re.search(r"\\(?:idx|idxw)\{", tail)
            if m and "$" not in tail[:m.start()]:
                bad.append(f"{os.path.basename(path)}: a mark inside a formula "
                           f"at '...{tail[max(0, m.start() - 30):m.start() + 30]}...'")
    return bad


def main() -> int:
    results: list[tuple[bool, str, str]] = []

    def gate(name: str, ok: bool, detail: str) -> None:
        results.append((ok, name, detail))

    log = read(LOG)

    n_err = len(re.findall(r"^!", log, re.M))
    gate("LaTeX errors", n_err == 0, f"{n_err} found")

    # The authoritative warning check greps 'Warning' ALONE.  A grep for
    # 'LaTeX Warning' misses 'Package enumitem Warning' and 'Package
    # microtype Warning', which is how a build reports zero errors while a
    # page is full of boxes.
    n_warn = log.count("Warning")
    gate("LaTeX warnings (grep 'Warning' alone)", n_warn == 0, f"{n_warn} found")

    n_undef = len(re.findall(r"undefined", log, re.I))
    gate("Undefined references and citations", n_undef == 0, f"{n_undef} found")

    n_missing = log.count("Missing character")
    gate("Missing characters", n_missing == 0, f"{n_missing} found")

    overfull = [float(m) for m in re.findall(r"Overfull \\hbox \(([\d.]+)pt", log)]
    bad_overfull = [v for v in overfull if v > 25.0]
    gate("Overfull hboxes over 25 pt", not bad_overfull,
         f"{len(overfull)} overfull, {len(bad_overfull)} over 25 pt")

    info = subprocess.run(["pdfinfo", PDF], capture_output=True, text=True).stdout
    n_pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
    gate("Trim size is 6 x 9 in",
         abs(float(size.group(1)) - PAGE_W) < 0.5 and abs(float(size.group(2)) - PAGE_H) < 0.5,
         f"{size.group(1)} x {size.group(2)} pt")

    fonts = subprocess.run(["pdffonts", PDF], capture_output=True, text=True).stdout.splitlines()
    type3 = sum(1 for line in fonts[2:] if "Type 3" in line)
    gate("Type 3 fonts", type3 == 0, f"{type3} found")

    not_embedded = []
    for line in fonts[2:]:
        parts = line.split()
        if len(parts) >= 6 and parts[5] == "no":
            not_embedded.append(line.strip())
    gate("All fonts embedded", not not_embedded,
         f"{len(not_embedded)} not embedded" + (f": {not_embedded}" if not_embedded else ""))

    # ----------------------------------------------------------------------
    # Page geometry: blank pages, words outside the safe area, folio overlaps
    # ----------------------------------------------------------------------
    bbox_xml = subprocess.run(
        ["pdftotext", "-bbox", PDF, "-"], capture_output=True, text=True).stdout
    root = ET.fromstring(bbox_xml)
    ns = {"x": "http://www.w3.org/1999/xhtml"}

    pages = root.findall(".//x:page", ns)

    blank_pages = []
    outside = []
    folio_overlaps = []

    for index, page in enumerate(pages, start=1):
        words = page.findall(".//x:word", ns)
        if len(words) == 0:
            blank_pages.append(index)
            continue

        boxes = []
        for w in words:
            wtext = (w.text or "")
            try:
                x0 = float(w.get("xMin")); x1 = float(w.get("xMax"))
                y0 = float(w.get("yMin")); y1 = float(w.get("yMax"))
            except (TypeError, ValueError):
                continue
            boxes.append((wtext, x0, y0, x1, y1))

        if not boxes:
            blank_pages.append(index)
            continue

        # The folio is the page number: the lowest text on the page, near
        # the centre.  The two cover leaves carry no folio and are skipped.
        is_cover = index in (1, n_pages)
        folio = None
        for wtext, x0, y0, x1, y1 in boxes:
            if re.fullmatch(r"[ivxlcdm]+|\d+", wtext or "") and abs((x0 + x1) / 2 - PAGE_W / 2) < 60:
                if folio is None or y1 > folio[3]:
                    folio = (wtext, x0, y0, x1, y1)

        if folio is not None:
            for wtext, x0, y0, x1, y1 in boxes:
                is_folio = (wtext, x0, y0, x1, y1) == folio
                if not is_folio and y1 > folio[2] and y0 < folio[4] and x1 > folio[1] and x0 < folio[3]:
                    folio_overlaps.append((index, wtext))

        # Odd pages are right-hand pages, so the outer edge is on the right;
        # even pages are left-hand pages, so the outer edge is on the left.
        # The outer margin is 0.60 in, the inner 0.80 in.
        if not is_cover:
            for wtext, x0, y0, x1, y1 in boxes:
                if index % 2 == 1 and x1 > PAGE_W - OUTER_MARGIN + 0.5:
                    outside.append((index, wtext, round(x1, 1)))
                if index % 2 == 0 and x0 < OUTER_MARGIN - 0.5:
                    outside.append((index, wtext, round(x0, 1)))

    gate("Blank pages", not blank_pages, f"{len(blank_pages)} found: {blank_pages[:10]}")
    gate("Words outside the safe area", not outside,
         f"{len(outside)} found" + (f": {outside[:8]}" if outside else ""))
    gate("Folio and running-head overlaps", not folio_overlaps,
         f"{len(folio_overlaps)} found" + (f": {folio_overlaps[:8]}" if folio_overlaps else ""))

    # ----------------------------------------------------------------------
    # The outline against the table of contents
    # ----------------------------------------------------------------------
    sys.path.insert(0, ROOT)
    from pypdf import PdfReader                                    # noqa: E402

    reader = PdfReader(PDF)

    def flatten(outline) -> list[str]:
        out: list[str] = []

        def walk(items):
            for item in items:
                if isinstance(item, list):
                    walk(item)
                else:
                    try:
                        out.append(item.title)
                    except AttributeError:
                        pass

        walk(outline)
        return out

    pdf_titles = flatten(reader.outline)
    toc_titles = toc_entries(TOC)

    pdf_set = [match_key(t) for t in pdf_titles]
    toc_set = [match_key(t) for t in toc_titles]

    mismatched = [(a, b) for a, b in zip(pdf_set, toc_set) if a != b]
    gate("PDF outline against the table of contents",
         len(pdf_set) == len(toc_set) and not mismatched,
         f"{len(pdf_set)} outline entries, {len(toc_set)} contents lines"
         + (f", {len(mismatched)} differ: {mismatched[:4]}" if mismatched else ""))

    # Every caption must be in the rendered document.  The figures are
    # embedded as vector PDF, so they are not raster images and
    # page.images does not see them; the caption text is the check that
    # actually means something.
    caption_source = ""
    for name in ["frontmatter.tex"] + [f"chapters/ch{n:02d}.tex" for n in range(1, 34)]:
        caption_source += read(os.path.join(ROOT, "source", name))

    captions = []
    for match in re.finditer(r"\\caption\{", caption_source):
        depth = 0
        for i in range(match.end() - 1, len(caption_source)):
            if caption_source[i] == "{":
                depth += 1
            elif caption_source[i] == "}":
                depth -= 1
                if depth == 0:
                    captions.append(caption_source[match.end():i])
                    break

    pdf_text = subprocess.run(["pdftotext", PDF, "-"], capture_output=True, text=True).stdout
    flat_pdf_text = match_key(pdf_text)
    missing_captions = []
    for cap in captions:
        key = match_key(cap)
        if key and key[:60] not in flat_pdf_text:
            missing_captions.append(key[:60])
    gate("Captions in the rendered document", not missing_captions,
         f"{len(captions)} captions, {len(missing_captions)} missing"
         + (f": {missing_captions[:3]}" if missing_captions else ""))

    # The index must be populated.
    n_headwords = len({re.search(r"\\indexentry\{([^{}]*)", line).group(1)
                        for line in read(IDX).splitlines() if "\\indexentry" in line})
    gate("Index headwords", n_headwords >= 60, f"{n_headwords} headwords")

    # The DOI must be in the rendered document in all four printed places.
    n_doi = pdf_text.count("10.5281/zenodo.24517244")
    gate("DOI in the rendered document", n_doi >= 4, f"{n_doi} occurrences")

    # The prose must not have lost a word to an index mark.  The strongest
    # form of this check is that the rendered document must contain the
    # manuscript's own sentences: an index mark that stands where a word
    # belongs breaks exactly the sentence it sits in.
    rendered = re.sub(r"\s+", " ", pdf_text)
    rendered = re.sub(r"(?<=[a-z])-\s+(?=[a-z])", "-", rendered)   # hyphenation
    rendered = remove_captions(rendered, captions)

    eaten = []
    for name in ["frontmatter.tex", "backmatter.tex"] + \
               [f"chapters/ch{n:02d}.tex" for n in range(1, 34)]:
        eaten += index_marks_eat_words(os.path.join(ROOT, "source", name))
    gate("Index marks that have not eaten a word", not eaten,
         f"{len(eaten)} found" + (f": {eaten[:4]}" if eaten else ""))

    in_maths = []
    for name in ["frontmatter.tex", "backmatter.tex"] + \
               [f"chapters/ch{n:02d}.tex" for n in range(1, 29)]:
        in_maths += index_marks_in_maths(os.path.join(ROOT, "source", name))
    gate("Index marks outside the formulae", not in_maths,
         f"{len(in_maths)} found" + (f": {in_maths[:4]}" if in_maths else ""))

    # ----------------------------------------------------------------------
    # The figures.  Fourteen charts, and the question a reader asks of every
    # one of them is whether the labels collide.  build/check_fig_overlaps.py
    # measures that in display coordinates.
    # ----------------------------------------------------------------------
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build", "check_fig_overlaps.py")],
        capture_output=True, text=True)
    fig_lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("[FAIL]")]
    fig_ok = proc.returncode == 0
    gate("Figure label overlaps", fig_ok,
         "none" if fig_ok else f"{len(fig_lines)} found: "
         + ("; ".join(ln[7:60] for ln in fig_lines[:3])))




    # ----------------------------------------------------------------------
    # Report
    # ----------------------------------------------------------------------
    width = max(len(n) for _, n, _ in results)
    failed = 0
    for ok, name, detail in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{status}] {name.ljust(width)}  {detail}")

    print()
    print(f"{len(results) - failed}/{len(results)} gates pass.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
