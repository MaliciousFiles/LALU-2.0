import sys
import pyperclip
from time import sleep
from threading import Thread
import os
import inspect
import traceback

#Minor Tweak


freeRegisters = 14

OPCODES = {
    'INFO':             ('Opcode' ,'Opclass','sym'),
    'nop':              ('0000000',-1,None),
    'add':              ('0000001',2,'+='),
    'sub':              ('0000010',2,'-='),
    'ld':               ('0000011',2,None),
    'mv':               ('0000100',2,'='),
    'st':               ('0000101',2,None),
    'smul':             ('0000110',2,'-*='),
    'umul':             ('0000111',2,'+*='),
    'psh':              ('0001000',1.5,None),
    'pop':              ('0001001',1.5,None),

    'bsl':              ('0001100',2,'<<='),
    'bsr':              ('0001101',2,'>>='),
    'brl':              ('0001110',2,'|<<|='),
    'brr':              ('0001111',2,'|>>|='),
    'and':              ('0010000',2,'&='),
    'or':               ('0010001',2,'|='),
    'xor':              ('0010010',2,'^='),
    'any':              ('0010011',2,'!!='),
    'call':             ('0010100',3.5,None),
    'ret':              ('0010101',-1,None),
    'lfm':              ('0010110',2,None),
    'usm':              ('0010111',1,None),
    'usmz':             ('0011000',1,None),
    
    'lfmz':             ('0011010',2,None),
    'hsb':              ('0011011',2,None),

    'prreg':            ('0100000',2.5,None),
    'prmem':            ('0100001',2.6,None),
    'prprg':            ('0100010',2.6,None),
    #'prext':            ('0100011',3.6),
    'prhdl':            ('0100100',3.6,None),
    'enpr':             ('0100101',3.6,None),
    'expr':             ('0100110',-1,None),
    'sar':              ('0100111',-1,None),
    'par':              ('0101000',-1,None),
    
    'exjmp':            ('0011110',-2,None),
    'jmp':              ('10'     ,3,None),
    
    'halt':             ('1111111',-1,None),
}

#Thx Stack Exchange (https://stackoverflow.com/questions/3056048/filename-and-line-number-of-python-script)
def __LINE__() -> int:
    return inspect.currentframe().f_back.f_lineno
def __CALL_LINE__() -> int:
    return inspect.currentframe().f_back.f_back.f_lineno

class CompileError(Exception):        #Just makes a custom Exception class so its own errors can be caught
    def __init__(self,message):
        super().__init__(message)

def errormsg(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CompileError as e:
            print(e)
    return inner

def KeyFromValue(dictionary, val):
    for key in dictionary:
        if dictionary[key]==val:
            return key
    return None

def PreScan(contents):
    statics=[]
    for linenum, line in enumerate(contents.split('\n')):
        line = [x for x in line.split() if x != None]
        if len(line)==1 and line[0][-1]==':':
            lbl = line[0][:-1]
            statics.append((lbl,linenum))
    return statics

@errormsg
def run(contents, verb = False):
    def AsmSrcMarker(func):
        nonlocal immexp, linenum
        def inner(*args, **kwargs):
            preImmExpLen = len(immexp)
            ret = func(*args, **kwargs)
            new = immexp[preImmExpLen:]
            for line in new:
                line['Src'] = line.get('Src', f'Line: {linenum+1}')
                line['Src'] = f'{func.__name__}::'+line['Src']

            return ret
        return inner
        
    def Error(msg):
        nonlocal linenum, line
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+' '.join(line)[:100]+'`'+'\nSource Line: '+str(linenum+1))

    def ErrorWithHighlight(msg, linesubsection):
        nonlocal linenum, line
        highlight = ' '.join([' '*len(seg) if idx != linesubsection else '^'*len(seg) for idx,seg in enumerate(line)])
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+' '.join(line)[:100]+'`'+'\n\t '+highlight+'\nSource Line: '+str(linenum+1))

    @AsmSrcMarker
    def DeclareVar(name, virtual = False):
        nonlocal Vars
        for reg in range(freeRegisters):
            if regdict.get(reg, None) == None:
                break
        else:
            MemPush(reg:=regUseOrder[0])
        regdict[reg] = name
        UseReg(reg)
        Vars.append(name)
        if not virtual:
            memloc = MemLoc(None, goto=False)
            memdict[memloc]=name

    @AsmSrcMarker
    def MemPush(reg):
        MemSync(reg)
        regdict[reg] = None

    @AsmSrcMarker
    def RegSync(reg):
        nonlocal immexp
        addr = MemLoc(regdict[reg])
        immexp.append( {'op': 'ld', 'Rd': addr, 'Rs': reg} )

    @AsmSrcMarker
    def UseVar(name):
        for reg in range(freeRegisters):
            if regdict.get(reg, None) == name:
                return reg
        else:
            MemPush(reg:=regUseOrder[0])
            regdict[reg]=name
            addr = MemLoc(name)
            UseReg(reg)
            immexp.append( {'op': 'ld', 'Rd': reg, 'Rs': addr} )
            return reg

    @AsmSrcMarker      
    def UseReg(reg):
        if reg in regUseOrder:
            regUseOrder.remove(reg)
        regUseOrder.append(reg)

    @AsmSrcMarker
    def TryNum(val):
        num = 0
        isNeg = val[0] == '-'
        if isNeg:
            val=val[1:]
        if len(val)==0:
            return None
        if val[0] == '0' and len(val) > 1:
            if val[1] == 'x':
                num = ParseInt(val[2:],16)
            elif val[1] == 'b':
                num = ParseInt(val[2:],2)
            elif val[1] not in '_0123456789':
                Error('Unknown base identifier: `'+val[1]+'`')
            else:
                num = ParseInt(val[2:],10)
        elif val[0] in '0123456789':
            num = ParseInt(val,10)
        else:
            return None
        if isNeg:
            num = (2**16-num)%2**16
        return num
                
    @AsmSrcMarker
    def ParseInt(val, base=10):
        num = 0
        for c in val:
            if c == '_':
                continue
            elif c.lower() in '0123456789abcde':
                digitval = '0123456789abcde'.index(c.lower())
                if digitval >= base:
                    Error('Integer Parse failure')
                num *= base
                num += digitval
        return num
            

    #Load Imm Extended
    @AsmSrcMarker
    def LDIEX(reg, val):
        nonlocal immexp
        chunks = []
        while val > 15:
            cnk = val % 16
            val //= 16
            chunks.append(cnk)

        immexp.append( {'op': 'mv', 'Rd': reg, 'Rs': val, 'Imm': True} )
        for cnk in chunks:
            immexp.append( {'op': 'bsl', 'Rd': reg, 'Rs': 4, 'Imm': True} )
            immexp.append( {'op': 'add', 'Rd': reg, 'Rs': cnk, 'Imm': True} )
                

    #Stk Ptr Set Extended
    @AsmSrcMarker
    def SPSE(val):
        nonlocal relstkptr
        if val > relstkptr:
            diff = val - relstkptr
            LDIEX(14, diff)
            immexp.append( {'op': 'add', 'Rd': 15, 'Rs': 14} )
        elif val == relstkptr:
            return
        else:
            diff = relstkptr - val
            LDIEX(14, diff)
            immexp.append( {'op': 'sub', 'Rd': 15, 'Rs': 14} )
        relstkptr = val

    #Offset Imm Extended
    @AsmSrcMarker
    def OFIEX(reg, val):
        nonlocal immexp, linenum
        if val > 0:
            immexp.append( {'op': 'add', 'Rd': reg, 'Rs': val, 'Imm': True} )
        elif val == 0:
            return
        else:
            immexp.append( {'op': 'sub', 'Rd': reg, 'Rs': -val, 'Imm': True} )

    @AsmSrcMarker
    def MemLoc(name, goto = True):
        nonlocal immexp, relstkptr
        if name in memdict.values():
            loc = [loc for loc in memdict if memdict[loc] == name][0]
            if goto:
                SPSE(loc)
            return loc
        else:
            off = 0
            while True:
                if memdict.get(relstkptr + off, None) == None:
                    if goto:
                        OFIEX(15, off)
                    relstkptr += off
                    memdict[relstkptr]=name
                    return relstkptr
                elif relstkptr - off >= 0 and memdict.get(relstkptr - off, None) == None:
                    if goto:
                        OFIEX(15, -off)
                    relstkptr -= off
                    memdict[relstkptr]=name
                    return relstkptr
                off += 1

    @AsmSrcMarker
    def SetState(tarstate, oldstate):
        tarreg, tarmem, tarptr = tarstate
        oldreg, oldmem, oldptr = oldstate

        queue = [(i, tarreg[i]) for i in enumerate(tarreg)]
        while queue != []:
            trn = [name for i,name in queue]
            cloc, cvar = trn[0]
            if cvar in oldreg.values():
                if cloc == (oloc:=KeyFromValue(oldreg, cvar)):
                    pass    #The registers are fine so no worries
                else:
                    #Vacate the current location
                    MemPush(cloc)
                    regdict[cloc]=cvar
                    immexp.append( {'op': 'mv', 'Rd': cloc, 'Rs': oloc} )
                    regdict[oloc]=None #Also go ahead and mark the old location as free
            else:
                MemPush(cloc)
                regdict[cloc]=cvar
                RegSync(cloc)
        SPSE(tarptr)
                    
    immexp = []
    memdict = {}
    regdict = {}
    regUseOrder = []
    relstkptr = 0
    Vars=[]

    staticIdents = PreScan(contents)
    sIN = [name for name,lnum in staticIdents]
    staticIdents = {name:lnum for name,lnum in staticIdents}
    states = {}

    opsyms = [sym for bits,opclass,sym in OPCODES.values()]
    for linenum, line in enumerate(contents.split('\n')):
        line = line.split()
        if linenum in staticIdents.values():
            lbl=line[0][:-1]
            immexp.append( {'op': 'lbl', 'val': lbl} )
            states[lbl] = (memdict,regdict,relstkptr)
        elif line != []:
            #Declarations
            if line[0] == 'decl':
                if line[1][0].lower() == 'r':
                    ErrorWithHighlight('Cannot declare variable that starts with `r`',1)
                elif line[1] in sIN:
                    ErrorWithHighlight(f'Identifier collides with static Identifier `{line[1]}` found at {staticIdents[line[1]]}',1)
                elif line[1] == 'virtual':
                    virtual = True
                    if line[2][0].lower() == 'r':
                        ErrorWithHighlight('Cannot declare variable that starts with `r`',2)
                    DeclareVar(line[2],True)
                else:
                    DeclareVar(line[1])

            #Inplace binary operations
            elif line[0] in Vars:
                if line[1] in opsyms and line[2] in Vars:
                    opname = list(OPCODES.keys())[opsyms.index(line[1])]
                    lhsreg = UseVar(line[0])
                    rhsreg = UseVar(line[2])
                    immexp.append( {'op': opname, 'Rd': lhsreg, 'Rs': rhsreg} )
                elif line[1] not in opsyms:
                    ErrorWithHighlight(f'Unknown symbol: `{line[1]}`',1)

                #Load and variations
                elif line[2][-2:]=='.*':
                    lhsreg = UseVar(line[0])
                    rhs = line[2][:-2]
                    if line[1] == '=':
                        if rhs in Vars:
                            rhsreg = UseVar(rhs)
                            immexp.append( {'op': 'ld', 'Rd': lhsreg, 'Rs': rhsreg} )
                        elif (rhsnum := TryNum(rhs)) != None:
                            LDIEX(lhsreg, rhsnum)
##                            immexp.append( {'op': 'ld', 'Rd': lhsreg, 'Rs': rhsnum, 'Imm': True} )
                        else:
                            ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier as address: `{rhs}`',2)
                    else:
                        ErrorWithHighlight(f'Binary operand must be `=` for memory write',1)
                #Address of
                elif line[2][-2:]=='.&':
                    opname = list(OPCODES.keys())[opsyms.index(line[1])]
                    lhsreg = UseVar(line[0])
                    rhs = line[2][:-2]
                    if rhs in Vars:
                        rhsnum = MemLoc(rhs, goto=False)
                        immexp.append( {'op': opname, 'Rd': lhsreg, 'Rs': rhsnum, 'Imm': True} )
                    else:
                        ErrorWithHighlight(f'Cannot take address of non adressable identifier: `{rhs}`',2)

                #Rhs is numeric
                elif line[2] not in Vars:
                    opname = list(OPCODES.keys())[opsyms.index(line[1])]
                    if (rhs := TryNum(line[2])) != None:
                        lhsreg = UseVar(line[0])
                        LDIEX(lhsreg, rhs)
##                        immexp.append( {'op': opname, 'Rd': lhsreg, 'Rs': rhs, 'Imm': True} )

                    #RHS intrinsic functions
                    elif line[2][0] == '@' and line[1]=='=':
                        lhsreg = UseVar(line[0])
                        line.insert(3, line[2].split('(')[1])
                        line.insert(3, '(')
                        line[2]=line[2].split('(')[0]
                        if line[-1][-1] == ')':
                            line[-1]=line[-1][:-1]
                        else:
                            ErrorWithHighlight(f'Expected `)` at end of: `{line[-1]}`', len(line)-1)
                        line.append(')')

                        #Pop
                        if line[2] == '@pop':
                            if line[4] == '':
                                immexp.append( {'op': 'pop', 'Rs': lhsreg} )
                            else:
                                ErrorWithHighlight(f'Expected `)` for function of arity 0: `{line[4]}`',4)
                            if line[5] != ')':
                                ErrorWithHighlight(f'Expected `)`, found: `{line[5]}`', 5)
                        else:
                            ErrorWithHighlight(f'Unknown Intrinsic Function: `{line[0]}`', 0)
                    else:
                        ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier: `{line[2]}`',2)
                else:
                    Error('Internal compiler error')

            #Store and variations
            elif line[0][-2:] == '.*':
                lhs = line[0][:-2]
                if lhs in Vars:
                    lhsreg = UseVar(lhs)
                    if line[1] == '=':
                        if line[2] in Vars:
                            rhsreg = UseVar(line[2])
                            immexp.append( {'op': 'st', 'Rd': rhsreg, 'Rs': lhsreg} )
                        elif (rhs := TryNum(line[2])) != None:
                            ErrorWithHighlight(f'Cannot use static integer as rhs of memory write: `{line[2]}`\nIf this is desired behavior, consider prefixing the numeral with `$` to make a temporary`',2)
                        elif (rhs := TryNum(line[2][1:])) != None and line[2][0]=='$':
                            LDIEX(14, rhs)
                            immexp.append( {'op': 'st', 'Rd': 14, 'Rs': lhsreg} )
                        else:
                            ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier: `{line[2]}`',2)
                    else:
                        ErrorWithHighlight(f'Binary operand must be `=` for memory write',1)
                elif (lhsnum := TryNum(lhs)) != None:
                    if line[1] == '=':
                        if line[2] in Vars:
                            rhsreg = UseVar(line[2])
                            immexp.append( {'op': 'st', 'Rd': rhsreg, 'Rs': lhsnum, 'Imm': True} )
                        elif (rhs := TryNum(line[2])) != None:
                            ErrorWithHighlight(f'Cannot use static integer as rhs of memory write: `{line[2]}`\nIf this is desired behavior, consider prefixing the numeral with `$` to make a temporary`',2)
                        elif (rhs := TryNum(line[2][1:])) != None and line[2][0]=='$':
                            LDIEX(14, rhs)
                            immexp.append( {'op': 'st', 'Rd': 14, 'Rs': lhsnum, 'Imm': True} )
                        else:
                            ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier: `{line[2]}`',2)
                    else:
                        ErrorWithHighlight(f'Binary operand must be `=` for memory write',1)
                else:
                    ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier as address: `{lhs}`',0)
                
            elif lhs := TryNum(line[0]):
                    ErrorWithHighlight(f'LHS of inplace operation cannot be static',0)

            #Function-like ASM intrinsics
            elif line[0][0]=='@':
                line.insert(1, line[0].split('(')[1])
                line.insert(1, '(')
                line[0]=line[0].split('(')[0]
                if line[-1][-1]==')':
                    line[-1]=line[-1][:-1]
                else:
                    ErrorWithHighlight(f'Expected `)` at end of: `{line[-1]}`', len(line)-1)
                line.append(')')

                #Push
                if line[0] == '@push':
                    if line[2] in Vars:
                        rhsreg = UseVar(line[2])
                        immexp.append( {'op': 'psh', 'Rs': rhsreg} )
                    elif line[2][:-1] in Vars and line[2][-1]==',':
                        ErrorWithHighlight(f'Cannot use continuation character `,` in function with arity 1: `{line[2]}`',2)
                    elif (rhs := TryNum(line[2])) != None:
                        immexp.append( {'op': 'psh', 'Rs': rhs, 'Imm': True} )
                    else:
                        ErrorWithHighlight(f'Usage of undeclared nonnumeric identifier: `{line[2]}`',2)
                    if line[3] != ')':
                        ErrorWithHighlight(f'Expected `)`, found: `{line[3]}`', 3)
                else:
                    ErrorWithHighlight(f'Unknown Intrinsic Function: `{line[0]}`', 0)
            elif line[0] == 'goto':
                if line[1] in sIN:
                    immexp.append( {'op': 'jmp', 'lbl': line[1]} )
                elif line[1] in Vars:
                    ErrorWithHighlight(f'Cannot goto variable identifier: `{line[1]}`, if you intend to go to the destination of this variable, please use @jmp(...)', 1)
                else:
                    ErrorWithHighlight(f'Unknown destination: `{line[1]}`', 1)
                if len(line)>2:
                    ErrorWithHighlight(f'Expected End Of Line, found: `{line[2]}`', 2)
                    
            else:
                ErrorWithHighlight('Line cannot be parsed, failed here', 0)

        for line in immexp:
            line['Src'] = line.get('Src', f'Line: {linenum+1}')
    print('\n'.join([str(x) for x in immexp]))

inp = None

def monitor_input():
    global inp
    
    while True:
        inp = input().strip()
        if inp == "q":
            os._exit(1)

fName = sys.argv[1] if len(sys.argv) > 1 else input("Program File: ")
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
                    try:
                        run(contents, verb=verb)
                    except Exception as e:
                        print(f'Unexpected assembler crash\n')
                        print(e)
                        print(traceback.format_exc())
        else:
            run(f.read())
