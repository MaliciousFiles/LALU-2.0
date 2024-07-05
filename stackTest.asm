	mv		R0,(15)
	psh		R0
	call	func:
	
	pop		R1
	halt


func:mv		R0,(10)
	psh		R0
	call	func2:
	
	pop		R2
	ret
	


func2:mv	R0,(5)
	psh		R0
	ret
	
