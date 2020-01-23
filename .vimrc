"{{{ Nek5000
au BufNewFile,BufRead *.par set filetype=cfg
au BufNewFile,BufRead * if &syntax == '' | set syntax=fortran | endif
au BufNewFile,BufRead * if &filetype == '' | set ft=fortran | endif
au BufNewFile,BufRead *.usr,*.inc set filetype=fortran
"}}}

" Fuzzy search:
" Use :fin[d] command
set path+=src/**,lib/Nek5000/core/**
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
