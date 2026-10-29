# CV editing workflow

- Make source, bibliography, formatting, documentation, and workflow edits on
  the `update` branch. Do not commit or push these changes directly to `main`.
- Fetch `github` before starting. Create `update` from `github/main` if it does
  not exist; otherwise preserve its existing work and merge `github/main`
  into it before continuing. Never reset or force-push someone else's work.
- Keep CV content in `main.tex`, paper metadata in `publications.bib`, and
  structural formatting in `cvstyle.sty`.
- Compile with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
  For workflow or publisher changes, also run the publisher tests and validate
  the workflow with actionlint when available.
- Push `update` to the `github` remote and open or update a PR to `main` when
  finished. Leave the PR ready for the user; merge only when explicitly asked.
- PR checks compile a downloadable PDF preview. They must not publish PDFs or
  write to the repository. After a merge to `main`, GitHub Actions alone may
  commit `YangZhao_CV.pdf`, the daily PDF in `history/`, and its build index.
- Generated intermediate files such as `.aux`, `.bbl`, logs, and `main.pdf`
  stay ignored. Do not manually edit published PDFs.
- Overleaf is the `origin` remote. Bring Overleaf source changes into `update`
  for review rather than bypassing the PR process on GitHub's `main` branch.
