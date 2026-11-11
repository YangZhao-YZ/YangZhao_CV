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

A pull request targeting `main` runs the **Compile CV** check and uploads a
PDF preview when its pages differ from the published CV. Each later push to the
PR compiles once, using the final commit when the push includes multiple commits. PR builds are read-only
and never change the published PDFs.

After the PR is merged, the push to `main` compiles and publishes the final CV.
The workflow compiles `main.tex` with pdfLaTeX/BibTeX using TeX Live 2025,
then compares every page with the published CV using Poppler at 150 dpi. PDF
timestamps, document IDs, and other invisible metadata do not count as CV
changes. When the pages are identical, it skips the preview artifact upload,
publishing job, history backup, build-index update, and generated commit.
Otherwise it commits:

- `YangZhao_CV.pdf`: the latest successfully compiled CV.
- `history/YangZhao_CV_yyyymmdd.pdf`: the latest successful revision for that date.
- `history/build-index.json`: the source commit behind the latest and daily PDFs.

Dates come from the source commit timestamp in **America/Chicago**. Later
successful updates on the same date overwrite that day’s PDF. Earlier versions
remain accessible through Git history. All builds are allowed to finish. A build
superseded by a newer source commit on main skips publication; the newer build decides whether the CV changed.
This also prevents an older build from publishing after a newer no-change run.
Failed compilation leaves the existing PDFs untouched. A dedicated repository deploy key commits the PDFs after merge,
with `[skip ci]` in the generated commit message to prevent a rebuild loop.
The private key is stored as the encrypted Actions secret `CV_PDF_PUBLISH_KEY`
and is supplied only to the main-branch publishing job. PR builds receive no
publishing key. No personal access token is used.

A changed PDF is also downloadable from its successful Actions run.
An unchanged build passes the compile check without uploading another PDF.
The publisher compares again against the current main branch before committing,
so a concurrent publication cannot create a duplicate backup. To rebuild
manually, choose **Actions → Build and archive CV → Run workflow** on `main`.
Overleaf edits must first be brought into `update` and submitted as a PR.
The workflow publishes to GitHub; it does not push to Overleaf.

## Synchronize

This checkout uses these remotes:

- `origin`: the new Overleaf project, `6ae27d0e7c9d7131e3af7136`.
- `github`: `https://github.com/YangZhao-YZ/YangZhao_CV.git`.

Work on the reusable `update` branch and keep `main` as the approved CV.
Start the branch once:

```sh
git fetch github
git switch -c update github/main
```

For later editing sessions, preserve existing work and bring in the latest
approved version:

```sh
git fetch github
git switch update
git merge github/main
```

Compile and review the changes, then submit them:

```sh
git add main.tex cvstyle.sty publications.bib README.md .gitignore
git commit -m "Update CV"
git push -u github update
gh pr create --base main --head update --fill
```

If an `update` PR is already open, later pushes update that PR. Review its
**Compile CV** result and download the PDF preview from the linked Actions run,
then merge the PR when satisfied. The post-merge workflow refreshes the root
PDF and the daily backup. No second reviewer is required for this personal
repository, but the PR and a passing **Compile CV** check are required.

The versioned policy is `.github/rulesets/main-pr.json`. Its repository deploy-key
exception permits generated PDF commits after merge; ordinary source changes
must use a PR. The rule also prevents deleting or force-pushing `main`. The CV publisher is
the repository’s only deploy key; GitHub applies this bypass to repository
deploy keys as a group.

To bring source edits from Overleaf into the review process:

```sh
git switch update
git fetch origin
git merge origin/main
git push github update
```

Resolve any conflicts before committing. Do not use Overleaf's synchronization
to bypass the protected `main` branch on GitHub. The `origin` and `github`
remotes do not automatically mirror each other, and their settings belong to
this local checkout rather than the repository files.

## Recover an Overleaf GitHub sync conflict

If Overleaf creates an `overleaf-...` recovery branch, compare its content
with the current CV before merging. Bring the recovery branch into `update`
and resolve conflicts there, preserving any genuine new edits and the current
formatting and automation. Submit the result through the existing update PR.

For a sync recovery, merge the PR using **Create a merge commit**, rather than
squashing or rebasing. Overleaf needs its recovery branch to be part of the
history of the default branch. After the PR is merged into `main`, return to
Overleaf and click **I have manually merged. Continue**. Do not click that
button while the recovery exists only in `update`.

The `overleaf-2026-10-28-2359` recovery branch was verified to have exactly the
same file tree as the earlier IEEE-formatting commit `e8ea092`. Its history
was reconciled into `update` while keeping the newer CV, corrected citation
name, and automation files.
