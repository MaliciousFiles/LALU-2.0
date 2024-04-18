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



	mv	R0, (12)
	mv	R1, (12)
    	$N $JNE, R0, R1, ne:, R2
	mv	R2, (2)
	halt
ne:	mv	R2, (1)
	halt
