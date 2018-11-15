from constant import OPERATOR_DICT
import constant as  Constant
from constant import USE_PARM_DICT


# 从Rx 读取到 R[x]
def str2register(code, R):
    num = filter(str.isdigit, code)
    return eval('R[' + str(num) + ']')


# 把指令后面的参数分开，并格式化变量对应的字符串 R0 -> R[0] | #12->12
def change_code2parm_str_list(code):
    parms = code.replace('(', Constant.DIVIDE).replace(')', '').replace('#', '').split(Constant.DIVIDE)
    i = 0
    length = len(parms)
    while i < length:
        if (parms[i][0]) == 'R':
            parms[i] = parms[i][:1] + '[' + parms[i][1:] + ']'
        i += 1
    return parms


# 替换 rx 等指代寄存器为真实变量 rd=rs+rt -> R[0]=R[1]+12,两个list的长度必须相等
def get_exec_str(code, old_parm_list, new_parm_list):
    i = 0
    length = len(old_parm_list)
    while i < length:
        code = code.replace(old_parm_list[i], new_parm_list[i])
        i += 1
    return code


def simulate(dis_assembly_list, mem_line_num):
    PC = 0
    R = [0] * 32
    simulate_txt = ''
    cycle = 0
    while True:
        cycle += 1
        operator = dis_assembly_list[PC][0]
        parms_str = dis_assembly_list[PC][1]
        if parms_str != '':
            parms = change_code2parm_str_list(parms_str)
            parms_str = Constant.TAB + dis_assembly_list[PC][1]
        if operator == 'J' or operator == 'JR':
            use_parms = USE_PARM_DICT['r']
        elif operator == 'BGTZ' or operator == 'BGTZ':
            use_parms = USE_PARM_DICT['r,offset']
        elif operator in OPERATOR_DICT:
            use_parms = USE_PARM_DICT['rd,rs,rt']
        else:
            print('不识别操作')
            PC += 1
            continue
        exec_str = OPERATOR_DICT[operator]
        loc = locals()
        exec(get_exec_str(exec_str, use_parms, parms), loc)
        PC_print = str(PC * 4 + 64)
        simulate_seg = '--------------------\n' \
                       'Cycle:' + str(cycle) + Constant.TAB + PC_print + Constant.TAB + \
                       dis_assembly_list[PC][0] + parms_str + '\n\n' + \
                       R2str(R) + mem2str(dis_assembly_list, mem_line_num)
        print(simulate_seg)
        PC = int(loc['newPC'])
        simulate_txt += simulate_seg
        if operator == 'BREAK':
            break
    return simulate_txt


def R2str(R):
    result = 'Registers\nR00:	'
    for r in R[0:16]:
        result += str(r) + Constant.TAB
    result = result[:-1] + '\n'
    result += 'R16:	'
    for r in R[16:32]:
        result += str(r) + Constant.TAB
    result = result[:-1] + '\n\n'
    return result


def mem2str(mem, pc):
    result = 'Data\n'
    length = len(mem)
    line_index = 0
    while pc < length:
        result += str(pc * 4 + 64) + ':	'
        while pc < length and line_index < Constant.LINE_DATA_COUNT:
            result += str(mem[pc]) + Constant.TAB
            line_index += 1
            pc += 1
        result = result[:-1] + '\n'
        line_index = 0
    return result
