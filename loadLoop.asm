# R0 = idx
# R1 = x pos
# R2 = y pos

# R6 = meta
# R7 = x amt
# R8 = y amt

# RA = x sign
# RB = y sign


		mv		R0,(3)
		mv		R1,(0)
		mv		R2,(0)
		
loop:	ld		R6,R0
		jmpz	loop:
		add		R0,(1)

		ld		R7,R0
		add		R0, (1)

		ld		R8,R0
		add		R0,(1)

		mv		RA,R6
		bsr		RA,(4)
		and		RA,{1}

		jmprz	(3)
		sub		R1,R7
		jmpr	(2)
		add		R1,R7

		mv		RB,R6
		bsr		RB,(5)
		and		RB,{1}

		jmprz	(3)
		sub		R2,R8
		jmpr	(2)
		add		R2,R8

		jmp		loop: