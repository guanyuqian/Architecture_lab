# coding=utf-8
"""Module docstring.
This serves as a long usage message.
"""

# 程序主函数入口
from disassembly import dis_assembly
import constant as Constant

def write_file(txt, file_path):
    with open(file_path, 'wt') as f:
        print(txt, file=f, end='')

def main():
    dis_assembly_txt,dis_assembly_list=dis_assembly()
    write_file(dis_assembly_txt, Constant.MIPS_DIS_ASSEMBLY_PATH)

if __name__ == "__main__":
    main()
