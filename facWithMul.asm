		jmp		main:
		nop



# assumes R0 is first param
# output is R2
# overwrites R1
fac:	mv		R2,R2

		usm		{1000}
		jmprx	[3]
		nop
		mv		R2,[1]
		
		mv		R1,[1]
		sub		R1,R0
		jmprz	[5]
		nop

		umul	R2,R0
		sub		R0,[1]

		call	fac:
		nop

		ret
		nop


main:	ld		R0,[0]
		call	fac:
		nop
		st		R2,[1]
		halt
