#!/usr/bin/env python3
"""Repair the heading arguments after a bad normalisation pass.

The pass that joined heading arguments onto one line mis-read the closing
brace of every heading, so each heading carries one brace too many and a
few multi-line headings were left with an orphaned closer on the following
line.  This script restores the intended form:

  * a heading whose title is complete on its own line keeps exactly one
    closing brace --- the extra one is removed;
  * a heading whose title ran onto a second line is rejoined, and the
    orphaned closer is deleted;
  * an orphaned closer that stood on its own line is deleted.

Only the braces are touched.  No title text is changed.

    python3 build/repair_headings.py
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")

HEADING = re.compile(r"^(\\chapter\*?|\\section\*?|\\subsection\*?|\\subsubsection\*?)(\{.*)$")


def repair(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    out: list[str] = []
    i = 0
    fixed = 0

    while i < len(lines):
        line = lines[i]
        m = HEADING.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        cmd, rest = m.group(1), m.group(2)
        n_trail = len(rest) - len(rest.rstrip("}"))
        # ``rest`` still holds the opening brace; strip it before measuring.
        inner = rest[1:-n_trail] if n_trail else rest[1:]
        inner_depth = inner.count("{") - inner.count("}")

        # Case one: the title is complete and the line carries a spare
        # closing brace.  Drop exactly one.
        if n_trail >= 2 and inner_depth == 0:
            out.append(cmd + "{" + inner + "}" * (n_trail - 1))
            fixed += 1
            i += 1
            continue

        # Case two: the title ran onto the next line, which now ends with
        # an orphaned closer.  Rejoin the two.
        if n_trail == 1 and inner_depth == 0 and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if nxt.endswith("}") and nxt.count("{") - nxt.count("}") == -1:
                tail = nxt[:-1].strip()
                if tail:
                    out.append(cmd + "{" + inner + " " + tail + "}")
                else:
                    # The orphan was the whole continuation: the heading was
                    # already complete and the closer simply stands alone.
                    out.append(cmd + "{" + inner + "}")
                fixed += 1
                i += 2
                continue

        # Case three: the title is complete and the orphaned closer stands
        # on its own line a few lines below.
        if n_trail == 1 and inner_depth == 0:
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip() == "}":
                out.append(line)
                out.extend(lines[i + 1:j])
                fixed += 1
                i = j + 1
                continue

        out.append(line)
        i += 1

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return fixed


def main() -> int:
    total = 0
    for base in (SRC, os.path.join(SRC, "chapters"), os.path.join(SRC, "generated")):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if not name.endswith(".tex"):
                continue
            path = os.path.join(base, name)
            n = repair(path)
            if n:
                print(f"{os.path.relpath(path, ROOT)}: {n} heading(s) repaired")
                total += n
    print(f"{total} headings repaired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
