"{{{ Nek5000
au BufNewFile,BufRead *.usr,*.inc,SIZE set filetype=fortran
au BufNewFile,BufRead *.par set filetype=cfg
au BufNewFile,BufRead * if &syntax == '' | set syntax=fortran | endif
"}}}
