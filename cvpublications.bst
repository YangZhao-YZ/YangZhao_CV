%% BibTeX style for the Word CV's unnumbered, author-first publications.
%% Entries are displayed in main.tex order by bibentry; no sorting is needed.
ENTRY
  { author title journal booktitle year volume number pages
    doi url eprint archivePrefix note cvtitleunderline cvlinespacing }
  {} {}
INTEGERS { nameptr numnames }
STRINGS { names name result entrytext venue }

FUNCTION {format.authors}
{ author empty$
    { "" }
    { author 'names :=
      names num.names$ 'numnames :=
      #1 'nameptr :=
      "" 'result :=
      { nameptr numnames > { #0 } { #1 } if$ }
      { names nameptr "{vv~}{ll}{, jj}{, f.}" format.name$ 'name :=
        name "others" = { "others." 'name := } 'skip$ if$
        name "Zhao, Y." =
          { "\textbf{" name * "}" * 'name := }
          'skip$
        if$
        nameptr #1 >
          { nameptr numnames =
              { ", \& " }
              { ", " }
            if$
            result swap$ * 'result :=
          }
          'skip$
        if$
        result name * 'result :=
        nameptr #1 + 'nameptr :=
      }
      while$
      result
    }
  if$
}

FUNCTION {format.title}
{ cvtitleunderline empty$ { #0 } { cvtitleunderline "yes" = } if$
    { "\uline{" title * ".}" * }
    { title "." * }
  if$
}

FUNCTION {format.entry}
{ format.authors " (" * year * "). " * format.title * 'entrytext :=
  journal empty$ { booktitle } { journal } if$ 'venue :=
  venue empty$
    'skip$
    { entrytext " " * venue * 'entrytext := }
  if$
  volume empty$
    'skip$
    { entrytext ", " * volume * 'entrytext := }
  if$
  number empty$
    'skip$
    { entrytext "(" * number * ")" * 'entrytext := }
  if$
  pages empty$
    'skip$
    { entrytext ", " * pages * 'entrytext := }
  if$
  note empty$
    'skip$
    { entrytext " (" * note * ")" * 'entrytext := }
  if$
  entrytext "." * 'entrytext :=
  eprint empty$
    'skip$
    { entrytext " \href{https://arxiv.org/abs/" * eprint *
      "}{\uline{arXiv:" * eprint * "}}." * 'entrytext := }
  if$
  doi empty$
    { url empty$
        'skip$
        { entrytext " \href{" * url * "}{\uline{" * url * "}}." * 'entrytext := }
      if$
    }
    { entrytext " \href{https://doi.org/" * doi *
      "}{\uline{https://doi.org/" * doi * "}}" * 'entrytext := }
  if$
  entrytext
}

FUNCTION {output.entry}
{ newline$
  "\bibitem{" cite$ * "}" * write$ newline$
  cvlinespacing empty$ { "12.65" } { cvlinespacing } if$
  "\cvpublicationtext{" swap$ * "}{" * format.entry * "}" * write$ newline$
  newline$
}
FUNCTION {article} { output.entry }
FUNCTION {inproceedings} { output.entry }
FUNCTION {conference} { output.entry }
FUNCTION {misc} { output.entry }
FUNCTION {unpublished} { output.entry }
FUNCTION {default.type} { output.entry }
FUNCTION {begin.bib}
{ "\begin{thebibliography}{99}" write$ newline$ }
FUNCTION {end.bib}
{ "\end{thebibliography}" write$ newline$ }
READ
EXECUTE {begin.bib}
ITERATE {call.type$}
EXECUTE {end.bib}
