		mv		R0,[8]		# store address
		bsl		R0,[4]

		mv		R5,{0}		# not break code

		mv		R7,{0}		# shift
		mv		R8,{0}		# ctrl
		mv		R9,{0}		# alt
		mv		RA,{0}		# caps lock

		mv		RD,[4]		# char per line
		bsl		RD,(4)

		mv		RF,{0}		# NUL


loop:	ldkey	R1
		


		# left alt		
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[1]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		mv		R9,R5
		jmp		end:



		# left shift		
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[2]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		mv		R7,R5
		jmp		end:



		# right shift		
		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[9]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		mv		R7,R5
		jmp		end:



		# left control		
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[4]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		mv		R8,R5
		jmp		end:



		# caps lock	
		mv		R5,R5
		jmprz	(13)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[8]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)
		mv		RA,RA
		jmprz	(3)
		mv		RA,{0}
		jmp		end:
		mv		RA,{1}
		jmp		end:



		# if CTRL or ALT, don't type anything
		mv		R8,R8
		usm		{1000}
		jmpx	end:
		mv		R9,R9
		usm		{1000}
		jmpx	end:



		# if break, not a press
		mv		R5,R5
		jmpz	end:



		# tab		
		mv		R3,[0]
		bsl		R3,[4]
		add		R3,[D]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		add		R0,(4)
		jmp		end:



		# space
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[9]

		sub		R3,R1
		usm		{1000}
		jmprx	(3)
		add		R0,(1)
		jmp		end:



		# enter
		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[A]

		sub		R3,R1
		usm		{1000}
		jmprx	(5)
		bsr		R0,(6)
		add		R0,(1)
		umul	R0,RD
		jmp		end:



		# backspace
		mv		R3,[6]
		bsl		R3,[4]
		add		R3,[6]

		sub		R3,R1
		usm		{1000}
		jmprx	(4)
		sub		R0,(1)
		stchr	RF,R0
		jmp		end:



		# if not caps, can't render
		mv		R3,R7
		add		R3,RA
		usm		{1000}
		jmpnx	end:


		# A
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[C]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[1]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# B
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[2]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[2]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# C
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[1]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[3]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# D
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[3]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[4]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# E
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[4]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[5]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# F
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[B]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[6]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# G
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[4]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[7]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# H
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[3]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[8]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# I
		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[3]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[9]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# J
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[B]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[A]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# K
		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[2]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[B]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# L
		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[B]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[C]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# M
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[A]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[D]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# N
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[1]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[E]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# O
		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[4]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[F]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# P
		mv		R3,[4]
		bsl		R3,[4]
		add		R3,[D]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[0]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# Q
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[5]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[1]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# R
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[D]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[2]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# S
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[B]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[3]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# T
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[C]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[4]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# U
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[C]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[5]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# V
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[A]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[6]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# W
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[D]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[7]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# X
		mv		R3,[2]
		bsl		R3,[4]
		add		R3,[2]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[8]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# Y
		mv		R3,[3]
		bsl		R3,[4]
		add		R3,[5]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[9]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# Z
		mv		R3,[1]
		bsl		R3,[4]
		add		R3,[A]

		sub		R3,R1
		usm		{1000}
		jmprx	(7)

		mv		R3,[5]
		bsl		R3,[4]
		add		R3,[A]

		stchr	R3,R0
		add		R0,(1)
		jmp		end:



		# not break code
end:	mv		R3,[F]
		bsl		R3,[4]

		sub		R3,R1
		usm		{1000}
		mv		R5,{1}
		jmprx	(2)
		mv		R5,{0}
		jmp		loop:
