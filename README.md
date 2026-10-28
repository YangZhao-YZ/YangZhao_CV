# Yang Zhao CV

Editable LaTeX transcription of `YangZhao_CV_ 202610.docx`.
The wording, section order, publication emphasis, and hyperlinks are retained.
The layout follows the Word CV using a Times-compatible font; line wrapping
and page breaks can differ between Word and LaTeX.

## Compile

In Overleaf, select `main.tex` as the main document and **pdfLaTeX** as the
compiler. Use a recent TeX Live version. No external fonts, custom document
classes, bibliography processor, or shell escape are required.

Locally, with TeX Live installed:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The result is `main.pdf`. Build products, including `.bbl`, `.aux`, logs,
SyncTeX, and the generated PDF, are ignored by Git.

## Edit

- `main.tex`: all CV content, including contact information and every section.
- `cvstyle.sty`: typography, spacing, section rules, and page numbering.

Publications are written directly in `main.tex` to preserve
the exact citation wording in the Word file. No `.bib` or `.bbl` is needed.

## Synchronize

This checkout uses these remotes:

- `origin`: the new Overleaf project, `6ae27d0e7c9d7131e3af7136`.
- `github`: `https://github.com/YangZhao-YZ/YangZhao_CV.git`.

After editing locally, compile and review the PDF, then commit and push:

```sh
git add main.tex cvstyle.sty README.md .gitignore
git commit -m "Update CV"
git push origin main
git push github main
```

Before editing locally after changes in Overleaf or GitHub, fetch and merge
the corresponding remote branch. Resolve concurrent edits before pushing.
These two Git remotes do not automatically mirror each other; push to both
to keep them synchronized. Git remote settings belong to the local checkout
and are not stored in the repository files.
