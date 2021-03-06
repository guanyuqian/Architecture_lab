﻿# coding=utf-8


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
Constant.MIPS_MACHINE_CODE_PATH = 'sample_int.txt'
Constant.MIPS_SIMULATION_PATH = 'simulation_int.txt'
Constant.MIPS_DIS_ASSEMBLY_PATH = 'disassembly_int.txt'

Constant.LINE_DATA_COUNT = 8
Constant.BASE_PC = 60
Constant.CODE_BYTES = 4
Constant.SPACE = ' '
Constant.TAB = '\t'
Constant.WRAP = '\n'
Constant.DIVIDE = ', '
Constant.NOP_CODE = '00000000000000000000000000000000\n'
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
    'ADD': 'rd=int(rs)+int(rt)', 'SUB': 'rd=int(rs)-int(rt)',
    'MUL': 'rd=int(rs)*int(rt)',
    'AND': 'rd=int(rs)&int(rt)', 'NOR': 'rd=~(int(rs)|int(rt))',
    'SLT': 'rd = (int(rs) < int(rt))',
    'SLL': 'rd=SLL(rs,rt)',
    'SRL': 'rd=SRL(rs,rt)',
    'SRA': 'rd=int(rs)>>int(rt)',
    'NOP': '', 'BREAK': '',
    # 保留原来PC的最高四位
    'J': 'PC =int((int(PC) & int(1006632960)) +(r-64)/4)', 'JR': 'PC =(r-64)/4',
    'BEQ': 'if rd==rs : PC += int(rt/4)',
    'BGTZ': 'if(int(r)>0):PC +=int(offset/4)',
    'BLTZ': 'if(int(r)<0):PC +=int(offset/4)',
    'LW': 'rd=memory[int((rs+rt-64)/4)]',
    'SW': 'memory[int((rs+rt-64)/4)]=int(rd)'
}

# 汇编指令使用参数的情况
Constant.USE_PARM_DICT = {
    'rd,rs,rt': ['rd', 'rs', 'rt'],
    'r': ['r'],
    'r,offset': ['r', 'offset']
}


def SRL(rs, rt):
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
Constant.SLL=SLL
Constant.SRL=SRL

# project2
Constant.IF_MAX_COUNT = 2
Constant.PRE_ISSUE_SIZE = 4
Constant.BRANCH_INST = ['J', 'JR', 'BEQ', 'BGTZ', 'BLTZ']
Constant.ISSUE_MAX_COUNT = 2
# function operands dict
Constant.FU_OP_DICT = {'MEM': ['SW', 'LW'], 'ALUB': ['SLL', 'SRL', 'SRA', 'MUL'], 'ALU': ['DEFAULT']}

Constant.POST_BUFFER_NAME=['post_mem', 'post_alu', 'post_alub']
# 没有目标寄存器的指令
Constant.INST_NO_DEST_REGISTER = ['BREAK', 'NOP', 'SW']