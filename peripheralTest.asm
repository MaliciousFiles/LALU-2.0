		rstkey
		mv		R0,(0)	# index

loop:	ldkeyr	R5
		
		mv		R1,[F]
		bsl		R1,[4]
		add		R1,[F]

		sub		R1,R5
		jmpz	loop:

		stchr	R5,R0
		add		R0,(1)
		jmp	loop: