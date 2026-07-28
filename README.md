# Personal website and shared publications

`metadata/pub2.bib` is the canonical bibliography shared by this website and
the sibling `中文` and `英文` CV projects. The CV projects contain relative
symlinks to this file; do not maintain separate BibTeX copies.

## Update the website

```bash
./setup.sh
source venv/bin/activate
./update_pubs.sh
```

The publication list in `index.html` follows the entry order in `pub2.bib`.

## Update the CVs

Each CV's `compile.sh` calls `scripts/generate_cv_publications.py` before LaTeX.
The generated publication sections therefore follow `pub2.bib` automatically:

```bash
cd ../中文 && ./compile.sh
cd ../英文 && ./compile.sh
```

For the Chinese CV, first/corresponding-author grouping is inferred from the
author list: Zhongxin Liu is either the first author or his author token has an
asterisk. Chinese-language duplicate entries replace their English counterpart
when they share the same DOI.

Paper descriptions are keyed by BibTeX key in each CV's
`sections/publication_descriptions.tex`. Set `\publicationdescriptions` to `1`
before loading the main CV file to show them, or to `0` to hide them. The
Chinese `academic.tex` hides descriptions and `industry.tex` shows them.
