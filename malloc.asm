DEFINE $SAD	<Rd>, <val>
;	bsl	<Rd>, [4]
;	add	<Rd>, <val>

DEFINE $LDIEX	<Rd>, <val>
;	mv	<Rd>, <val>$3
;	$SAD	<Rd>, <val>$2
;	$SAD	<Rd>, <val>$1
;	$SAD	<Rd>, <val>$0

DEFINE $CDIV	<Rd>, <Div>
;	bsr	<Rd>, <Div>
;	jmpru	[3]
;	add	<Rd>, [1]
;	sub	<Rd>, [1]

	mv	R1, [1]
	bsl	R1, [6]		#Load 64 into R1
	st	R1, [0]  	#Amt of heap memory at mem[1]
	mv	R1, [1]
	bsl	R1, [7]		#Load 64 into R1
	sub	R1, [4]		#Subtract off size of block
	add	R1, [1]		#Set data to free
	st	R1, [2] 	#Init the first memblock



# - - - - Program Begin - - - - 
	
	$LDIEX	Ra, (17)
	mv	R0, Ra
	call	malloc:
	nop
	
	st	Ra, R0

	$LDIEX	Rb, (100)
	mv	R0, Rb
	mv	R4, [0]
	mv	R5, [0]
	mv	R6, [0]
	call	malloc:
	nop
	
	st	Rb, R0
	
	halt
	nop


#Malloc Struct Found at Mem[0]
# 0bAAAAAAAA_AAAAAAAB
# uint A = size / 4
# bool B = isFree
#Finds and allocates a block of `R0` (rounded up to the nearest 4) blocks of double words
# in 	R0  out
#  	R1  clob
#  	R2  clob
#	R3  clob
# zero	R4  clob
# zero	R5  clob
# zero	R6  clob
#	R7  clob
#	R8  clob
#	R9  clob


malloc:	$CDIV	R0, [2]
	mv	R1, [2]		#Ptr to first data
	
	#R7 = EOH ptr
	ld	R7, [0]		#Set R7 to size of heap
	add	R7, [2]		#offset by first block

	#R4 = target ptr
	#R5 = hijack ptr
	#R6 = doSplit

lp01:	ld	R2, R1		# R2 = *R1
	bsr	R2, [1]		# R2 >>= 1
		#Undeflow flag now happens to store `isFree`
	usm	{0001}
	jmpnx	nfree:
	mv	R3, R2		#Copy R2
	sub	R3, R0		#Difference between current mem and target mem
	jmpz	eq:
	sub	R3, [1]		#Decr R3 to test if 1
	jmpn	nfree:		#Skip if negative (will only be if was before, 0 jmp'd away already)
	jmpz	hj:	
	jmp	split:		#If not neg, nor zero, must be pos

split:	mv	R6, [1]		#Do split = true
				#Fall through into eq case
eq:	mv	R4, R1		#Set target
	jmp	end:		#Break loop
	nop

hj:	mv	R5, R1		#Hijack = currptr
				#Fall through
nfree:	mv	R3, R2		#Make a copy of R2	
	add	R1, [2]		#Point to data
	bsl	R3, [2]		#Fast mul R2 by 4
	add	R1, R3		#Offset ptr by amt of data held
	mv	R3, R1		#Make a copy of R1
	sub	R3, R7	
	jmpz	end:		#if R1 == End of Heap, jmp out of loop
	jmp	lp01:
	
end:	mv	R6, R6		#Check R6
	jmpp	nsplt:		#If !doSplit
	mv	R4, R4		#Then
	jmpz	tpz:		#  If tarptr != 0
	nop			#  Then
	bsl	R2, [1]		#    Prepare to write R2, but not free
	st	R2, R4		#    *tarloc = R2	
	add	R4, [2]		#    offset to data
	mv	R0, R4		#    mv to ret reg
	ret			#    return
	nop			#
tpz:	mv	R5, R5		#  Else
	jmpz	hjz:		#    If hijack != 0
	nop			#    Then
	bsl	R2, [1]		#      Prepare to write R2, but not free
	st	R2, R5		#      *hijack = R2	
	add	R5, [2]		#      offset to data
	mv	R0, R5		#      mv to ret reg
	ret			#      return
	nop			#
hjz:	mv	R0, [0]		#    Else
	ret			#      Return Nullptr
	nop			#
				#
nsplt:	mv	R5, R2		#Else, copy size
	#R5, R1, and R6 no longer are needed	
	mv	R6, R5		#  Copy R5, which is size of memory
	sub	R6, R0		#  Excess memory
	sub	R6, [2]	
	mv	R2, R0		#  Copy tarmemsize into R2
	bsl	R2, [1]		#  Prepare to write R2, but not free
	st	R2, R4		#  *tarloc = R2	
	mv	R1, R4		#  Copy R4 into R1
	add	R1, [2]
	bsl	R2, [2]		#  Fast mull by 4
	add	R1, R2		#  R1 is now next block ptr
	#R1 = nextblockptr
	mv	R8, R6		#  Copy of excess mem
	mv	R9, R8		#  Copy of excess mem
	bsl	R6, [1]		#  Prepare to write free flag of R6 (excess memory)
	add	R6, [1]		#  Set it to be free
	st	R6, R1		#  *R1 = R6
	add	R1, [1]		#  prevptr of block
	st	R0, R1		#  Write prevsize if next block to be tarsize
	
	add	R1, [1]
	bsl	R8, [2]		#  Fast mull by 4
	add	R1, R8		#  Set it to be free
	#R1 = next next block ptr
	mv	R2, R1		#  Copy R1
	sub	R2, R7
	jmpz	end2:		#  If next next != end of heap
	add	R1, [1]		#    prevsize ptr of next next
	st	R9, R1		#    Prev size of next next = excess

end2:	add	R4, [2]
	mv	R0, R4		#      mv to ret reg
	ret			#      return
	