start 0 0 accept 0 0 S S
start 1 0 go 3 0 S S
start 2 0 go 4 0 S S
go 1 0 go 1 0 R S
go 2 0 go 2 0 R S
go 3 0 go 3 0 R S
go 4 0 go 4 0 R S
go 0 0 copy 0 0 L S
copy 1 0 copy 1 1 L R
copy 2 0 copy 2 2 L R
copy 3 0 go2 3 1 L R
copy 4 0 go2 4 2 L R
go2 1 0 go2 1 0 R S
go2 2 0 go2 2 0 R S
go2 3 0 go2 3 0 R S
go2 4 0 go2 4 0 R S
go2 0 0 check 0 0 L L
check 1 1 check 1 1 L L
check 2 2 check 2 2 L L
check 3 1 accept 3 1 S S
check 4 2 accept 4 2 S S