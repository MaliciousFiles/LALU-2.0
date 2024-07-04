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

# OP Classes
# -2 = exjmp (handled really weird)
# -1 = no parameters
# 1 = one parameter (Rs)
# 1.5 = one parameter (Rd)
# 2 = two parameters
# 2.5 = prot mask (immediate)
# 2.6 = prot mask (register)
# 3 = jump
# 3.5 = call

# valid instructions, case insensitive
OPCODES = {
    'INFO':             ('Opcode' ,'Opclass'),
    'nop':              ('0000000',-1),
    'add':              ('0000001',2),
    'sub':              ('0000010',2),
    'ld':               ('0000011',2),
    'mv':               ('0000100',2),
    'st':               ('0000101',2),
    'smul':             ('0000110',2),
    'umul':             ('0000111',2),

    'bsl':              ('0001100',2),
    'bsr':              ('0001101',2),
    'brl':              ('0001110',2),
    'brr':              ('0001111',2),
    'and':              ('0010000',2),
    'or':               ('0010001',2),
    'xor':              ('0010010',2),
    'any':              ('0010011',2),
    'call':             ('0010100',3.5),
    'ret':              ('0010101',-1),
    'lfm':              ('0010110',2),
    'usm':              ('0010111',1),
    'usmz':             ('0011000',1),
    'psh':              ('0001000',1.5),
    'pop':              ('0001001',1.5),
    
    'lfmz':             ('0011010',2),
    'hsb':              ('0011011',2),

    'prreg':            ('0100000',2.5),
    'prmem':            ('0100001',2.6),
    'prprg':            ('0100010',2.6),
    'prext':            ('0100011',3.6),
    'prhdl':            ('0100100',3.6),
    'enpr':             ('0100101',3.6),
    'expr':             ('0100110',-1),
    'sar':              ('0100111',-1),
    'par':              ('0101000',-1),
    
    'exjmp':            ('0011110',-2),
    'jmp':              ('10'     ,3),
    
    'halt':             ('1111111',-1),
}

fName = sys.argv[1] if len(sys.argv) > 1 else input("Program File: ")

class MacroError(Exception):        #Just makes a custom Exception class so its own errors can be caught
    def __init__(self,message):
        super().__init__(message)

def errormsg(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MacroError as e:
            print(e)
    return inner
            

@errormsg
def macroEXP(contents,verb=False):
    print('Macro Expansion begin')

    macs = {}
    olines = []
    nlines=[{}]
    clines=[]
    lbp=[]      #Out of scope labels
    lbsp=[[]]     #Inscope labels
    nolbl=[]

    def error(msg):
        raise MacroError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')')
        return
    def tweakLabel(lbl):
        lbl=lbl
        abc='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        flt = []
        for lbs in lbsp:
            flt += [x[0] for x in lbs]
        flt+=lbp
        flt+=nolbl
        if verb:
            print(f'{flt=}')
        while lbl in flt:
            lbls=list(lbl)[:-1]
            j = 1
            while (i:=abc.index(lbls[-j]))==len(abc)-1:
                lbls[-j]=abc[0]
                j+=1
                if j > len(lbls):
                    lbls=['a']+lbls
            lbls[-j]=abc[i+1]
            lbl=''.join(lbls)+':'
        nolbl.append(lbl)
        return lbl
            

    isMac = False

    lines = [('Line '+str(lnum+1), line) for lnum, line in enumerate(contents.split("\n"))]
    lines = [(None,'SCOPE BEGIN')]+lines+[(None,'SCOPE END')]
    while len(lines)>0:
        source,line = lines.pop(0)
        if verb:
            print(f'Read {line!r} from {source}')
        line = (line[:line.index("#")] if "#" in line else line).split()
        if len(line) == 0:
            continue
        if isMac:
            if line[0][0] == ';':
                line[0]=line[0][1:]
                if line[0] == '':
                    del line[0]
                macsource = macs[macname][0]
                newsource = macname+' '+source
                macs[macname][2].append((newsource, ' '.join(line)))
            else:
                isMac = False
        if not isMac:
            if line[0] == 'SCOPE' and line[1] == "BEGIN":
                if verb:
                    print('Scope begin')
                lbsp.append([])
                clines.append([])
                cldrn=nlines[-1].get('Children',[])
                cldrn.append({})
                nlines[-1]['Children']=cldrn
                nlines.append(cldrn[-1])
                continue
            elif line[0] == 'SCOPE' and line[1] == "END":
                if verb:
                    print('Scope end')
                nlps=lbsp.pop(-1)
                lbp+=[x[0] for x in nlps]
                child=nlines.pop(-1)
                child['lbls']=nlps
                child['code']=clines.pop(-1)
                continue
            if line[0] == 'DEFINE':
                isMac = True
                macname = line[1]
                if not ('$' == macname[0] and (macname[1].isalpha() or macname[1] == '_')):
                    if not '$' == macname[0]:
                        error(f'macro @ {source} does not begin with $')
                    else:
                        error(f'macro @ {source} does not begin with letter or _')
                    return
                if macname in macs.keys():
                    error(f'macro @ line: {source} has same name as prexisting macro')
                    return
                args = [x for x in [x.strip() for x in ''.join(line[2:]).split(',')] if x != None]
                for arg in args:
                    if not (arg[0]=='<' and arg[-1] == '>' and len(arg)>2 and ' ' not in arg):
                        if not (arg[0]=='<' and arg[-1] == '>'):
                            error(f'macro @ line: {source} argument must be wrapped in < >')
                        if not (len(arg)>2):
                            error(f'macro @ line: {source} argument must have identifier in angle brackets')
                        if not (' ' not in arg):
                            error(f'macro @ line: {source} argument cannot contain whitespace')
                        return
                macs[macname]=(source,args,[])
            else:
                op = line[0]
                labelDef = None
                if verb:
                    print(f'Prewrite {line!r}')
                if ":" in op:
                    op = op.split(":")
                    labelDef = op[0] + ":"
                    
                    op = op[1] if op[1] != '' else line[1]
                if op[0]=='$':
                    if op not in macs:
                        error(f'macro call @ line: {source} is undefined')
                        return
                    else:
                        ms, margs, mlines = macs[op]
                        if labelDef != None:
                            args = [x for x in [x.strip() for x in ''.join(line[2:]).split(',')] if x != None]
                        else:
                            args = [x for x in [x.strip() for x in ''.join(line[1:]).split(',')] if x != None]
                        if len(args) != len(margs):
                            error(f'macro call @ line: {source} has argument mismatch')
                            return
                        app=[]
                        for line in mlines:
                            ls, lv = line
                            for marg,arg in zip(margs,args):
                                lv = lv.replace(marg,arg)
                            ls = source + ' -> '+ls
                            app.append((ls, lv))
                        if labelDef != None:
                            app[0]=(app[0][0],labelDef +' '+ app[0][1])
                        if verb:
                            print(f"Pushback: {app!r}")
                        lines = app + lines
                else:
                    if labelDef != None:        #There was a label
                        if verb:
                            print(f"Label found: `{labelDef}`")
                            print(f'{lbsp=}')
                        for lps in lbsp[:-1]:                   #Label collisions in lower scopes result in an override cuz thats useful behavior
                            if labelDef in [x[0] for x in lps]:
                                lbl, src, rep = [x for x in lps if x[0]==labelDef][0]
                                nlbl = tweakLabel(labelDef)
                                lbsp[-1].append((labelDef,source,nlbl))
                                if verb:
                                    print(f'Label `{labelDef}` renamed to `{nlbl}` from lower scope collision, {lbsp=}')
                                break
                        else:
                            lps=lbsp[-1]
                            if labelDef in [x[0] for x in lps]:
                                lbl, src, rep = [x for x in lps if x[0]==labelDef][0]
                                error(f'Label definition @ {source} collides with previously named label `{labelDef}` from {src} in current scope'+
                                      f'\n :: {lps=}')
                                return
                            else:
                                nlbl=labelDef
                                if labelDef in lbp:
                                    nlbl = tweakLabel(labelDef)
                                    if verb:
                                        print(f'Label `{labelDef}` renamed to `{nlbl}` from past scope collision')
                                lbsp[-1].append((labelDef,source,nlbl))
                                if verb:
                                    print(f'Label `{labelDef}` pushed, {lbsp=}')
                            
                    if verb:
                        print(f'Write {line!r} from {source}')
                    clines[-1].append(line)
                    olines.append((source,line))
##    nlines[-1]['lbls']=lbsp[-1]
    
    baseScope = nlines[0]['Children'][0]
    if verb:
        print(f'{baseScope=}')
    scopes=[baseScope]
    while scopes != []:
        scope=scopes.pop(0)
        cldrn = scope.get('Children',None)
        if cldrn != None:
            scopes=cldrn+scopes

        lbs=[x[0] for x in scope['lbls']]
        for line in scope['code']:
            for i,v in enumerate(line):
                if v in lbs:
                    line[i]=scope['lbls'][lbs.index(v)][2]
    return olines
            

def run(contents, preprocessed = True):

    if contents == None:
        return
    
    print('Run begin')
    # Rx = register index x (in hex)
    # [x] = value of x (only works for Rs)
    # x: = label with name x

    instructions = []
    labels = {}

    def error(msg):
        nonlocal source, line
        instructions.append({'error': msg+f' (@ {source}) '+'(@ Py: '+str(__CALL_LINE__())+')'+'\n->\t'+f'{" ".join(line)}'+'\nInternally: '+f'{line!r}'})
        return

    def ImGetNib(val, nibID):
        return int(val // 16**nibID) % 16

    labelLen = opLen = antLen = argLen = 0
    addr = 0

    data = contents if preprocessed else list(enumerate(contents.split("\n")))
    for source, line in data:
        if not preprocessed:
            line = (line[:line.index("#")] if "#" in line else line).split()
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
        if op not in OPCODES and not op[:3] == 'jmp' and not (op[:2] == 'pr' and op[:5] in OPCODES):
            error("invalid operation")
            break


        # parse registers/immediates if necessary
        label = None
        Rd = None

        value = None
        rdValue = None
        Rs = None

        iFlag = False
        aFlag = ''
        jFlags = ''

        argStr = ''
        partial_label = None
        oop = op
        annot = None
        retNorm = False
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

            protMaskRe = None
            if op not in OPCODES and op[:2] == 'pr' and op[:5] in OPCODES:
                if op[5:] not in ['RE', 'WR']:
                    error('unexpected prot mask flag: `'+op[5:]+'`')
                protMaskRe = op[5:] == 'RE'
                op = op[:5]

##                print(xfl,aFlag)
##            print('Prevalidate')
            opClass = OPCODES[op][1]
            
            if len(args) > 2:
                error("more than two args found for op class 2")
                break
##            print('Check 1')
            if len(args) > 1 and int(opClass) == 3:
                error("more than one arg found for op class 3")
                break
##            print('Check 2')
            if len(args) > 1 and int(opClass) == 1:
                error("more than one arg found for op class 1/1.5")
                break
##            print('Check 3')
            if len(args) > 0 and opClass == -1:
                error("args found for op class -1")
                break
##            print('Check 4')
            if ("[" in args[0] or "]" in args[0] or "(" in args[0] or ")" in args[0] or "{" in args[0] or "}" in args[0]) and opClass not in [0, 1, 2.5, 3]:
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
            if Rd is None and opClass not in [0, 1, 2.5]:
                if ':' in args[0]:
                    label = args[0][:-1]
                    iFlag = True
                elif opClass != 3:
                    error("unrecognized arg is neither label nor register")
                    break

            if opClass in [0, 1, 2.5, 3]:
                if args[0][0] in ["[","(","{"]:
                    try:
                        nib = None
                        if '$' in args[0]:
                            args[0],nib = args[0].split('$')
                        rdValue = int(args[0][1:-1], 16 if args[0][0] == "[" else 10 if args[0][0] == "(" else 2)
                        if nib != None:
                            rdValue = ImGetNib(rdValue,nib)
                        iFlag = True
                    except:
                        error("invalid immediate")
                        break

            if len(args) > 1:
                if args[1][0] in ["[","(","{"]:
                    if opClass == 2.6:
                        error("immediates not allowed in opclass 2.6")
                    try:
                        nib = None
                        if '$' in args[1]:
                            args[1],nib = args[1].split('$')
                        value = int(args[1][1:-1], 16 if args[1][0] == "[" else 10 if args[1][0] == "(" else 2)
                        if nib != None:
                            value = ImGetNib(value,int(nib))
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
                            error("unrecognized second arg is neither label nor register")
                            break
                    try:
                        Rs = int(args[1][1:], 16)
                        if Rs > 15:
                            error("second register index greater than 15")
                            break
                    except:
                        if ':' in args[1]:
                            partial_label = args[1][:-1]
                            iFlag = True
                            
                        else:
                            error("unrecognized second arg is neither label nor register")
                            break

            if opClass == 2.5 and (rdValue is None or value is None):
                error("only immediates allowed in opclass 2.5")

        instructions.append({'op': op, 'op_asm': oop, 'labelDef': labelDef, 'argStr': argStr, 'label': label, 'partial_label': partial_label, 'Rd': Rd, 'Rs': Rs, 'value': value, 'iFlag': iFlag, 'error': None,
                             'aFlag': aFlag, 'jFlags': jFlags, 'source': source, 'protMaskRe': protMaskRe, 'rdValue': rdValue})
        argLen = max(argLen, len(argStr))
        
        addr += 1
    else:
        print('First Scan Normal')
        retNorm = True
    if not retNorm:
        print(f"First Scan Abnormal: {line}")

    def to_binary(num, bits, err=True):
        ret = bin(num)[2:]
        if err and len(ret) > bits:
            print(f"ERROR: invalid binary number '{num}' for bit length '{bits}': {ret}"+' (@ Py: '+str(__CALL_LINE__())+')')

        return ret.rjust(bits, "0" if num >= 0 else "1")

    print('Program print')

##    print(labels)
    
    program = ""
    addr = 0


    if len(list(filter(lambda i: i is not None, instructions))) > 0:
        casc_err = list(filter(lambda i: i is not None, instructions))[-1]['error'] is not None

        previnstr = None
        for instr in instructions:
            if instr is None:
                print()
                continue

            if instr['error'] is not None:
                print(f"ERROR: {instr['error']}")
                return


            opclass = OPCODES[instr['op']][1]

            if previnstr is not None and previnstr['op'] == 'exjmp' and int(opclass) != 3:
                print("ERROR: exjmp precedes non-jmp instruction")
                return

            code = ""

            def addLabel():
                if instr['label'] is not None:
                    if instr['label'] not in labels:
                        print("ERROR: label not found"+(" caused by cascade error")*casc_err)
                        if casc_err:
                            print(f"ERROR: {list(filter(lambda i: i is not None, instructions))[-1]['error']}")
                        return ('ret' if not casc_err else '',)
                    else:
                        immLen = 8 if opclass == 3.6 else 9

                        loc = to_binary(labels[instr['label']], immLen, False)
                        prog = ""
                        if len(loc) > immLen:
                            if previnstr is None or previnstr['op'] != 'exjmp':
                                print("ERROR: exjmp required immediately above to expand jump destination")
                                return ('ret',)

                            code = "00" + to_binary(labels[instr['label']], 16)[:(16-immLen)] + OPCODES['exjmp'][0]
                            prog = hex(int(code, 2))[2:].rjust(4, "0")+" "

                            print(f"[{hex(addr-1)[2:].rjust(3, '0')}] {prog}  {previnstr['labelDef'].rjust(labelLen+1, ' ')} {previnstr['op_asm'].ljust(opLen, ' ')}\t\t{previnstr['argStr']}\t\t{previnstr.get('annot','')}")
                        return (loc[-immLen:], prog)

            if opclass == -1:
                code += '0'*9
                code += OPCODES[instr['op']][0]

            if opclass == 0:
                code += to_binary(instr['rdValue'],9)
                code += OPCODES[instr['op']][0]

            if opclass == 1:
                lbl = addLabel()
                if type(lbl) == tuple:
                    if lbl[0] == 'ret' or lbl[0]=='':
                        return
                    code += lbl[0]
                    program += lbl[1]
                else:
                    code += '0000' 
                    if (pl:=instr['partial_label'])!=None:
                        rootlabel,part = pl.split('$');part = int(part,16)
                        partial_label = to_binary(labels[rootlabel], 16)[::-1][4*part:4+4*part][::-1]
                        code += partial_label
                        instr['annot']='#0b'+('....'*(2-part)+partial_label+'....'*(part))[3:]
                        antLen = max(argLen, len(instr['annot']))
                    else:
                        code += to_binary(instr['value'] if instr['value'] is not None else instr['rdValue'] if instr['rdValue'] is not None else instr['Rs'], 4)
                    code += '1' if instr['iFlag'] else '0'
                code += OPCODES[instr['op']][0]

            if opclass == 1.5:
                code = to_binary(instr['Rd'], 4)+"00000"+OPCODES[instr['op']][0]
            
            if int(opclass) == 2:
                lbl = addLabel()
                if type(lbl) == tuple:
                    if lbl[0] == 'ret' or lbl[0]=='':
                        return
                    code += lbl[0]
                    program += lbl[1]
                else:
                    code += to_binary(instr['Rd'] if instr['Rd'] is not None else instr['rdValue'], 4) 
                    if (pl:=instr['partial_label'])!=None:
                        rootlabel,part = pl.split('$');part = int(part,16)
                        partial_label = to_binary(labels[rootlabel], 16)[::-1][4*part:4+4*part][::-1]
                        code += partial_label
                        instr['annot']='#0b'+('....'*(2-part)+partial_label+'....'*(part))[3:]
                    else:
                        code += to_binary(instr['value'] if instr['value'] is not None else instr['Rs'], 4)
                    
                    if opclass == 2:
                        code += '1' if instr['iFlag'] else '0'
                    elif opclass == 2.5 or opclass == 2.6:
                        code += '1' if instr['protMaskRe'] else '0'
                code += OPCODES[instr['op']][0]

            elif int(opclass) == 3:
                lbl = addLabel()
                if type(lbl) == tuple:
                    if lbl[0] == 'ret' or lbl[0]=='':
                        return
                    code += lbl[0]
                    program += lbl[1]
                else:
    ##                print(instr)
                    code += to_binary(instr['rdValue'] if instr['rdValue'] is not None else instr['Rd'], 9)

                if opclass == 3.6:
                    code += '1' if instr['iFlag'] else '0'

                code += OPCODES[instr['op']][0]
                if opclass == 3:
                    code += '1' if instr['aFlag'] else '0'
                    code += '1' if instr['iFlag'] else '0'
                    code += to_binary(instr['jFlags'], 3)

            # to_binary must have errored already, so don't need to worry about printing
            if len(code) > 16:
                return

            if len(code) > 0:
                code = hex(int(code, 2))[2:].rjust(4, "0")
                program += code+" "


    ##        print(instr)
                print(f"[{hex(addr)[2:].rjust(3, '0')}] {code}  {instr['labelDef'].rjust(labelLen+1, ' ')} {instr['op_asm'].ljust(opLen, ' ')}"+
                      f"\t\t{instr['argStr'].ljust(argLen, ' ')}"+
                      f"\t\t{instr.get('annot','').ljust(antLen, ' ')}"+
                      f"\t\t{instr['source']}")


            addr += 1

            previnstr = instr

        
    

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
            verb = "--verb" in sys.argv[2:]
            Thread(target=monitor_input).start()
            
            contents = None
            while True:
                sleep(.1)
                f.seek(0)
                newContents = f.read()
                
                if inp is not None or newContents != contents:
                    inp = None
                    contents = newContents

                    if (platform := sys.platform) == 'win32':
                        os.system("cls")
                    elif platform == 'darwin':
                        os.system("clear")
                    else:
                        exit('Unsupported Operating System `' + platform +'`')
                    run(mx:=macroEXP(contents, verb=verb))
        else:
            run(mx:=macroEXP(f.read()))
##            print(mx)
##            run(f.read())


#y=0x0084;x=bin(y)[2:].rjust(16,'0');print(x[0:4],x[4:8],x[8],x[9:16])
#y=0x03dd;x=bin(y)[2:].rjust(16,'0');print(x[0:9],x[9:11],x[11],x[12],x[13:16])
#for self