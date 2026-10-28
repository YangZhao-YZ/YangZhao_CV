# Yang Zhao CV

Editable LaTeX transcription of `YangZhao_CV_ 202610.docx`.
The wording, section order, publication emphasis, and hyperlinks are retained.
The layout follows the Word CV using a Times-compatible font; line wrapping
and page breaks can differ between Word and LaTeX.

## Compile

In Overleaf, select `main.tex` as the main document and **pdfLaTeX** as the
compiler. Use a recent TeX Live version. No external fonts, custom document
classes or shell escape are required. Publications use BibTeX; Overleaf and
`latexmk` run it automatically.

Locally, with TeX Live installed:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The result is `main.pdf`. Build products, including `.bbl`, `.aux`, logs,
SyncTeX, and the generated PDF, are ignored by Git.

## Edit

- `main.tex`: CV content and publication keys in the desired display order.
- `cvstyle.sty`: typography, spacing, section rules, page numbering, and BibTeX loading.
- `publications.bib`: editable paper metadata.
- `cvpublications.bst`: BibTeX formatting, including bold author names and links.

To add a paper, add a record to `publications.bib`, then place its key in the
Publications section of `main.tex`:

```tex
\cvpublication{zhao2026caffnet}
```

Reorder these lines to change publication order. Metadata uses standard
BibTeX fields such as `author`, `title`, `booktitle` or `journal`, `year`,
`pages`, `doi`, and `eprint` (for arXiv IDs). Separate authors with `and`;
use `Zhao, Yang` for your name so the style displays **Zhao, Y.** automatically.
The optional `cvtitleunderline = {yes}` retains title emphasis from the Word CV.
The `.bbl` file is generated during compilation and stays ignored by Git.

Without `latexmk`, compile with `pdflatex main`, `bibtex main`, then
`pdflatex main` twice. No Biber installation is needed.

## Synchronize

This checkout uses these remotes:

- `origin`: the new Overleaf project, `6ae27d0e7c9d7131e3af7136`.
- `github`: `https://github.com/YangZhao-YZ/YangZhao_CV.git`.

After editing locally, compile and review the PDF, then commit and push:

```sh
git add main.tex cvstyle.sty publications.bib cvpublications.bst README.md .gitignore
git commit -m "Update CV"
git push origin main
git push github main
```

Before editing locally after changes in Overleaf or GitHub, fetch and merge
the corresponding remote branch. Resolve concurrent edits before pushing.
These two Git remotes do not automatically mirror each other; push to both
to keep them synchronized. Git remote settings belong to the local checkout
and are not stored in the repository files.
