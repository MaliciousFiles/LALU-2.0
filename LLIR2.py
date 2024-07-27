import sys
import pyperclip
from time import sleep
from threading import Thread
import os
import inspect
import traceback


freeRegisters = 14
stkPtr = 15
intReg = 14


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


    ###################################################################################
    #  * * * * * * * * * * * * * * *                   * * * * * * * * * * * * * * *  #
    # * * * * * * * * * * * * * * * * State Code Here * * * * * * * * * * * * * * * * #
    #  * * * * * * * * * * * * * * *                   * * * * * * * * * * * * * * *  #
    ###################################################################################

def Error(msg):
    raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')')

class State():
    def __init__(self):
        self.regs = [None for i in range(freeRegisters)]
        self.mem = {}
        self.statLoc = {}
        self.tempLoc = {}
        self.relStkPtr = 0
        self.relTopStk = 0
        self.regUseOrder = [i for i in range(freeRegisters)]
        self.numRegsUsed = 0
        self.vIdents = []
        self.sIdents = []
        self.finals = []

    def M_DeclVar(self, tkn, virtual):
        name = tkn.val
        if name in self.vIdents:
            tkn.Error(f'Redeclaration of variable `{name}`')
        self.vIdents.append(name)
        for i in range(freeRegisters):
            if self.regs[i] == None:
                self.regs[i] = name
                self.numRegsUsed = max(i, self.numRegsUsed)
                break
        else:
            reg = self.M_AquireReg()
        addr = self.AquireMem(1, name)
        if virtual:
            self.tempLoc[name] = addr
        else:
            self.statLoc[name] = addr

    def M_AquireReg(self):
        regIdx = self.regUseOrder[0]
        var = self.regs[regIdx]
        self.M_MemPushVar(var)
        self.regs[redIdx] = None
        return regIdx

    def AquireMem(self, width, var):
        off = 0
        while True:
            addr = self.relStkPtr + off
            if self.I_MemIsFree(addr, width):
                break

            addr = self.relStkPtr - off
            if self.I_MemIsFree(addr, width):
                break
            off += 1
        if addr + width > self.relTopStk:
            self.relTopStk = addr + width
        for i in range(width):
            self.mem[addr+i] = var
        return addr

    def I_MemIsFree(self, addr, width):
        if addr < 0:
            return False
        for i in range(width):
            if self.mem.get(addr+i, None) != None:
                return False
        return True

    def M_MemPushVar(self, var):
        regLoc = self.I_RegLoc(var)
        self.M_StkPointTo(var)
        self.M_OpRegReg('st', stkPtr, regLoc)    # *stkPtr = regVal

    def M_StkPointTo(self, var):
        relAddr = self.I_MemLoc(var)
        self.M_SetStkPtr(relAddr)

    def M_SetStkPtr(self, addr):
        offset = addr - self.relStkPtr
        if offset > 0:
            self.M_OpRegImm('add', stkPtr, offset)
        elif offset < 0:
            self.M_OpRegImm('sub', stkPtr, -offset)
        self.relStkPtr = addr

    def M_OpRegReg(self, op, rd, rs):
        global immexp
        immexp.append( {'op': op, 'Rd': rd, 'Rs': rs} )

    def M_OpRegImm(self, op, rd, imm):
        global immexp

        if 0 <= imm < 16:
            immexp.append( {'op': op, 'Rd': rd, 'Rs': imm, 'Imm': True} )
        elif 16 <= imm < 2**16 and op != 'mv':
            self.M_LoadImm(intReg, imm)
            immexp.append( {'op': op, 'Rd': rd, 'Rs': intReg} ) #Load from the intermediate register
        elif 16 <= imm < 2**16 and op == 'mv':
            self.M_LoadImm(rd, imm)     #Special case where performing a move afterwards can be avoided by just loading in place.
        else:
            Error('Immediate supplied is not encodeable')

    def M_LoadImm(self, reg, val):
        global immexp
        chunks = []
        while val > 15:
            cnk = val % 16
            val //= 16
            chunks.append(cnk)

        immexp.append( {'op': 'mv', 'Rd': reg, 'Rs': val, 'Imm': True} )
        for cnk in chunks:
            immexp.append( {'op': 'bsl', 'Rd': reg, 'Rs': 4, 'Imm': True} )
            immexp.append( {'op': 'add', 'Rd': reg, 'Rs': cnk, 'Imm': True} )

    def I_RegLoc(self, var):
        for i in range(self.numRegsUsed):
            if self.regs[i] == var:
                return i
        else:
            print('Register Dump:')
            print(f'{self.regs=}')
            Error(f'Could not find variable `{var}` in registers')

    def I_MemLoc(self, var):
        if var in self.statLoc:
            return statLoc[var]
        elif var in self.tempLoc:
            return tempLoc[var]
        elif var in self.mem.values():
            print('Memory Dump:')
            print(f'{self.mem=}')
            print('Static Location Dump:')
            print(f'{self.statLoc=}')
            print('Temporary Location Dump:')
            print(f'{self.tempLoc=}')
            Error(f'Internal desync error. Compilation terminated as correctness can not be guarenteed')
        else:
            print('Memory Dump:')
            print(f'{self.mem=}')
            Error(f'Could not find variable `{var}` in memory')

def TryNum(tkn, val):
    num = 0
    isNeg = val[0] == '-'
    if isNeg:
        val=val[1:]
    if len(val)==0:
        return None
    if val[0] == '0' and len(val) > 1:
        if val[1] == 'x':
            num = ParseInt(tkn, val[2:],16)
        elif val[1] == 'b':
            num = ParseInt(tkn, val[2:],2)
        elif val[1] not in '_0123456789':
            tkn.Error('Unknown base identifier: `'+val[1]+'`')
        else:
            num = ParseInt(tkn, val[2:],10)
    elif val[0] in '0123456789':
        num = ParseInt(tkn, val,10)
    else:
        return None
    if isNeg:
        num = (2**16-num)%2**16
    return num

def ParseInt(tkn, val, base=10):
    num = 0
    for c in val:
        if c == '_':
            continue
        elif c.lower() in '0123456789abcdef':
            digitval = '0123456789abcdef'.index(c.lower())
            if digitval >= base:
                tkn.Error('Integer Parse failure')
            num *= base
            num += digitval
    return num


def errormsg(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CompileError as e:
            print(e)
    return inner

@errormsg
def Compile(contents, verb = False):
    class TknList():
        def __init__(self, line, vIdents, sIdents, uFuncs, lbls):
            self.tkns = []
            self.next = 0

            if '#' not in line:
                line += '#'
            line, self.comment = line.split('#',maxsplit=1)
            line += " " #This forces a terminal character and also forces a comment character, meaning we dont need special cases if they dont happen

            buff = ""
            prevWS = True   #Just assume we start with white space to discard initial indentation, simplifies errors a little
            for i,c in enumerate(line):
                if c.isspace():
                    if buff != "":
                        self.tkns.append(Token(buff, len(self.tkns), self))
                    if not prevWS:
                        self.tkns.append(Token(' ', len(self.tkns), self))
                    buff = ""
                    prevWS = True
                elif c in '(){},':
                    if buff != "":
                        self.tkns.append(Token(buff, len(self.tkns), self))
                    self.tkns.append(Token(c, len(self.tkns), self))
                    buff = ""
                    prevWS = False
                else:
                    buff += c
                    prevWS = False
            for tkn in self.tkns:
                tkn.Classify(vIdents, sIdents, uFuncs, lbls)
            self.tkns=self.tkns[:-1]
        def pop(self):
            rtype = 'ws'
            while rtype == 'ws':
                ret = self.rawpop()
                rtype = ret.type
            return ret
                
        def rawpop(self):
            if self.next == len(self.tkns):
                if len(self.tkns) == 0:
                    self.tkns.append(Token(' ', 0, self))
                    self.tkns[-1].Error('Expected another token, but got no line')
                self.tkns[-1].Error('Expected another token, but got end of line')
            ret = self.tkns[self.next]
            self.next += 1
            return ret

        def AssertEmpty(self):
            if self.CanPop():
                self.tkns[self.next].Error('Expected EOL, got: ')

        def CanPop(self):
            return self.next != len(self.tkns)
            
    class Token():
        def __init__(self, txt, idx, parent):
            self.raw = txt
            self.parent = parent
            self.idx = idx
            self.type = 'Unknown'
            self.isPtr = False

        def Error(self, msg):
            ErrorWithHighlight(msg, self.parent, self.idx)

        def Classify(self, vIdents, sIdents, uFuncs, lbls):
            self.val = self.raw
            
            if self.val[-2:] == '.*':
                self.val = self.val[:-2]
                self.isPtr = True
            
            if self.raw in vIdents:
                self.type = 'v-ident'
            elif self.raw in sIdents:
                self.type = 's-ident'
            elif self.raw in uFuncs:
                self.type = 'u-func'
            elif self.raw in lbls:
                self.type = 'lbl'
            elif self.raw[0] == '@':
                self.type = 'i-func'
                self.val = self.val[1:]
            elif self.raw[-2:] == '.&':
                self.type = 'addr'
                self.val = self.val[:-2]
            elif self.raw in '(){}':
                self.type = 'sym-lit'
            elif self.raw == ' ':
                self.type = 'ws'
            elif num := TryNum(self, self.raw):
                self.type = 'num'
            else:
                self.type = 'u-ident'
            
        
    def AsmSrcMarker(func):
        nonlocal immexp, linenum
        def inner(*args, **kwargs):
            preImmExpLen = len(immexp)
            ret = func(*args, **kwargs)
            new = immexp[preImmExpLen:]
            for line in new:
                line['rSrc'] = line.get('rSrc',linenum)
                line['Src'] = line.get('Src', f'Line: {linenum+1}')
                line['Src'] = f'{func.__name__}::'+line['Src']
            return ret
        return inner
        
    def NoHintError(msg):
        nonlocal linenum, line
        fline = ''.join(x.raw for x in line.tkns)
        if line.comment != '':
            fline += ' #'
            fline += line.comment
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+fline+'`'+'\nSource Line: '+str(linenum+1))

    def ErrorWithHighlight(msg, line, lineidx):
        nonlocal linenum
        fline = ''.join(x.raw for x in line.tkns)
        if line.comment != '':
            fline += ' #'
            fline += line.comment
        highlight = ''.join([('^' if idx == lineidx else ' ')*len(seg.raw) for idx,seg in enumerate(line.tkns)])
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+fline+'`'+'\n\t '+highlight+'\nSource Line: '+str(linenum+1))

    def ParseDecl(line):
        ident = line.pop()
        if ident.raw == 'virtual':
            ident = line.pop()
            if ident.type == 'u-ident':
                cstate.M_DeclVar(ident, True)
            elif ident.type in ["u-func", "lbl", "v-ident", "s-ident"]:
                ident.Error(f'Identifier collides with prexisting name, results in type: `{ident.type}`')
            else:
                ident.Error(f'Expected valid identifier type, found: `{ident.type}`')
        else:
            if ident.type == 'u-ident':
                cstate.M_DeclVar(ident, False)
            elif ident.type in ["u-func", "lbl", "v-ident", "s-ident"]:
                ident.Error(f'Identifier collides with prexisting name, results in type: `{ident.type}`')
            else:
                ident.Error(f'Expected valid identifier type, found: `{ident.type}`')

    def Parse(line):
        if not line.CanPop():
            return
        tkn = line.pop()

        if tkn.raw == 'decl':
            ParseDecl(line)
        elif tkn.isPtr == False and tkn.type == 'v-ident':
            pass
        else:
            tkn.Error('Unable to detirmine type of line based on initial token')

        line.AssertEmpty()


    ####################################################################################
    #  * * * * * * * * * * * * * * *                    * * * * * * * * * * * * * * *  #
    # * * * * * * * * * * * * * * * * Code Starts Here * * * * * * * * * * * * * * * * #
    #  * * * * * * * * * * * * * * *                    * * * * * * * * * * * * * * *  #
    ####################################################################################

    cstate = State()
    lbls = []
    funcs = []

    immexp = []
    for linenum, line in enumerate(contents.split('\n')):
        line = TknList(line, cstate.vIdents, cstate.sIdents, funcs, lbls)

        try:
            Parse(line)
        except CompileError as e:
            print(str(e))
            NoHintError('Parsing Failure')
        
        print('`'+'`'.join(x.raw for x in line.tkns)+'`')

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
                        Compile(contents, verb=verb)
                    except Exception as e:
                        print(f'Unexpected assembler crash\n')
                        print(e)
                        print(traceback.format_exc())
        else:
            Compile(f.read())
