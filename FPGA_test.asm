		mv		R0,[0]			# R0 = address
		nop

loop:	ld		R1,R0
		nop
		add		R0,[1]
		nop

		ld		R2,R0
		nop
		jmpz	end:
		nop

		smul	R2,R1
		nop
		st		R2,R0
		nop

		jmp		loop:
		nop


end:	halt