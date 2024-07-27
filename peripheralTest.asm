		rstkey
		mv		R0,[9]	# index
		bsl		R0,[4]

loop:	ldkeyr	R5
		jmpz	loop:

		stchr	R5,R0
		add		R0,(1)
		jmp	loop: