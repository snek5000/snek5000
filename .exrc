"{{{ Nek5000
au BufNewFile,BufRead *.par set filetype=cfg
au BufNewFile,BufRead * if &syntax == '' | set syntax=fortran | endif
au BufNewFile,BufRead * if &filetype == '' | set ft=fortran | endif
au BufNewFile,BufRead *.usr set filetype=fortran
au BufNewFile,BufRead Snakefile set filetype=snakemake syntax=snakemake
au BufNewFile,BufRead *.smk set filetype=snakemake syntax=snakemake
"}}}

" Fuzzy search:
" Use :fin[d] command
set path=.,src/**,lib/Nek5000/core/**,tests,docs,.github/workflows
set wildignore+=*.pyc,*.o,*.so

" Ctags: https://ctags.io
" Basics
" Use :ta[g] command to search for a tag
"     CTRL-] / C-LeftMouse to go to definition
"     CTRL-T to return
set tags^=.tags

" See https://arjanvandergaag.nl/blog/navigating-project-files-with-vim.html
" Use gf in normal mode to go to a file
set suffixesadd+=.py,.f

" Quickfix with pre-commit
set makeprg=pre-commit\ run\ \-\-all\-files
function s:pre_commit()
    let old_make = &makeprg
    let &makeprg = 'pre-commit run --all-files'
    make
    let &makeprg = old_make
endfunction
command! PreCommit call s:pre_commit()
