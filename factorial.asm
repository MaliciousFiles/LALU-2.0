		jmp		main:
		nop




# multiplies R5 by R6 into R4
mul:	mv		R4,[0]
loop:	bsr		R6,[1]
		usm		[1]
		jmprnx	[3]
		nop
		add		R4,R5

		bsl		R5,[1]
		mv		R6,R6
		usm		[8]
		jmpx	loop:
		nop
		ret
		nop



# assumes R0 is first param
# output is R2
# overwrites R1
fac:	mv		R2,R2

		usm		[8]
		jmprx	[3]
		nop
		mv		R2,[1]
		
		mv		R1,[1]
		sub		R1,R0
		jmprz	[9]
		nop

		mv		R5,R2
		mv		R6,R0
		call	mul:
		nop
		mv		R2,R4
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
