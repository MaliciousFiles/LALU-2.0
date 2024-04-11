import sys
import pyperclip
from time import sleep
from threading import Thread
import os
import inspect

#Thx Stack Exchange (https://stackoverflow.com/questions/3056048/filename-and-line-number-of-python-script)
def __LINE__() -> int:
    return inspect.currentframe().f_back.f_lineno
def __CALL_LINE__() -> int:
    return inspect.currentframe().f_back.f_back.f_lineno

# valid instructions, case insensitive
OPCODES = {
    'INFO':             ('Opcode' ,'Opclass'),
    'nop':		('0000000',-1),
    'add':	    	('0000001',2),
    'sub':  		('0000010',2),
    'ld':		('0000011',2),
    'mv':		('0000100',2),
    'st':		('0000101',2),

    'bsl':              ('0001100',2),
    'bsr':              ('0001101',2),
    'brl':              ('0001110',2),
    'brr':              ('0001111',2),
    'and':              ('0010000',2),
    'or':               ('0010001',2),
    'xor':              ('0010010',2),
    'any':              ('0010011',2),
    'call':             ('0010100',4),
    'ret':              ('0010101',-1),
    'lfm':              ('0010110',2),
    'usm':              ('0010111',1),
    'usmz':             ('0011000',1),
    
    'lfmz':             ('0011010',2),
    'hsb':              ('0011011',2),
    
    'exjmp':            ('0011110',0),
    'jmp':              ('10'     ,3),
    
    'halt':             ('1111111',-1),
}

fName = sys.argv[1] if len(sys.argv) > 1 else input("Program File: ")
def run(contents):
    print('Run begin')
    # Rx = register index x (in hex)
    # [x] = value of x (only works for Rs)
    # x: = label with name x

    instructions = []
    labels = {}

    def error(msg):
        instructions.append({'error': msg+' (@ Py: '+str(__CALL_LINE__())+')'})
        return



    labelLen = opLen = 0
    addr = 0
    for line in contents.split("\n"):
        line = (line[:line.index("#")] if "#" in line else line).split()
##        print(line)
        if len(line) == 0:
            instructions.append(None)
            continue
        

        # get instruction, and parse label if necessary
        labelDef = ' '
        op = line[0]
        if ":" in op:
            op = op.split(":")
            labelDef = op[0] + ":"
            
            labelLen = max(labelLen,len(op[0]))
            labels[op[0]] = addr
            op = op[1] if op[1] != '' else line.pop(1)
            opLen = max(opLen,len(op))
        if op not in OPCODES.keys() and not op[:3] == 'jmp':
            error("invalid operation")
            break


        # parse registers/immediates if necessary
        label = None
        Rd = None

        value = None
        Rs = None

        iFlag = False
        aFlag = ''
        jFlags = ''

        argStr = ''
        partial_label = None
        oop = op
        annot = None
        if len(line) > 1:
            argStr = ''.join(line[1:])
            
            args = list(filter(lambda s: len(s) > 0, argStr.split(",")))

            if op[:3]=='jmp':
                xfl = op[3:]
                op=op[:3]

                if not (aFlag := 'r' != (xfl+' ')[0]):
                    xfl=xfl[1:]

                try:
                    jFlags = ['','n','z','o','u','p','x', 'nx'].index(xfl)
                except:
                    error('unexpected jmp flag: `'+xfl+'`')
                    break
##                print(xfl,aFlag)
##            print('Prevalidate')
            opClass = OPCODES[op][1]
            
            if len(args) > 2:
                error("more than two args found for op class 2")
                break
##            print('Check 1')
            if len(args) > 1 and opClass in [3, 4]:
                error("more than one arg found for op class 3")
                break
##            print('Check 2')
            if len(args) > 1 and opClass == 1:
                error("more than one arg found for op class 1")
                break
##            print('Check 3')
            if len(args) > 0 and opClass == -1:
                error("args found for op class -1")
                break
##            print('Check 4')
            if ("[" in args[0] or "]" in args[0]) and opClass not in [0, 1, 3]:
##                print('Check 4 Err')
                error("immediates not allowed in Rd")
                break
##            print('Validated')
            if args[0][0] == "R":
                if opClass == 0:
                    error('op class 0 cannot take register arguments')
                    break
                try:
                    Rd = int(args[0][1:], 16)
                except:
                    pass
            if Rd is None and opClass not in [0, 1]:
                if ':' in args[0]:
                    label = args[0][:-1]
                    iFlag = True
                elif opClass != 3:
                    error("unrecognized arg is neither label nor register")
                    break

            if opClass in [0, 1, 3]:
                if args[0][0] == "[":
                    try:
                        value = int(args[0][1:-1], 16)
                        iFlag = True
                    except:
                        error("invalid immediate")
                        break

            if len(args) > 1:
                if args[1][0] == "[":
                    try:
                        value = int(args[1][1:-1], 16)
                        iFlag = True
                    except:
                        error("invalid immediate")
                        break
                else:
                    if args[1][0] != "R":
                        if ':' in args[1]:
                            partial_label = args[1][:-1]
                            iFlag = True
                            
                        else:
                            error("unrecognized arg is neither label nor register")
                            break
                    try:
                        Rs = int(args[1][1:], 16)
                        if Rs > 15:
                            error("register index greater than 15")
                            break
                    except:
                        if ':' in args[1]:
                            partial_label = args[1][:-1]
                            iFlag = True
                            
                        else:
                            error("unrecognized arg is neither label nor register")
                            break

        instructions.append({'op': op, 'op_asm': oop, 'labelDef': labelDef, 'argStr': argStr, 'label': label, 'partial_label': partial_label, 'Rd': Rd, 'Rs': Rs, 'value': value, 'iFlag': iFlag, 'error': None,
                             'aFlag': aFlag, 'jFlags': jFlags, })

        addr += 1
    else:
        print('First Scan Normal')

    def to_binary(num, bits):
        ret = bin(num)[2:]
        if len(ret) > bits:
            print(f"ERROR: invalid binary number '{num}' for bit length '{bits}': {ret}")

        return ret.rjust(bits, "0")

    print('Program print')

##    print(labels)
    
    program = ""
    addr = 0


    if len(list(filter(lambda i: i is not None, instructions))) > 0:
        casc_err = list(filter(lambda i: i is not None, instructions))[-1]['error'] is not None
        
        for instr in instructions:
            if instr is None:
                print()
                continue
        
            code = ""
            
            if instr['error'] is not None:
                print(f"ERROR: {instr['error']}")
                return

            opclass = OPCODES[instr['op']][1]

            if opclass == -1:
                code += '0'*9
                code += OPCODES[instr['op']][0]

            if opclass == 0:
                code += to_binary(instr['value'],9)
                code += OPCODES[instr['op']][0]

            if opclass == 1:
                if instr['label'] is not None:
                    if instr['label'] not in labels:
                        print("ERROR: label not found"+(" caused by cascade error")*casc_err)
                        if not casc_err:
                            return
                    else:
                        code += to_binary(labels[instr['label']], 9)

                else:
                    code += '0000' 
                    if (pl:=instr['partial_label'])!=None:
                        rootlabel,part = pl.split('$');part = int(part,16)
                        partial_label = to_binary(labels[rootlabel], 16)[::-1][4*part:4+4*part][::-1]
                        code += partial_label
                        instr['annot']='#0b'+('....'*(2-part)+partial_label+'....'*(part))[3:]
                    else:
                        code += to_binary(instr['value'] if instr['value'] is not None else instr['Rs'], 4)
                    code += '1' if instr['iFlag'] else '0'
                code += OPCODES[instr['op']][0]

            if opclass == 2:
                if instr['label'] is not None:
                    if instr['label'] not in labels:
                        print("ERROR: label not found"+(" caused by cascade error")*casc_err)
                        if not casc_err:
                            return
                    else:
                        code += to_binary(labels[instr['label']], 9)

                else:
                    code += to_binary(instr['Rd'] if instr['Rd'] is not None else instr['value'], 4) 
                    if (pl:=instr['partial_label'])!=None:
                        rootlabel,part = pl.split('$');part = int(part,16)
                        partial_label = to_binary(labels[rootlabel], 16)[::-1][4*part:4+4*part][::-1]
                        code += partial_label
                        instr['annot']='#0b'+('....'*(2-part)+partial_label+'....'*(part))[3:]
                    elif opclass == 2:
                        code += to_binary(instr['value'] if instr['value'] is not None else instr['Rs'], 4)
                    else:
                        code += '0000'
                    code += '1' if instr['iFlag'] else '0'
                code += OPCODES[instr['op']][0]

            elif opclass == 3:
                if instr['label'] is not None:
                    if instr['label'] not in labels:
                        print("ERROR: label not found"+(" caused by cascade error")*casc_err)
                        if not casc_err:
                            return
                    else:
                        code += to_binary(labels[instr['label']], 9)

                else:
    ##                print(instr)
                    code += to_binary(instr['value'] if instr['value'] is not None else instr['Rd'], 9)
                    

                code += OPCODES[instr['op']][0]
                code += '1' if instr['aFlag'] else '0'
                code += '1' if instr['iFlag'] else '0'
                code += to_binary(instr['jFlags'], 3)

            elif opclass == 4:
                if instr['label'] is not None:
                    if instr['label'] not in labels:
                        print("ERROR: label not found"+(" caused by cascade error")*casc_err)
                        if not casc_err:
                            return
                    else:
                        code += to_binary(labels[instr['label']], 9)

                else:
                    code += to_binary(instr['value'] if instr['value'] is not None else instr['Rd'], 9)
                    
                code += OPCODES[instr['op']][0]

            # to_binary must have errored already, so don't need to worry about printing
            if len(code) > 16:
                return

            code = hex(int(code, 2))[2:].rjust(4, "0")
            program += code+" "


    ##        print(instr)
            print(f"[{hex(addr)[2:].rjust(2, '0')}] {code}  {instr['labelDef'].rjust(labelLen+1, ' ')} {instr['op_asm'].ljust(opLen, ' ')}\t\t{instr['argStr']}\t\t{instr.get('annot','')}")


            addr += 1

        
    

    print(f"\nTotal instruction count: {addr}")
    print("\nProgram Memory (added to clipboard)")
    print(program)
    pyperclip.copy(program)


inp = None

def monitor_input():
    global inp
    
    while True:
        inp = input().strip()
        if inp == "q":
            os._exit(1)


if __name__ == "__main__":
    with open(fName) as f:
        if "--monitor" in sys.argv[2:]:
            Thread(target=monitor_input).start()
            
            contents = None
            while True:
                f.seek(0)
                newContents = f.read()
                
                if inp is not None or newContents != contents:
                    inp = None
                    contents = newContents
                    
                    os.system("clear")
                    run(contents)
        else:
            run(f.read())


#y=0x0084;x=bin(y)[2:].rjust(16,'0');print(x[0:4],x[4:8],x[8],x[9:16])
#y=0x03dd;x=bin(y)[2:].rjust(16,'0');print(x[0:9],x[9:11],x[11],x[12],x[13:16])
#for self
