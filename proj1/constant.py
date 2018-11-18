# coding=utf-8

def SLR(rs, rt):
    sa = int(rt)
    rs = int(rs)
    if rs < 0:
        if sa > 31:
            return '00000000000000000000000000000000'
        from disassembly import int2complement_code_32bits
        complement_code = int2complement_code_32bits(rs)
        return int('0' * sa + complement_code[:-sa], 2)
        pass
    else:
        return rs >> sa


def SLL(rs, rt):
    sa = int(rt)
    rs = int(rs)
    if sa > 31:
        return '00000000000000000000000000000000'
    from disassembly import int2complement_code_32bits
    complement_code = int2complement_code_32bits(rs)
    if complement_code[sa] == '1':
        return -1 * int(complement_code[sa + 1:] + '0' * sa, 2)
    else:
        return int(complement_code[sa + 1:] + '0' * sa, 2)


class Const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const value!")
        if not name.isupper():
            raise self.ConstCaseError('const "%s" is not all letters are capitalized' % name)
        self.__dict__[name] = value


import sys

sys.modules[__name__] = Const()

import constant as Constant

# 读取文件时每次读取的行数
Constant.READ_LINE_NUM_PER_TIME = 10000
# 输入的MIPS机器代码
Constant.MIPS_MACHINE_CODE_PATH = './doc/sample.txt'
Constant.MIPS_DIS_ASSEMBLY_PATH = './doc/disassembly.txt'
Constant.MIPS_SIMULATION_PATH = './doc/simulation.txt'
Constant.LINE_DATA_COUNT = 8
Constant.BASE_PC = 60
Constant.CODE_BYTES = 4
Constant.SPACE = ' '
Constant.TAB = '\t'
Constant.WRAP = '\n'
Constant.DIVIDE = ', '
Constant.NOP_CODE = '00000000000000000000000000000000'
Constant.BREAK_CODE = '000000001101'
Constant.FUNCTION_CODE_DICT = {
    '110000': 'ADD', '110001': 'SUB', '100001': 'MUL', '110010': 'AND', '110011': 'NOR', '110101': 'SLT',
    '101011': 'SW', '100011': 'LW',
    '000010': 'J', '000111': 'BGTZ', '000001': 'BLTZ', '000100': 'BEQ',
    '000000001000': 'JR',
    '000000100000': 'ADD', '000000100010': 'SUB', '011100000010': 'MUL',
    '000000100100': 'AND', '000000100111': 'NOR', '000000101010': 'SLT',
    '000000000000': 'SLL', '000000000010': 'SRL', '000000000011': 'SRA'
}

Constant.OPERATOR_DICT = {
    'ADD': 'rd=int(rs)+int(rt)\nnewPC=PC+1', 'SUB': 'rd=int(rs)-int(rt)\nnewPC=PC+1',
    'MUL': 'rd=int(rs)*int(rt)\nnewPC=PC+1',
    'AND': 'rd=int(rs)&int(rt)\nnewPC=PC+1', 'NOR': 'rd=~(int(rs)|int(rt))\nnewPC=PC+1',
    'SLT': 'rd = (int(rs) < int(rt))\nnewPC=PC+1',
    'SLL': 'rd=SLL(rs,rt)\nnewPC=PC+1',
    'SLR': 'rd=SLR(rs,rt)\nnewPC=PC+1',
    'SRA': 'rd=int(rs)>>int(rt)\nnewPC=PC+1',
    'NOP': 'newPC=PC+1', 'BREAK': 'newPC=PC+1',
    # 保留原来PC的最高四位
    'J': 'newPC =(int(PC)&int(1006632960))+(r-64)/4', 'JR': 'newPC =(r-64)/4',
    'BEQ': 'newPC=PC+1\nif(rd==int(rs)):newPC =newPC+(int(rt))/4',
    'BGTZ': 'newPC=PC+1\nif(r>0):newPC =newPC+(int(offset))/4',
    'BLTZ': 'newPC=PC+1\nif(r<0):newPC =newPC+(int(offset))/4',
    'LW': 'rd=dis_assembly_list[int((rs+rt-64)/4)]\nnewPC=PC+1',
    'SW': 'dis_assembly_list[int((rs+rt-64)/4)]=int(rd)\nnewPC=PC+1'
}

# 汇编指令使用参数的情况
Constant.USE_PARM_DICT = {
    'rd,rs,rt': ['rd', 'rs', 'rt'],
    'r': ['r'],
    'r,offset': ['r', 'offset']
}

Constant.SLL=SLL
Constant.SLR=SLR
