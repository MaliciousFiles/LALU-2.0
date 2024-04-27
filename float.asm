DEFINE $SAD	<Rd>, <val>
;	bsl	<Rd>, [4]
;	add	<Rd>, <val>

DEFINE $LDIEX	<Rd>, <val>
;	mv	<Rd>, <val>$3
;	$SAD	<Rd>, <val>$2
;	$SAD	<Rd>, <val>$1
;	$SAD	<Rd>, <val>$0

DEFINE $DADD	<URd>, <LRd>, <URs>, <LRs>
;SCOPE BEGIN
;	add	<LRd>, <LRs>
;	jmpo	skip:
;	add	<URd>, [1]
;	sub	<URd>, [1]
;skip: 	add	<URd>, <URs>
;SCOPE END

DEFINE	$SUSPEND <narg>
;	halt
;	nop
;	nop

DEFINE $SHB	<Rd>, <Rs>
;	bsl	<Rd>, [1]
;	or	<Rd>, <Rs>
;	brr	<Rd>, [1]

DEFINE	$TRUEHALT <narg>
;SCOPE BEGIN
;loop:	halt
;	nop
;	nop
;	jmp loop:
;SCOPE END

DEFINE $JMPNZ <label>
;	usm	{1000}
;	jmpx	<label>

#Note to self, this is the format of packed floats:
# Ra: 0bSEEEEEEE_EMMMMMMM    Rb: 0xMMMM_MMMM
#It is across two registers for 32 bit width, with highest bit as sign, next 8 as exp, and then 23 for mantissa

#Unpacks <Ra> into <Sign>, <Exp>, and uses <Ra> as the high val of <Man>
DEFINE $UPKFL <Ra>, <Sign>, <Exp>
;	bsl	<Ra>, [1]		#0b EEEEEEEE_MMMMMMM0
;	lfm	<Sign>, {0010}
;	mv	<Exp>, <Ra>		#0b EEEEEEEE_MMMMMMM0
;	bsr	<Exp>, [8]		#0b 00000000_EEEEEEEE
;	bsl	<Ra>, [8]		#0b MMMMMMM0_00000000
;	add	<Ra>, [1]		#0b MMMMMMM0_00000001
;	brr	<Ra>, [1]		#0b 1MMMMMMM_00000000
;	bsr	<Ra>, [8]		#0b 00000000_1MMMMMMM

# - - - - - - - - MAIN - - - - - - - - 
	$LDIEX	R0, {0000000000101010}		#Sign = +, Exp = +0, Man = 1.5
	$LDIEX	R1, {1010101010101010}		#More Man
	$UPKFL	R0, R2, R3			#Sign = R2, Exp = R3, UMan = R0, LMan = R1

	$LDIEX	R4, {00000000000000000}		#Sign = +, Exp = +0, Man = 1.
	$LDIEX	R5, {00000000000000000}		#More Man
	$UPKFL	R4, R6, R7			#Sign = R6, Exp = R7, UMan = R4, LMan = R5

	$SUSPEND

# - - - - FLOAT TO DECIMAL - - - - 
	psh	R0
	psh	R1
	
	nop
	call	fl2dec:
	nop
	
	pop	R1
	pop	R0
	
	$SUSPEND

	$DADD	R0, R1, R4, R5			#Add Man0, Man1
	mv	R8, R0
	bsr	R8, [8]				#Nonzero means it has a higher exp now
	jmpz	skip:				#Jmpz
	bsr	R0, [1]				#Bitshift lower bits
	jmpu	lbo:
	bsr	R1, [1]				#Exploit always run to truncate right
	bsl	R1, [1]				#If here, need to set highest bit, so go left
	or	R1, [1]				#Put 1 in lowest bit
	brr	R1, [1]				#Wrap it around
lbo:	nop
skip:	nop

	$TRUEHALT


#  in  R0  clob		#Upper 8 bits
#  in  R1  clob		#Lower 16 bits
#      R9  clob
#      Ra  out		#Upper 4 digs
#      Rb  clob
#      Rc  clob
#      Rd  out		#Lower 4 digs

fl2dec:	$LDIEX	R8, {1000100010001000}		#Nibble high bits
SCOPE BEGIN
	mv	R9, [1]				#Lowest bit
	brr	R9, [1]				#Highest bit
	mv	Ra, [0]				#Initalize bcd rep
	mv	Rd, [0]				#Initalize bcd rep reg 2

	mv	Rc, (8)				#How many bits to read off
	jmp	cmp:				#Jump to the test
	nop

1loop:	or	Ra, R9				#Set highest bit
0loop:	mv	Rb, Ra				#Copy
	and	Rb, R8				#And to create mask
	xor	Ra, Rb				#Just go ahead and zero those bits
	bsr	Rb, [3]				#Get its bit right align
	umul	Rb, (5)				#Now all the ones have a 5, and otherwise 0
	add	Ra, Rb

	mv	Rb, Rd				#Copy
	and	Rb, R8				#And to create mask
	xor	Rd, Rb				#Just go ahead and zero those bits
	bsr	Rb, [3]				#Get its bit right align
	umul	Rb, (5)				#Now all the ones have a 5, and otherwise 0
	add	Rd, Rb

	#$SUSPEND

	sub	Rc, [1]
cmp:	jmpz	end:
	nop
	bsr	Rd, [1]
	bsr	Ra, [1]
	jmpru	[3]				#If the bit knocked off was 1
	jmpr	[3]
	nop
	or	Rd, R9

	bsr	R0, [1]
	jmpu	1loop:				#if the lowest bit was 1
	jmp	0loop:				#Otherwise jmp past
end:	nop
	mv	R0, R1				#Load in extra bits
	usm	{1000}				#Store util flag for jmp
	mv	R1, [0]				#Zero R1 so that next time through it doesnt repeat
	mv	Rc, [1]				#number of bits to read off
	bsl	Rc, [4]				#Load 16
	jmpx	cmp:				#jump if util flag set actually matters	
	nop
	ret
SCOPE END