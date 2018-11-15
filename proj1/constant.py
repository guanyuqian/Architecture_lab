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

Constant.BASE_PC = 60
Constant.CODE_BYTES = 4
Constant.SPACE = ' '
Constant.TAB = '\t'
Constant.WRAP = '\n'
Constant.DIVIDE = ', '
Constant.NOP_CODE = '00000000000000000000000000000000'
Constant.BREAK_CODE = '000000001101'
Constant.FUNCTION_CODE_DICT = { \
    '110000': 'ADD', '110001': 'SUB', '100001': 'MUL', '110010': 'AND', '110011': 'NOR', '110101': 'SLT', \
    '101011': 'SW', '100011': 'LW', \
    '000010': 'J', '000111': 'BGTZ', '000001': 'BLTZ', '000100': 'BEQ', \
    '000000001000': 'JR', \
    '000000100000': 'ADD', '000000100010': 'SUB', '011100000010': 'MUL', \
    '000000100100': 'AND', '000000100111': 'NOR', '000000101010': 'SLT', \
    '000000000000': 'SLL', '000000000010': 'SRL', '000000000011': 'SRA' \
    }

Constant.OPERATOR_DICT = { \
    'ADD':'+','SUB':'rd=rs-rt','MUL':'rd=rs*rt'
    }
