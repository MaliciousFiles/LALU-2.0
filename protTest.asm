		call		main:
		mv			R0,(9)
		halt


prot:	halt
		mv			R0,(10)		# invalid reg
		mv			R1,(3)		# valid
		mv			R2,(7)		# invalid reg

		st			R0,(0)		# valid
		st			R2,(0)		# invalid reg
		st			R0,(1)		# invalid mem
		st			R2,(1)		# invalid reg/mem

		ld			R0,(1)		# invalid reg
		ld			R1,(0)		# invalid mem
		ld			R0,(0)		# invalid reg/mem
		ld			R1,(1)		# valid

		jmp			main:		# invalid jmp
		jmpr		(9)			# invalid jmp
		jmpr		R1			# invalid jmp
		jmpr		R0			# invalid reg/jmp
		jmpr		R3			# invalid reg
goto:	sub			R1,(1)		# valid
		usm			{1000}
		jmpx		goto:		# valid
		call		ex:			# valid

		jmp 		goto:		# valid
		nop
		nop
		nop

ex:		mv			R1,(14)		# valid
		psh			R1
		mv			R5,[B]
		mv			R1,(3)
		sar
		pop			R1
		expr



main:	mv			R0,(5)
		mv			RF,(6)
		
		prregWR		{1011},{0001}
		prregRE		{1110},{0000}

		mv			R4,{1111}
		bsl			R4,(4)
		add			R4,{1111}
		bsl			R4,(4)
		add			R4,{1111}
		bsl			R4,(4)
		add			R4,{1111}

		mv			R2,(0)
		prmemWR		R4,R2

		mv			R3,(1)
		prmemRE		R4,R3



		mv			R2,{0001}
		bsl			R2,(4)
		add			R2,{0100}

		bsl			R4,(4)
		add			R4,{0111}

		prprgRE		R4,R2

		prhdl		setreg:

		st			RF,(1)

		enpr		prot:
		ret







#	R5 = which reg, R1 = value
setreg:		call	test:
			par
test:		psh		R5

			umul	R5,(2)
			add		R5,(1)
			jmpr	R5

			mv		R0,R1
			ret
			mv		R1,R1
			ret
			mv		R2,R1
			ret
			mv		R3,R1
			ret
			mv		R4,R1
			ret
			mv		R5,R1
			ret
			mv		R6,R1
			ret
			mv		R7,R1
			ret
			mv		R8,R1
			ret
			mv		R9,R1
			ret
			mv		RA,R1
			ret
			mv		RB,R1
			ret
			mv		RC,R1
			ret
			mv		RD,R1
			ret
			mv		RE,R1
			ret
			mv		RF,R1
			ret