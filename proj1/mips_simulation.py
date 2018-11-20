# coding=utf-8
"""Module docstring.
This serves as a long usage message.
"""

# 程序主函数入口
from disassembly import dis_assembly
import constant as Constant
from  simulation import simulate


def write_file(txt, file_path):
    with open(file_path, 'wt') as f:
        print(txt, file=f, end='')


def main():
    dis_assembly_txt, dis_assembly_list,mem_line_num = dis_assembly()
    write_file(dis_assembly_txt, Constant.MIPS_DIS_ASSEMBLY_PATH)
    simulate_txt=simulate(dis_assembly_list,mem_line_num)
    write_file(simulate_txt, Constant.MIPS_SIMULATION_PATH)


if __name__ == "__main__":
    # print(Constant.SLR('-16', '2'))
    print(Constant.SLL('1', '2'))
    main()
