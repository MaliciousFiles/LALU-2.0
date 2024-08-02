import sys
import pyperclip
from time import sleep
from threading import Thread
import os
import inspect
import traceback
from copy import deepcopy as copy


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

CMPCODES = {
    #Name
    'INFO':             ('Opcode' ,'sym'),
    'ugt':              ('0000', '+>'),
    'uge':              ('0001', '+>='),
    'ult':              ('0010', '+<'),
    'ule':              ('0011', '+<='),
    'sgt':              ('0100', '->'),
    'sge':              ('0101', '->='),
    'slt':              ('0110', '-<'),
    'sle':              ('0111', '-<='),
    'eq':               ('1000', '=='),
    'ne':               ('1001', '!='),
}

#Thx Stack Exchange (https://stackoverflow.com/questions/3056048/filename-and-line-number-of-python-script)
def __LINE__() -> int:
    return inspect.currentframe().f_back.f_lineno
def __CALL_LINE__() -> int:
    return inspect.currentframe().f_back.f_back.f_back.f_lineno
def __OUTER_FUNC__() -> str:
    return inspect.currentframe().f_back.f_back.f_code.co_name

class CompileError(Exception):        #Just makes a custom Exception class so its own errors can be caught
    def __init__(self,message):
        super().__init__(message)

class TokenlessCompileError(Exception):
    def __init__(self,message):
        super().__init__(message)

def AsmSrcMarker(func):
    global immexp, linenum
    def MarkedInner(*args, **kwargs):
        preImmExpLen = len(immexp)
        ret = func(*args, **kwargs)
        new = immexp[preImmExpLen:]
        for line in new:
            line['rSrc'] = line.get('rSrc',linenum)
            line['Src'] = line.get('Src', f'Line: {linenum+1}')
            line['Src'] = f'{func.__name__}::'+line['Src']
        return ret
    return MarkedInner

def DontTakeNone(func):
    def NonelessInner(*args, **kwargs):
        if None in args:
            nonearg = [i for i,arg in enumerate(args) if arg == None][0]
            fname = __OUTER_FUNC__()
            raise TokenlessCompileError(f'{fname} does not take None as a valid arguement, arg_{nonearg} is None, called from line: {__CALL_LINE__()}')
        return func(*args, **kwargs)
    return NonelessInner

    ###################################################################################
    #  * * * * * * * * * * * * * * *                   * * * * * * * * * * * * * * *  #
    # * * * * * * * * * * * * * * * * State Code Here * * * * * * * * * * * * * * * * #
    #  * * * * * * * * * * * * * * *                   * * * * * * * * * * * * * * *  #
    ###################################################################################

def Error(msg):
    raise TokenlessCompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')')

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

    def __hash__(self):
        full = [self.regs, self.mem, self.statLoc, self.tempLoc, self.relStkPtr, self.relTopStk, self.regUseOrder, self.numRegsUsed, self.vIdents, self.sIdents, self.finals]
        parts = [repr(hash(repr(x))) for x in full]
        return hash(''.join(parts))

    @AsmSrcMarker
    @DontTakeNone
    def M_DeclVar(self, tkn, virtual):
        name = tkn.val
        if name in self.vIdents:
            tkn.Error(f'Redeclaration of variable `{name}`')
        self.vIdents.append(name)
        for i in range(freeRegisters):
            if self.regs[i] == None:
                self.regs[i] = name
                self.numRegsUsed = max(1+i, self.numRegsUsed)
                break
        else:
            reg = self.M_AquireReg()
            self.regs[reg] = name
        if virtual:
            self.tempLoc[name] = None
        else:
            addr = self.AquireMem(1, name)
            self.statLoc[name] = addr

    @DontTakeNone
    def UseReg(self, reg):
        if reg in self.regUseOrder:
            self.regUseOrder.remove(reg)
        self.regUseOrder.append(reg)

    @DontTakeNone
    @AsmSrcMarker
    def M_AquireReg(self):
        regIdx = self.regUseOrder[0]
        var = self.regs[regIdx]
        self.M_MemPushVar(var)
        self.regs[regIdx] = None
        return regIdx

    @DontTakeNone
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

    @DontTakeNone
    def I_MemIsFree(self, addr, width):
        if addr < 0:
            return False
        for i in range(width):
            if self.mem.get(addr+i, None) != None:
                return False
        return True

    @DontTakeNone
    @AsmSrcMarker
    def M_MemPushVar(self, var):
        regLoc = self.I_RegLoc(var)
        self.M_StkPointTo(var)
        self.M_OpRegReg('st', regLoc, stkPtr)    # *stkPtr = regVal

    @DontTakeNone
    @AsmSrcMarker
    def M_MemSyncVar(self, var):
        if var in self.regs:
            self.M_MemPushVar(var)
        elif var not in self.vIdents:
            Error(f'Cannot memsync variable `{var}`, which is not a variable identifier in this scope')

    @DontTakeNone
    @AsmSrcMarker
    def M_MemPullVar(self, var):
        regLoc = self.I_RegLoc(var)
        self.M_StkPointTo(var)
        self.M_OpRegReg('ld', regLoc, stkPtr)    # *stkPtr = regVal
        if var in self.tempLoc:
            self.tempLoc[var] = None

    @DontTakeNone
    @AsmSrcMarker
    def M_RegSyncVar(self, var):
        if var in self.regs:
            memLoc = self.I_MemLoc(var)
            if memLoc == None:
                return
            self.M_MemPullVar(var)
        elif var not in self.vIdents:
            Error(f'Cannot regsync variable `{var}`, which is not a variable identifier in this scope')

    @DontTakeNone
    @AsmSrcMarker
    def M_StkPointTo(self, var):
        relAddr = self.MemLoc(var)
        self.M_SetStkPtr(relAddr)

    @DontTakeNone
    @AsmSrcMarker
    def M_SetStkPtr(self, addr):
        offset = addr - self.relStkPtr
        if offset > 0:
            self.M_OpRegImm('add', stkPtr, offset)
        elif offset < 0:
            self.M_OpRegImm('sub', stkPtr, -offset)
        self.relStkPtr = addr

    @DontTakeNone
    @AsmSrcMarker
    def M_OpRegReg(self, op, rd, rs):
        global immexp
        immexp.append( {'op': op, 'Rd': rd, 'Rs': rs} )

    @DontTakeNone
    @AsmSrcMarker
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

    @DontTakeNone
    @AsmSrcMarker
    def M_OpReg(self, op, rs):
        global immexp
        immexp.append( {'op': op, 'Rs': rs} )

    @DontTakeNone
    @AsmSrcMarker
    def M_OpImm(self, op, imm):
        global immexp

        if 0 <= imm < 16:
            immexp.append( {'op': op, 'Rs': imm, 'Imm': True} )
        elif 16 <= imm < 2**16 and op != 'mv':
            self.M_LoadImm(intReg, imm)
            immexp.append( {'op': op, 'Rs': intReg} ) #Load from the intermediate register
        else:
            Error('Immediate supplied is not encodeable')

    @DontTakeNone
    @AsmSrcMarker
    def M_OpLit(self, op, lit):
        global immexp

        immexp.append( {'op': op, 'Rs': lit} )

    @DontTakeNone
    @AsmSrcMarker
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
            if cnk != 0:
                immexp.append( {'op': 'add', 'Rd': reg, 'Rs': cnk, 'Imm': True} )

    @DontTakeNone
    def I_RegLoc(self, var):
        for i in range(self.numRegsUsed):
            if self.regs[i] == var:
                return i
        else:
            print('Register Dump:')
            print(f'{self.regs=}')
            Error(f'Could not find variable `{var}` in registers')

    @DontTakeNone
    @AsmSrcMarker
    def M_RegLoc(self, var):
        for i in range(self.numRegsUsed):
            if self.regs[i] == var:
                self.UseReg(i)
                return i
        else:
##            print(f'{self.regs=}')
            regloc = self.M_AquireReg()
##            print(f'{self.regs=}')
            self.regs[regloc] = var
            self.M_RegSyncVar(var)
            self.UseReg(regloc)
            return regloc
            
    @DontTakeNone
    def I_MemLoc(self, var):
        if var in self.statLoc:
            return self.statLoc[var]
        elif var in self.tempLoc:
            return self.tempLoc[var]
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

    @DontTakeNone
    def MemLoc(self, var):
        if (ret := self.I_MemLoc(var)) == None:
            addr = self.AquireMem(1, var)
            self.tempLoc[var] = addr
            return addr
        else:
            return ret

    @DontTakeNone
    @AsmSrcMarker
    def M_PushStateChange(self, oldstatename, tarstatename):
        global immexp
        immexp.append( {'proc': 'stateChange', 'from': oldstatename, 'to': tarstatename} )

    @DontTakeNone
    @AsmSrcMarker
    def M_UCJmp(self, destLbl):
        global immexp
        immexp.append ({'op': 'jmp', 'to': destLbl} )

    @DontTakeNone
    @AsmSrcMarker
    def M_PrepCmpJmp(self, lReg, rReg, cmp):
        global immexp
        self.M_OpRegReg('mv', intReg, lReg)
        self.M_OpRegReg('sub', intReg, rReg)
        if cmp not in CMPCODES:
            Error(f'This should not occur, recieved CmpCode: `{cmp}`')
        cmpbin, _ = CMPCODES[cmp]
        self.M_OpLit('usm', cmp)

    @DontTakeNone
    @AsmSrcMarker
    def M_CmpJmp(self, destLbl):
        global immexp
        immexp.append ({'op': 'cmpjmp', 'to': destLbl} )

    @DontTakeNone
    @AsmSrcMarker
    def M_PushLbl(self, lbl):
        global immexp
        immexp.append ({'lbl': lbl} )

        
global NoneState
NoneState = copy(State())

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
    global immexp, linenum
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
                self.tkns.append(Token(' ', len(self.tkns), self))
                self.tkns[-1].Error('Expected another token, but got end of line')
            ret = self.tkns[self.next]
            self.next += 1
            return ret

        def AssertEmpty(self):
            if self.CanPop():
                self.tkns[self.next].Error('Expected EOL, got: ')

        def CanPop(self):
            return self.next != len(self.tkns)

        def Reset(self):
            self.next = 0
            
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
            
            if self.val in vIdents:
                self.type = 'v-ident'
            elif self.val in sIdents:
                self.type = 's-ident'
            elif self.val in uFuncs:
                self.type = 'u-func'
            elif self.val in lbls:
                self.type = 'lbl'
            elif self.val[:-1] in lbls and self.val[-1]==':':
                self.type = 'lbl'
                self.val = self.val[:-1]
            elif self.val[0] == '@':
                self.type = 'i-func'
                self.val = self.val[1:]
            elif self.val[-2:] == '.&':
                self.type = 'addr'
                self.val = self.val[:-2]
            elif self.val in '(){}':
                self.type = 'sym-lit'
            elif self.val == ' ':
                self.type = 'ws'
            elif (num := TryNum(self, self.val)) != None:
                self.type = 'num'
                self.val = num
            else:
                self.type = 'u-ident'
        
    def NoHintError(msg):
        nonlocal line
        fline = ''.join(x.raw for x in line.tkns)
        if line.comment != '':
            fline += ' #'
            fline += line.comment
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+fline+'`'+'\nSource Line: '+str(linenum+1))

    def ErrorWithHighlight(msg, line, lineidx):
        fline = ''.join(x.raw for x in line.tkns)
        if line.comment != '':
            fline += ' #'
            fline += line.comment
        highlight = ''.join([('^' if idx == lineidx else ' ')*len(seg.raw) for idx,seg in enumerate(line.tkns)])
        raise CompileError('ERROR: '+msg+' (@ Py: '+str(__CALL_LINE__())+')'+'\n\t`'+fline+'`'+'\n\t '+highlight+'\nSource Line: '+str(linenum+1))

    @AsmSrcMarker
    def ParseDecl(line):
        ident = line.pop()
        if ident.raw == 'virtual':
            ident = line.pop()
            if ident.type == 'u-ident':
                if ident.isPtr:
                    ident.Error(f'Cannot declare variable with the suffix `.*`: `{ident.type}`')
                cstate.M_DeclVar(ident, True)
            elif ident.type in ["u-func", "lbl", "v-ident", "s-ident"]:
                ident.Error(f'Identifier collides with prexisting name, results in type: `{ident.type}`')
            else:
                ident.Error(f'Expected valid identifier type, found: `{ident.type}`')
        else:
            if ident.type == 'u-ident':
                if ident.isPtr:
                    ident.Error(f'Cannot declare variable with the suffix `.*`: `{ident.type}`')
                cstate.M_DeclVar(ident, False)
            elif ident.type in ["u-func", "lbl", "v-ident", "s-ident"]:
                ident.Error(f'Identifier collides with prexisting name, results in type: `{ident.type}`')
            else:
                ident.Error(f'Expected valid identifier type, found: `{ident.type}`')


    #There are four valid types for rhs in many cases, which may be registers, immediates, addresses, and labels. These last two needs special processing and act like registers
    @AsmSrcMarker
    def ParseBinaryOp(line):
        line.Reset()
        lhs = line.pop()
        op = line.pop()
        rhs = line.pop()
        line.AssertEmpty()

        if lhs.isPtr and rhs.isPtr:
            op.Error('Either lhs or rhs may be pointer destinations, but not both')
        elif lhs.isPtr and not rhs.isPtr:   #Store operation *Rs = Rd,      Rs(i) = lhs, Rd = rhs
            if op.raw != '=':
                op.Error('Cannot perform an inplace binary operation other than assignment with pointer types')
            if lhs.type == 'v-ident':
                lhsreg = cstate.M_RegLoc(lhs.val)
                if rhs.type == 'v-ident':
                    rhsreg = cstate.M_RegLoc(rhs.val)
                    cstate.M_OpRegReg('st', rhsreg, lhsreg)
                elif rhs.type == 'num':
                    rhsnum = rhs.val
                    cstate.M_LoadImm(intReg, rhsnum)
                    cstate.M_OpRegImm('st', intReg, lhsreg)
                else:
                    lhs.Error('Path not implemented: Var.* = Addr/Lbl')
                
            elif lhs.type == 'num':
                lhsnum = lhs.val
                if rhs.type == 'v-ident':
                    rhsreg = cstate.M_RegLoc(rhs.val)
                    cstate.M_OpRegReg('st', rhsreg, lhsnum)
                elif rhs.type == 'num':
                    rhsnum = rhs.val
                    cstate.M_LoadImm(intReg, rhsnum)
                    cstate.M_OpRegImm('st', intReg, lhsnum)
                else:
                    lhs.Error('Path not implemented: Imm.* = Addr/Lbl')
            else:
                lhs.Error(f'Storing to the location of type: `{lhs.type}`, is not implemented behavior, please use a temporary variable if this is infact desire behavior')
        elif not lhs.isPtr and rhs.isPtr:   #Load operation Rd = *Rs,      Rs(i) = rhs, Rd = lhs
            if op.raw != '=':
                op.Error('Cannot perform an inplace binary operation other than assignment with pointer types')
            if lhs.type == 'v-ident':
                lhsreg = cstate.M_RegLoc(lhs.val)
                if rhs.type == 'v-ident':
                    rhsreg = cstate.M_RegLoc(rhs.val)
                    cstate.M_OpRegReg('ld', lhsreg, rhsreg)
                elif rhs.type == 'num':
                    rhsnum = rhs.val
                    cstate.M_OpRegImm('ld', lhsreg, rhsnum)
                else:
                    rhs.Error('Loading from the location of type: `{rhs.type}`, is not implemented behavior, please use a temporary variable if this is infact desire behavior')
                
            elif lhs.type == 'num':
                lhs.Error('Cannot assign to constant lhs')
            else:
                lhs.Error(f'Storing to the location of type: `{lhs.type}`, is not implemented behavior')
        elif not lhs.isPtr and not rhs.isPtr:   #Generic Operation, Rd op= Rs   Rs(i) = rhs, Rd = lhs
            if lhs.type == 'v-ident':
                lhsreg = cstate.M_RegLoc(lhs.val)
                opname = list(OPCODES.keys())[opsyms.index(op.raw)]
                if rhs.type == 'v-ident':
                    rhsreg = cstate.M_RegLoc(rhs.val)
                    cstate.M_OpRegReg(opname, lhsreg, rhsreg)
                elif rhs.type == 'num':
                    rhsnum = rhs.val
                    cstate.M_OpRegImm(opname, lhsreg, rhsnum)
                elif op.raw == '=':
                    if rhs.type == 'addr' and rhs.val in cstate.statLoc:
                        cstate.M_StkPointTo(rhs.val)
                        cstate.M_OpRegReg(opname, lhsreg, stkPtr)
                    elif rhs.type == 'addr' and rhs.val in cstate.tempLoc:
                        rhs.Error(f'Cannot take address of virtual variable `{rhs.val}`')
                    elif rhs.type == 'addr' and rhs.val in cstate.vIdents:
                        rhs.Error('This error should not occur, internal memory desync')
                    else:
                        rhs.Error(f'Loading from the location of type: `{rhs.type}`, is not implemented behavior, please use a temporary variable if this is infact desire behavior')
                else:
                    rhs.Error(f'Inplace operations with an rhs of type: `{rhs.type}`, is not implemented behavior, please use a temporary variable if this is infact desire behavior')
                
            elif lhs.type == 'num':
                lhs.Error('Cannot assign to constant lhs')
            else:
                lhs.Error(f'Storing into type: `{lhs.type}`, is not implemented behavior')
        else:
            op.Error('This error should not occur, something has gone very wrong')
        
    def ParseRetIFunc(line):
        line.Reset()
        lhs = line.pop()
        assg = line.pop()
        ifunc = line.pop()
        lparen = line.pop()
        rparen = line.pop()

        if assg.raw != '=':
            assg.Error('Expected `=` for returning intrinsic function calls')
        if lparen.raw != '(':
            lparen.Error('Expected `(` for returning intrinsic function calls')
        if rparen.raw != ')':
            rparen.Error('Expected `)` for function of arity 0')
        
        line.AssertEmpty()

        if lhs.isPtr or lhs.type != 'v-ident':
            lhs.Error('Return destination must be a plain variable identifier')

        lhsreg = cstate.M_RegLoc(lhs.val)
        if ifunc.val == 'pop':
            cstate.M_OpReg('pop',lhsreg)
        elif ifunc.val == 'ldkey':
            cstate.M_OpReg('ldkey',lhsreg)
        else:
            ifunc.Error(f'Unknown intrinsic function `{ifunc.val}`')

    def ParseVoidIFunc(line):
        line.Reset()
        ifunc = line.pop()
        lparen = line.pop()
        arg = line.pop()
        rparen = line.pop()

        if lparen.raw != '(':
            lparen.Error('Expected `(` for returning intrinsic function calls')
        if rparen.raw != ')':
            rparen.Error('Expected `)` for function of arity 1')
        
        line.AssertEmpty()

        if arg.isPtr:
            arg.Error('Return destination must be a plain variable identifier, number, label, or address')
        
        if arg.type in ['v-ident', 'addr']:
            if arg.val not in cstate.vIdents:
                arg.Error(f'Usage of undeclared variable `{arg.val}`')
            if arg.type == 'v-ident':
                argReg = cstate.M_RegLoc(arg.val)
            else:
                if arg.val not in cstate.statLoc:
                    arg.Error(f'Cannot take address of virtual variable `{arg.val}`')
                cstate.M_StkPointTo(arg.val)
                argReg = stkPtr
            if ifunc.val == 'push':
                cstate.M_OpReg('psh',argReg)
            elif ifunc.val == 'stkey':
                cstate.M_OpReg('stkey',argReg)
            else:
                ifunc.Error(f'Unknown intrinsic function `{ifunc.val}`')
        elif arg.type == 'num':
            if ifunc.val == 'push':
                cstate.M_OpImm('psh',arg.val)
            elif ifunc.val == 'stkey':
                cstate.M_OpImm('stkey',arg.val)
            else:
                ifunc.Error(f'Unknown intrinsic function `{ifunc.val}`')
        elif arg.type == 'lbl':
            arg.Error('Unimplemented Path: @IFunc(lbl)')
        else:
            arg.Error(f'Invalid arguement type: `{arg.type}`')

    def ParseCmpGoto(line):
        line.Reset()
        commonkword = line.pop()
        cmpkword = line.pop()
        lhs = line.pop()
        cmp = line.pop()
        rhs = line.pop()
        gotokword = line.pop()
        lbl = line.pop()

        line.AssertEmpty()

        if lhs.type != 'v-ident':
            lhs.Error(f'Left hand side of the comparison must be of variable type, not `{lhs.type}`')
        if lhs.isPtr:
            lhs.Error(f'Left hand side of the comparison cannot be a ptr type')
        if rhs.type != 'v-ident':
            rhs.Error(f'Right hand side of the comparison must be of variable type, not `{rhs.type}`')
        if rhs.isPtr:
            lhs.Error(f'Right hand side of the comparison cannot be a ptr type')

        sOps = ['>','<','>=','<=']  #Sign marked comparions
        uOps = ['!=', '==']         #Unsigned comparisons

        if cmp.type != 'u-ident':
            cmp.Error(f'Comparions cannot be of type `{cmp.type}`')
        if cmp.isPtr:
            cmp.Error(f'Comparions cannot be pointed')

        if cmp.raw[0] in '+-':  #Sign marked comparison
            if cmp.raw[1:] in sOps:
                condCode = {'+':'u', '-':'s'}[cmp.raw[0]] + {'>':'gt', '<':'lt', '>=':'ge', '<=':'le'}[cmp.raw[1:]]
            elif cmp.raw[1:] in uOps:
                cmp.Error(f'Equality tests do not need sign marking')
            else:
                cmp.Error(f'Unknown sign marked comparison operator: `{cmp.raw[1:]}`')
        else:  #No sign marked comparison
            if cmp.raw in uOps:
                condCode = {'!=':'ne', '==':'eq'}[cmp.raw]
            elif cmp.raw in sOps:
                cmp.Error(f'Inequalities require sign marking, please prefix with `+` for unsigned and `-` for signed')
            else:
                cmp.Error(f'Unknown sign markless comparison operator: `{cmp.raw}`')
        
        if lbl.type != 'lbl':
            lbl.Error(f'Expected identifier of label type, got: `{lbl.type}`')

        if gotokword.raw != 'goto':
            gotokword.Error('Expected keyword: `goto`')

        lhsreg = cstate.M_RegLoc(lhs.raw)
        rhsreg = cstate.M_RegLoc(rhs.raw)
        
        cstatename = linenum
        cstate.M_PrepCmpJmp(lhsreg, rhsreg, condCode)
        cstate.M_PushStateChange(cstatename, lbl.raw)
        cstate.M_CmpJmp(lbl.raw)
        cstate.M_PushStateChange(lbl.raw, cstatename)
        
                
    def Parse(line):
        nonlocal opsyms, cstate
        global linenum

        if not line.CanPop():
            return
        tkn = line.pop()

        #Special stateless status which occurs after unconditional gotos
        if cstate is NoneState:
            #From statements
            if tkn.raw == 'from':
                lbl = line.pop()
                if lbl.type != 'lbl':
                    lbl.Error(f'Expected identifier of label type, got: `{lbl.type}`')
                lblname = lbl.val
                if lblname not in states:
                    lbl.Error(f'Can only resume with state of previous label, not future static label')
                tarstate = copy(states[lblname])
                cstate = tarstate
                line.AssertEmpty()
            else:
                tkn.Error('State cannot be inferred following an unconitional goto, please use a `from` statement')
            return

        #Declarations
        if tkn.raw == 'decl':
            ParseDecl(line)

        #Memsync
        elif tkn.raw == 'memsync':
            var = line.pop()
            if var.type == 'v-ident':
                cstate.M_MemSyncVar(var.raw)
            elif var.type == 'u-ident':
                var.Error(f'Cannot memsync undeclared identifier `{var.val}`')
            else:
                var.Error(f'Expected variable, got type: `{var.type}`')

        #Regsync
        elif tkn.raw == 'regsync':
            var = line.pop()
            if var.type == 'v-ident':
                cstate.M_RegSyncVar(var.raw)
            elif var.type == 'u-ident':
                var.Error(f'Cannot regsync undeclared identifier `{var.val}`')
            else:
                var.Error(f'Expected variable, got type: `{var.type}`')

        #Labels
        elif tkn.raw[-1] == ':' and tkn.type == 'lbl':
            states[tkn.val] = copy(cstate)
            line.AssertEmpty()
            cstate.M_PushLbl(tkn.val)

        #From statements
        elif tkn.raw == 'from':
            lbl = line.pop()
            if lbl.type != 'lbl':
                lbl.Error(f'Expected identifier of label type, got: `{lbl.type}`')
            lblname = lbl.val

            cstatename = linenum
            states[cstatename] = copy(cstate)
            if lblname not in states:
                lbl.Error(f'Can only resume with state of previous label, not future static label')
            tarstate = copy(states[lblname])
            cstate.M_PushStateChange(cstatename, lblname)
            cstate = tarstate
            line.AssertEmpty()

        #Always goto statements
        elif tkn.raw == 'goto':
            lbl = line.pop()
            if lbl.type != 'lbl':
                lbl.Error(f'Expected identifier of label type, got: `{lbl.type}`')
            lblname = lbl.val

            cstatename = linenum
            states[cstatename] = copy(cstate)
            cstate.M_PushStateChange(cstatename, lblname)
            cstate.M_UCJmp(lblname)
            cstate = NoneState
            line.AssertEmpty()

        #Simple varients of conditional gotos:
        elif tkn.raw == 'common':
            ntkn = line.pop()
            
            #Comparions driven conditional goto statements
            if ntkn.raw == 'cmp':
                ParseCmpGoto(line)

            elif ntkn.raw == 'flg':
                ntkn.Error('Path not implemented: Common Flag Goto')
                ParseFlgGoto(line)

        #Generally better variants, but more complicated
        elif tkn.raw == 'cmp':
            tkn.Error('Path not implemented: Fast Cmp Goto')
            ParseFastCmpGoto(line)

        elif tkn.raw == 'flg':
            tkn.Error('Path not implemented: Fast Flag Goto')
            ParseFastFlgGoto(line)

        #Binary Ops & Returning IFuncs
        elif tkn.type in ['v-ident', 'num']:
            mid = line.pop()
            if mid.raw in opsyms:
                rhsi = line.pop()
                if rhsi.type in ['addr', 'num', 'v-ident', 'lbl']:
                    ParseBinaryOp(line)
                elif mid.raw == '=' and rhsi.type == 'i-func':    #Simple assignment is overloaded, so fall back to other cases
                    ParseRetIFunc(line)
                else:
                    mid.Error('Expected a numeric type or variable as rhs, found: `{rhsi.type}`, which is not valid with operator: `{mid.raw}`')
                    
            else:
                mid.Error('Line starts with variable, and thus must be followed by either a binary operator, function call, or name cycling')

        #Void IFuncs
        elif tkn.type == 'i-func':
            ParseVoidIFunc(line)

        #Different error messages
        elif tkn.type == 'addr':
            tkn.Error(f'Assigning to an address is not allowed')
        else:
            if line.CanPop():
                ntkn = line.pop()
                if ntkn.raw in opsyms:
                    tkn.Error(f'Usage of undeclared identifier of type `{tkn.type}`')
            tkn.Error(f'Unable to detirmine type of line based on initial token, got type: `{tkn.type}`')

        line.AssertEmpty()

    def SIAParse(line):
        nonlocal lbls, funcs

        if not line.CanPop():
            return

        tkn = line.pop()
        if tkn.type == 'u-ident' and tkn.raw[-1] == ':':
            lbl = tkn.raw[:-1]
            lbls.append(lbl)
            line.AssertEmpty()
        elif tkn.raw == 'func':
            ParseFuncHeader(line)
        elif tkn.raw == 'macro':
            tkn.Error('Path not implemented: Macros')
        


    ####################################################################################
    #  * * * * * * * * * * * * * * *                    * * * * * * * * * * * * * * *  #
    # * * * * * * * * * * * * * * * * Code Starts Here * * * * * * * * * * * * * * * * #
    #  * * * * * * * * * * * * * * *                    * * * * * * * * * * * * * * *  #
    ####################################################################################

    opsyms = [sym for bits,opclass,sym in OPCODES.values()]

    cstate = State()
##    print(f'{hash(pstate)=}, {hash(cstate)=}')
      
    lbls = []
    funcs = []
    mark = []
    dmark = []
    states = {}

    #0. Static Identifier Analysis
    for linenum, line in enumerate(contents.split('\n')):
        line = TknList(line, cstate.vIdents, cstate.sIdents, funcs, lbls)
        if len(line.comment)>0 and line.comment[0]=='!':
            if len(line.comment)>1 and line.comment[1]=='!':
                dmark.append(linenum)
            mark.append(linenum)

        try:
            SIAParse(line)
        except TokenlessCompileError as e:
            print()
            print(str(e))
            print()
            print(traceback.format_exc())
            NoHintError('Static Identifier Analysis Parsing Failure')


    #1. Main Expansions
    immexp = []
    for linenum, line in enumerate(contents.split('\n')):
        line = TknList(line, cstate.vIdents, cstate.sIdents, funcs, lbls)

        try:
            Parse(line)
        except TokenlessCompileError as e:
            print()
            print(str(e))
            print()
            print(traceback.format_exc())
            NoHintError('Parsing Failure')
        
##        print('`'+'`'.join(x.raw for x in line.tkns)+'`')

    asm=[]

    maxlbllen = 1+max([len(d['lbl']) for d in immexp if 'lbl' in d])
    srcl = 0

    #4. Compile to assembly
    for x in immexp:
        if srcl != x['rSrc'] and len([v for v in dmark if srcl < v < x['rSrc']]) > 0:
            asm.append('')
        if 'op' in x:   #Ready assembly
            if 'to' in x:
                op = x['op']
                dest = x['to']
                if op == 'jmp':
                    asm.append(f'jmp\t{dest}:')
                elif op == 'cmpjmp':
                    asm.append(f'jmpu\t{dest}:')
            elif 'Rd' in x:   #Two register type
                Rs = x['Rs']
                Rd = x['Rd']
                op = x['op']
                if x.get('Imm', False):
                    Rs = f'[{hex(Rs)[2:]}]'
                else:
                    Rs = f'R{hex(Rs)[2:]}'
                Rd = f'R{hex(Rd)[2:]}'
                asm.append(f'{op}\t{Rd}, {Rs}')
            else:
                Rs = x['Rs']
                op = x['op']
                if op == 'usm':
                    asm.append(f'{op}\t{Rs}')
                else:
                    if x.get('Imm', False):
                        Rs = f'[{hex(Rs)[2:]}]'
                    else:
                        Rs = f'R{hex(Rs)[2:]}'
                    asm.append(f'{op}\t{Rs}')
            asm[-1]+='\t\t#'+x['Src']
            asm[-1] = ' '*(1+maxlbllen) + asm[-1]

            srcl = x['rSrc']
            if srcl in mark:
                asm[-1]='\t'+asm[-1]
        elif 'lbl' in x:
            lbl = x['lbl']+':'
            asm.append(lbl.ljust(maxlbllen))
            asm[-1]+='\t\t\t\t#'+x['Src']
        else:
            asm.append(repr(x))
            asm[-1] = ' '*(1+maxlbllen) + asm[-1]
            srcl = x['rSrc']
            if srcl in mark:
                asm[-1]='\t'+asm[-1]
    

    for x in asm:
        print(x)
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
