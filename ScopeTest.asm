

main:	mv 	R0, [1]
SCOPE BEGIN
loop:	add	R0, [2]
	jmp	loop:
	ret
	nop
SCOPE END

loop:	nop
	jmp loop:
	nop