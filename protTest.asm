		mv			R0,(5)
		mv			RF,(6)
		
		prregWR		{1111},{0001}
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



		mv			R2,{0010}
		bsl			R2,(2)
		add			R2,{0111}
		prprgRE		R4,R2

		st			RF,(1)

		prext		ext:
		enpr		prot:


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

		jmp			ext:		# invalid jmp
		jmpr		(9)			# invalid jmp
		jmpr		R1			# invalid jmp
		jmpr		R0			# invalid reg/jmp
		jmpr		R3			# invalid reg
goto:	sub			R1,(1)		# valid
		usm			{1000}
		jmpx		goto:		# valid

		expr




ext:	mv			R0,(9)
		halt