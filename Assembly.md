# LALU Instruction Set Manual
## Wordcode Formating

Most opcodes fall under one of six different formats (`DS`, `D`, `S`, `TS`, `I`, & `J`), they are as follows:

```
2 Register Codes: DS
F E D C B A 9 8 7 6 5 4 3 2 1 0
   Rd  |   Rs  |i|     Op
```
```
1 Register Codes: D
F E D C B A 9 8 7 6 5 4 3 2 1 0
       |   Rd  | |     Op
```
```
1 Register Codes: S
F E D C B A 9 8 7 6 5 4 3 2 1 0
  Imm  |   Rs  |i|     Op
```
```
1 Register Codes: TS
F E D C B A 9 8 7 6 5 4 3 2 1 0
       |   Rs  |i|     Op
```
```
0 Register Codes: I
F E D C B A 9 8 7 6 5 4 3 2 1 0
      Data       |     Op
```
```
Jump: J
F E D C B A 9 8 7 6 5 4 3 2 1 0
   Imm   |  Reg  | Op|a|i|Flags
```
 * For `DS`, `D` and `S` formats, `Rd` and `Rs` are Destination and Source Registers respectively, being a four bit register id. 
 * If the `i` flag is set, then `Rs` will be interperitted as an immediate value instead of a read from registers.
    *  If there is a segment of bits labeled `Imm`, these will be only used as extensions to the immediate.
 * `Data` is a segment of bits used as a larger immediate and which can never be a register id
 * `Op` which is normally 7 bits at the end to distinguish similar opcodes is only two bit for `J` formats
 * `Flags`, like `Data` is a specific bit code used to specify the condition underwhich to jump
    * Bitcode = Explanation (-suffix)
    * 000 = Uncondition (-)
    * 001 = Negative (-n)
    * 010 = Zero (-z)
    * 011 = Overflow (-o)
    * 100 = Underflow (-u)
    * 101 = Parity (-p)
    * 110 = Util (-x)
    * 111 = Not Util (-nx)
 * `a` is a bit flag indicating if the jump is by a relative amount (0) or an absolute amount (1)
 * 
 
## Kernel Features
The CPU has two modes, Protected and Super. Super is unregulated and can attempted to run any opcode it wants as well as access all of memory. To enable user applications which dont control the entire computer, it can enter protected mode which stores a pointer into readable memory (also the user's relative memory), and a length of its readable memory. the CPU can also choose to restrict the number of available registers if it needs to keep a persistant register value known. System calls can be handled by calling `sar` and having the OS then run code on the supplied arguments. 

 - Call `enpr` to jump and enter protection
	 - Push a new stack frame, store current stack pointer
 - Call `expr` to exit protection, which will jump to exit
	 - Pop stack frames back to stored stack pointer
 - Call `sar` (Super Application Request) to exit protection, jump to `handle`, and push the protected return address to the stack.
	 - Push a new stack frame
 - Call `par` (Protected Application Resume) to return and enter protection
	 - Pop a stack frame

There are two special opcodes assocated with Kernel Instructions. The `w` flag here indicates setting write mode on a `1` and setting read mode on a `0`.

```
Jump: IIM
F E D C B A 9 8 7 6 5 4 3 2 1 0
  Imm  |  Imm  |w|     Op   
```
```
Jump: RRM
F E D C B A 9 8 7 6 5 4 3 2 1 0
  Reg  |  Reg  |w|     Op   
```

## Current Opcodes
```
Opcodes (00...): //Core opcodes
Bits	Class    Mnemonic       Pseudocode / Name
6543210
0000000	——	 nop 		
0000001 DS	 add		Rd += Rs
0000010 DS	 sub		Rd -= Rs
0000011	DS	 ld 		Rd = *Rs
0000100	DS-	 mv 		Rd = Rs
0000101	DS-	 st	    	*Rs = Rd
0000110	DS-	 smul           (Signed) Rd *= Rs
0000111	DS	 umul           (Unsigned) Rd *= Rs
0001000	S-	 psh		Stk[idx++] = Rs
0001001	D	 pop		Rs = Stk[idx--]
0001010	D	 ldkey 	        Rs = @ldkey()  //Load key from keyboard buffer
0001011	DS	 stchr          vRAM[Rs] = Rd  //Write to video buffer
0001100	DS	 bsl		Rd <<= Rs % 16
0001101	DS	 bsr		Rd >>= Rs % 16
0001110	DS	 brl		Rd <<<= Rs % 16
0001111	DS	 brr		Rd >>>= Rs % 16
0010000	DS	 and		Rd &= Rs
0010001	DS	 or	        Rd |= Rs
0010010	DS	 xor		Rd ^= Rs
0010011	DS	 any 	        Rd = Rs ? 1 : 0
0010100	J	 call		
0010101	——	 ret		
0010110	DS	 lfm		Rd = (flags & (Rs % 16)) ? 1 : 0
0010111	TS	 usm		flags.util = flags & (Rs % 16)  //Will be replaced with a cmp command in the future
0011000	TS	 usmz	        flags.util = zflags & (Rs % 16)
0011001	DS	 rsub	        Rd = Rs - Rd 
0011010	DS	 lfmz 	        Rd = (zflags & (Rs % 16)) ? 1 : 0
0011011	DS	 hsb		Rd = HighestSetBit(Rs)
0011100		  - Nop - 
0011101		  - Nop - 
0011110	I	 exjmp**	Extend jump  //Set highest bits for jmp, assembler does this implicitly, so `I` format
0011111		  - Nop - 

Opcodes (01...): //Kernel Opcodes
Bits	Class    Mnemonic       Pseudocode / Name
0100000	IIM	 prreg***	Mask accessible registers
0100001	RRM	 prmem***	Mask accessible data memory
0100010	RRM	 prprg***	Mask accessible program memory
0100011	TS	 prext*	        Set exit location in protection
0100100	TS	 prhdl*	        Set handle location in protection
0100101	TS	 enpr*	        Jump absolute and enter protection
0100110	I	 expr**	        Jump to `exit` and exit protection
0100111	I	 sar**	        Super application request
0101000	I	 par**	        Protected application resume

Opcodes (10...): //Reserved for jumps
Bits	Class    Mnemonic       Pseudocode / Name
10.....	J	 jmp		Special, specified above

Opcodes (11...): //Mostly unused set of codes, might be used for accelerated instructions
Bits	Class    Mnemonic       Pseudocode / Name
1111111	——	 halt	        Exit()
```
