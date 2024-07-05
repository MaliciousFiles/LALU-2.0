		mv		R0,(15)
		psh		R0
		call	func:
		nop
		pop		R1
		halt
		nop

func:	mv		R0,(10)
		ret
		nop