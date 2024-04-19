DEFINE $SAD	<Rd>, <val>
;	bsl	<Rd>, [4]
;	add	<Rd>, <val>

DEFINE $LDIEX	<Rd>, <val>
;	mv	<Rd>, <val>$3
;	$SAD	<Rd>, <val>$2
;	$SAD	<Rd>, <val>$1
;	$SAD	<Rd>, <val>$0

DEFINE $LDI	<Rd>, <val>
;	mv	<Rd>, <val>$1
;	$SAD	<Rd>, <val>$0


DEFINE $CDIV	<Rd>, <Div>
;	bsr	<Rd>, <Div>
;	jmpru	[3]
;	add	<Rd>, [1]
;	sub	<Rd>, [1]

DEFINE	 $N <OP>, <Ra>, <Rb>, <Label>, <Rd>
;	<OP>	<Ra>, <Rb>, <Label>, <Rd>
;	nop

DEFINE 	$MV <Rd>, <OP>, <Ra>, <Rb>
;	mv	<Rd>, <Ra>
;	<OP>	<Rd>, <Rb>

DEFINE 	$JNE <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	usm	{1000}		#Nonzero
;	jmpx	<Label>		#jmp non-zero

DEFINE 	$JEQ <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	jmpz	<Label>		#jmp zero

DEFINE 	$JGE <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	usm	{0100}		#Negative
;	jmpnx	<Label>		#jmp non-neg

DEFINE 	$JGT <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	usmz	{1100}		#Zero or Negative
;	jmpnx	<Label>		#Not (Zero or Neg) -> Pos

DEFINE 	$JLE <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	usmz	{1100}		#Zero or Negative
;	jmpx	<Label>		#jmp Zero or Negative

DEFINE 	$JLT <Ra>, <Rb>, <Label>, <Rd>
;	$MV 	<Rd>, sub, <Ra>, <Rb>
;	jmpn	<Label>		#jmp neg

#Modifies <Ptr> in place, leaving data unmodified
DEFINE 	$BNX <Ptr>, <Data>, <Util>
;	$MV <Util>, 	bsr, <Data>, [1]
;			bsl 	<Data>, [1]
;			add	<Ptr>, [2]
;			add	<Ptr>, <Util>

#Modifies <Ptr> in place, leaving data unmodified
DEFINE 	$BPR <Ptr>, <Data>, <Util>
;	$MV <Util>, 	bsr, <Data>, [1]
;			bsl 	<Data>, [1]
;			sub	<Ptr>, [2]
;			sub	<Ptr>, <Util>

DEFINE	$SUSPEND <narg>
;	halt
;	nop
;	nop

# - - - - Malloc Init - - - - 

	$LDIEX	R1, (64)	#Load 64 into R1
	st	R1, [0]  	#Amt of heap memory at mem[1]
	
	$LDIEX	R1, (64)	#Load 64 into R1.
	sub	R1, [2]		#Subtract off size of block
	bsl	R1, [1]		#Double to add free tag
	add	R1, [1]		#Set data to free
	st	R1, [2] 	#Init the first memblock



# - - - - Program Begin - - - - 
	
	$LDIEX	Ra, (17)	#Initialize some data
	mv	R0, Ra		#Move it into call register

	#$SUSPEND

	call	malloc:		#Call
	nop
	
	st	Ra, R0		#Write the arg to the result as a sample usage
	mv	Rc, R0		#Write back this ptr for later usage

	#$SUSPEND

lpp1:	sub	Ra, [1]
	st	Ra, R0
	add	R0, [1]
	$JNE	Ra, [0], lpp1:, Re
	nop

	#$SUSPEND

	$LDIEX	Rb, (100)
	mv	R0, Rb
	mv	R4, [0]
	mv	R5, [0]
	mv	R6, [0]
	call	malloc:
	nop
	
	st	Rb, R0
	mv	Rd, R0		#Write back this ptr for later usage

	#$SUSPEND

	mv	R0, Rc		#Load Rc / inital malloc ptr
	call	free:
	nop

	mv	R1, Rc
	sub	Rc, [2]
	ld	R0, Rc
	$BNX	Rc, R0, Re
	add	Rc, [2]
	$LDIEX	R0, [abcd]
	st	R0, Rc
	
	$SUSPEND




#Frees the block found at R0
# in 	R0  clob
#  	R1  clob
#  	R2  clob
#  	R3  clob
#	R4  clob
#  	R7  clob
#	Re  clob

free:	sub	R0, [2]			#Offset to tab data
	ld	R1, R0			#Load data at ptr
	or	R1, {1}			#Set last bit to 1, marking it as free
	st	R1, R0
	mv	R2, R0			#Copy R0 (blockptr)
	$BNX	R2, R1, Re		#Get the next block of blockptr in R0, (R3 is junk)
	
	ld	R7, [0]			#Set R7 to EOH ptr
	$JEQ	R2, R7, eif1:, Re	#If next block == EOH (Junk R3)
	ld	R3, R2			#R3 = *R2 = *next
	bsr	R3, [1]			#Lop off last bit of R3, which is if it its free, now holds size of R2
	usm	{0001}			#Underflow bit
	jmpnx	eif1:			#Jmp if that last bit was not free
	nop	

#Free and not EOH
	mv	R4, R3
	add	R4, [1]
	$MV	Re, bsr, R1, [1]	#Get size of R1 in Re
	add	R4, Re			#Add that
	mv	R1, R4			#Set data of R2 to the new data width
	bsl	R1, [1]			#Fast double it back so it can be marked as free
	or	R1, [1]			#Unfortunately have to add back the free bit
	st	R1, R0			#Write back data to memory
	add	R2, [1]			#Increment R2 to point to previous size block
	st	R4, R2			#Write back the original unmodified size
	
eif1:	nop

	mv	R2, R0			#Copy R0 (blockptr)
	$BPR	R2, R1, Re		#Get the prev block of blockptr in R0, (R3 is junk)
	
	$JEQ	R2, [0], eif2:, Re	#If next block == null (Junk R3)
	ld	R3, R2			#R3 = *R2 = *prev
	bsr	R3, [1]			#Lop off last bit of R3, which is if it its free, now holds size of R2
	usm	{0001}			#Underflow bit
	jmpnx	eif2:			#Jmp if that last bit was not free

#Free and not null

	mv	R4, R3			#R4 = R2->size = R3.size = prev.size
	add	R4, [1]
	$MV	Re, bsr, R1, [1]	#Get size of R1 in Re
	add	R4, Re			#Add that
	mv	R1, R4			#Set data of R2 to the new data width
	bsl	R1, [1]			#Fast double it back so it can be marked as free
	or	R1, [1]			#Unfortunately have to add back the free bit
	st	R1, R2			#Write back data to memory at previous node spot
	$BNX	R2, R1, Re		#Make R2 point to the next node of R2 inplace using the just written data and a junk reg
	add	R2, [1]			#Increment to prev size block
	st	R4, R2			#Store prev size

eif2:	ret
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
	add	R7, [0]		#offset by first block

	#R4 = target ptr
	#R5 = hijack ptr
	#R6 = doSplit

lp01:	ld	R2, R1		# R2 = *R1
	bsr	R2, [1]		# R2 >>= 1
		#Undeflow flag now happens to store `isFree`
	usm	{0001}
	jmpnx	nfree:
	$N $JEQ, R2, R0, eq:, 	R3	#Jmp if R2 == R0 (using R3)
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