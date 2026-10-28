# Yang Zhao CV

Editable LaTeX transcription of `YangZhao_CV_ 202610.docx`.
The CV content and section order follow the Word source. Publications use
IEEE reference formatting with bold emphasis on the CV owner’s name.
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
SyncTeX, and the intermediate `main.pdf`, are ignored by Git. The published
PDFs described below are intentionally tracked.

## Edit

- `main.tex`: CV content and publication keys in the desired display order.
- `cvstyle.sty`: typography, spacing, section rules, page numbering, and BibTeX loading.
- `publications.bib`: editable paper metadata.
- Standard `IEEEtran.bst` (included in TeX Live): IEEE reference formatting.

To add a paper, add a record to `publications.bib`, then place its key in the
Publications section of `main.tex`:

```tex
\cvpublication{zhao2026caffnet}
```

Reorder these lines to change publication order. Metadata uses standard
BibTeX fields such as `author`, `title`, `booktitle` or `journal`, `year`,
`pages`, `doi`, and `eprint` (for arXiv IDs). Separate authors with `and`;
use `Zhao, Yang` for your name so IEEEtran displays **Y. Zhao** automatically.
The standard style handles initials before surnames, quoted sentence-case
paper titles, italic venue names, volume/page labels, and year placement.
Protect proper names and acronyms with braces, for example `{CAffNet}` and
`{MPC}`. Provide a `url` field for clickable arXiv/DOI links; IEEEtran uses
that field for its online-source link. The `doi` and `eprint` metadata can
also remain in the record for reuse.

The `cv:control` entry configures author-name emphasis and disables repeated-
author dashes. The CV retains its unnumbered publication list, manual ordering,
and bold owner name; these are CV presentation choices around IEEE-formatted
reference text. No custom bibliography style file is needed.
The `.bbl` file is generated during compilation and stays ignored by Git.

Without `latexmk`, compile with `pdflatex main`, `bibtex main`, then
`pdflatex main` twice. No Biber installation is needed.

## Automatic PDF builds and history

Every push to GitHub’s `main` branch runs `.github/workflows/build-cv.yml`
once, compiling only the final commit when a push includes multiple commits.
The workflow compiles `main.tex` with pdfLaTeX/BibTeX using TeX Live 2025,
then commits:

- `YangZhao_CV.pdf`: the latest successfully compiled CV.
- `history/YangZhao_CV_yyyymmdd.pdf`: the latest successful revision for that date.
- `history/build-index.json`: the source commit behind the latest and daily PDFs.

Dates come from the source commit timestamp in **America/Chicago**. Later
successful updates on the same date overwrite that day’s PDF. Earlier versions
remain accessible through Git history. All builds are allowed to finish; if runs finish out of order, the publisher keeps newer PDFs
as the root and daily versions. Failed compilation leaves the existing PDFs
untouched. GitHub’s built-in token commits the PDFs without triggering another
build, so no extra secret or personal access token is required.

The PDF is also downloadable from each successful Actions run. To rebuild
manually, choose **Actions → Build and archive CV → Run workflow** on `main`.
Overleaf edits trigger a build after those edits are synchronized to GitHub.
The workflow publishes to GitHub; it does not push to Overleaf.

## Synchronize

This checkout uses these remotes:

- `origin`: the new Overleaf project, `6ae27d0e7c9d7131e3af7136`.
- `github`: `https://github.com/YangZhao-YZ/YangZhao_CV.git`.

After editing locally, compile and review the PDF, then commit and push:

```sh
git add main.tex cvstyle.sty publications.bib README.md .gitignore
git commit -m "Update CV"
git push origin main
git push github main
```

GitHub Actions adds PDF commits to `main`, so run `git pull --ff-only github main`
before pushing further local edits. Before editing after changes in Overleaf or GitHub, fetch and merge
the corresponding remote branch. Resolve concurrent edits before pushing.
These two Git remotes do not automatically mirror each other; push to both
to keep them synchronized. Git remote settings belong to the local checkout
and are not stored in the repository files.
