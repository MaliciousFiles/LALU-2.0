		mv		R0,[0]			# R0 = address

loop:	ld		R1,R0
		add		R0,[1]

		ld		R2,R0
		jmpz	end:

		smul	R2,R1
		st		R2,R0

		jmp		loop:

end:	halt