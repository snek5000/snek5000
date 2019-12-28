"{{{ Nek5000
au BufNewFile,BufRead *.par set filetype=cfg
au BufNewFile,BufRead * if &syntax == '' | set syntax=fortran | endif
au BufNewFile,BufRead * if &filetype == '' | set ft=fortran | endif
au BufNewFile,BufRead *.usr,*.inc set filetype=fortran
"}}}
set path+=**
