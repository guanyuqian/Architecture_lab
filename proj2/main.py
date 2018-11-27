# coding=utf-8
"""Module docstring.
This serves as a long usage message.
"""

# 程序主函数入口
import sys

from disassembly import dis_assembly
import constant as Constant
from simulation import simulate


def write_file(txt, file_path):
    with open(file_path, 'wt') as f:
        print(txt, file=f, end='')


def main(sample_file, dis_assembly_file, simulation_file):
    dis_assembly_txt, dis_assembly_list, mem_line_num = dis_assembly(sample_file)
    write_file(dis_assembly_txt, dis_assembly_file)
    simulate_txt = simulate(dis_assembly_list, mem_line_num)
    write_file(simulate_txt, simulation_file)


if __name__ == "__main__":
    argv_length = len(sys.argv)
    sample_file = sys.argv[1] if argv_length > 1 else Constant.MIPS_MACHINE_CODE_PATH
    dis_assembly_file = sys.argv[2] if argv_length > 2 else Constant.MIPS_DIS_ASSEMBLY_PATH
    simulation_file = sys.argv[3] if argv_length > 3 else Constant.MIPS_SIMULATION_PATH

    main(sample_file, dis_assembly_file, simulation_file)
