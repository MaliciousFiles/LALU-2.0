DEFINE $SAD	<Rd>, <val>
;	bsl	<Rd>, [4]
;	add	<Rd>, <val>

DEFINE $LDIEX	<Rd>, <val>
;	mv	<Rd>, <val>$3
;	$SAD	<Rd>, <val>$2
;	$SAD	<Rd>, <val>$1
;	$SAD	<Rd>, <val>$0

DEFINE	$SUSPEND <narg>
;	halt
;	nop
;	nop

DEFINE	$TRUEHALT <narg>
;SCOPE BEGIN
;loop:	halt
;	nop
;	nop
;	jmp loop:
;SCOPE END


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
	$LDIEX	R0, {00000000000000000}		#Sign = +, Exp = +0, Man = 1.
	$LDIEX	R1, {00000000000000000}		#More Man
	$UPKFL	R0, R2, R3			#Sign = R2, Exp = R3, UMan = R0, LMan = R1


	$TRUEHALT
