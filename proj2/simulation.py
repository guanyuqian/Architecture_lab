import threading

import constant as Constant
import copy

SLL = Constant.SLL
SRL = Constant.SRL
cycle = 0
memory = []
PC = 0
data_pc = 0
R = [0] * 32
issued_register_list = []
is_break = False
# {FU name:{FU status}}
FU_list = {}
synchronize_buffer = {
    'pre_issue': {'val': [], 'add_val': [], 'del_val': []},
    'pre_mem': {'val': [], 'add_val': [], 'del_val': []},
    'pre_alu': {'val': [], 'add_val': [], 'del_val': []},
    'pre_alub': {'val': [], 'add_val': [], 'del_val': []},
    'post_mem': {'val': [], 'add_val': [], 'del_val': []},
    'post_alu': {'val': [], 'add_val': [], 'del_val': []},
    'post_alub': {'val': [], 'add_val': [], 'del_val': []}
}
post_buffer_name = ['post_mem', 'post_alu', 'post_alub']
# 没有目标寄存器的指令
inst_no_dest_register = ['BREAK', 'NOP', 'SW']
wait_inst = None
exec_inst = None


# 更新周期中删掉和添加，buffer
def update_data():
    global synchronize_buffer, exec_inst
    output()
    for key, buffer in synchronize_buffer.items():
        # 将目标寄存器回复可读写
        if key in post_buffer_name and len(buffer['del_val']) and get_dest_register_str(buffer['del_val'][0]) != None:
            issued_register_list.remove(get_dest_register_str(buffer['del_val'][0]))
        buffer['val'] = [inst for inst in buffer['val'] if inst not in buffer['del_val']]
        buffer['val'].extend(buffer['add_val'])
        buffer['add_val'].clear()
        buffer['del_val'].clear()

        print(key)
        dump(buffer['val'])
    exec_inst = None


import pprint


def output():
    global cycle
    cycle += 1
    print(str(cycle) + '===========================================================')
    print('IF Unit:')
    print('wait_inst:', end='')
    print (wait_inst)
    print('exec_inst:', end='')
    print(exec_inst)


def dump(dic):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(dic)


def simulate(dis_assembly_list, mem_line_num):
    global memory, data_pc
    memory = dis_assembly_list
    data_pc = mem_line_num
    FU_list_init()
    while True:
        instruction_fetch()
        issue()
        execution()
        write_back()
        update_data()


def instruction_fetch():
    global is_break, PC, wait_inst, exec_inst
    pre_issue = synchronize_buffer['pre_issue']['val']
    add_pre_issue = synchronize_buffer['pre_issue']['add_val']
    left_slot = Constant.PRE_ISSUE_SIZE - len(pre_issue)
    # 可以添加的数是2或者上周期剩余的slot
    IF_left_count = (Constant.IF_MAX_COUNT, left_slot)[Constant.IF_MAX_COUNT > left_slot]
    while IF_left_count > 0:
        if wait_inst is not None:
            execute_branch(wait_inst)
            IF_left_count = 0
        else:
            inst = memory[int(PC)]
            PC += 1
            operator = inst[0]
            if operator in Constant.BRANCH_INST:
                execute_branch(inst)
                IF_left_count = 0
            else:
                if operator in ['BREAK', 'NOP']:
                    is_break = operator == 'BREAK'
                else:
                    add_pre_issue.append(inst)
                IF_left_count = IF_left_count - 1


def issue():
    pre_issue = synchronize_buffer['pre_issue']['val']
    del_pre_issue = synchronize_buffer['pre_issue']['del_val']
    issue_left_count = Constant.ISSUE_MAX_COUNT
    mem_stall = False
    i = 0
    # 之前没有issue的指令 防止war waw
    pre_no_issue_inst_list = []
    if cycle == 25:
        print ("")
    while i < len(pre_issue) and issue_left_count > 0:
        inst = pre_issue[i]
        FU_name = get_FU_name(inst)
        if mem_stall and (inst[0] == 'LW' or inst[0] == 'SW'):
            pass
        elif FU_pre_queue_is_useful_in_previous_cycle(FU_name) \
                and no_write_after_write_and_read(inst, pre_no_issue_inst_list):
            add_pre_FU_queue(FU_name, inst)
            del_pre_issue.append(pre_issue[i])
            # 将目标寄存器弹入
            if get_dest_register_str(inst) != None:
                issued_register_list.append(get_dest_register_str(inst))
            issue_left_count -= 1
        else:
            pre_no_issue_inst_list.append(inst)
            mem_stall = (inst[0] == 'LW' or inst[0] == 'SW')
        i += 1


def execution():
    for FU_name, FU in FU_list.items():
        # print (FU_name, ' value : ', FU)
        pre_FU_buffer = FU['pre_FU_buffer']
        post_FU_buffer = FU['post_FU_buffer']
        FU['FU_cycle'] += 1
        if FU['FU_cycle'] >= FU['FU_cycle_cost']:
            FU['FU_cycle'] = 0
            if len(pre_FU_buffer['val']):
                inst=pre_FU_buffer['val'][0]
                execute_inst(inst)
                pre_FU_buffer['del_val'] = [inst]
                if pre_FU_buffer['val'][0][0] != 'SW':
                    post_FU_buffer['add_val'] = [inst]


def write_back():
    for FU_name, FU in FU_list.items():
        # print (FU_name, ' value : ', FU)
        post_FU_buffer = FU['post_FU_buffer']
        if len(post_FU_buffer['val']):
            post_FU_buffer['del_val'] = [post_FU_buffer['val'][0]]


#   初始化功能单元
def FU_list_init():
    global FU_list
    FU_Names = ['ALU', 'ALUB', 'MEM']
    FU_list = {
        'ALU': {'pre_FU_buffer': synchronize_buffer['pre_alu'], 'pre_FU_queue_size': 2,
                'post_FU_buffer': synchronize_buffer['post_alu'], 'FU_cycle_cost': 1, 'FU_cycle': 0},
        'ALUB': {'pre_FU_buffer': synchronize_buffer['pre_alub'], 'pre_FU_queue_size': 2,
                 'post_FU_buffer': synchronize_buffer['post_alub'], 'FU_cycle_cost': 2, 'FU_cycle': 0},
        'MEM': {'pre_FU_buffer': synchronize_buffer['pre_mem'], 'pre_FU_queue_size': 2,
                'post_FU_buffer': synchronize_buffer['post_mem'], 'FU_cycle_cost': 1, 'FU_cycle': 0}
    }


# 将指令加入FU_name 的pre_FU队列
def add_pre_FU_queue(FU_name, inst):
    FU_list[FU_name]['pre_FU_buffer']['add_val'].append(inst)


# 获取inst对应的FU
def get_FU_name(inst):
    dict = Constant.FU_OP_DICT
    for FU_name in dict:
        if inst[0] in dict[FU_name]:
            return FU_name
    return 'ALU'


# 操作符对应的FU再上一个周期还有没有位置
def FU_pre_queue_is_useful_in_previous_cycle(FU_name):
    FU = FU_list[FU_name]
    return len(FU['pre_FU_buffer']['val']) < FU['pre_FU_queue_size']


# 对war 和waw进行判断
def no_write_after_write_and_read(inst, pre_no_issue_inst_list):
    global issued_register_list
    register_list = get_all_register_str(inst)
    dest_register = get_dest_register_str(inst)
    # 自己的源和目标寄存器不能被使用
    if len(set(register_list) & set(issued_register_list)) != 0:
        return False
    for pre_inst in pre_no_issue_inst_list:
        pre_register_list = get_all_register_str(pre_inst)
        pre_dest_register = get_dest_register_str(pre_inst)
        # 自己的寄存器不能为pre_stall_inst的目标寄存器
        if pre_dest_register in register_list:
            return False
        # 自己的目标寄存器不能是pre_stall_inst的寄存器
        if dest_register in pre_register_list:
            return False

    return True


def register_no_busy(inst):
    global issued_register_list
    register_list = get_all_register_str(inst)
    if len(set(register_list) & set(issued_register_list)) != 0:
        return False

    return True


# 获取目标寄存器
def get_dest_register_str(inst):
    if inst[0] in inst_no_dest_register:
        return None
    return change_code2parm_str_list(inst)[0]


def get_all_register_str(inst):
    parameters = change_code2parm_str_list(inst)
    register_list = [v for v in parameters if not str(v).isdigit()]
    return register_list


def execute_branch(inst):
    global wait_inst, exec_inst
    pre_issue = synchronize_buffer['pre_issue']['val']
    if no_write_after_write_and_read(inst, pre_issue):
        exec_inst = inst
        wait_inst = None
        execute_inst(inst)
    else:
        wait_inst = inst
    return


# 替换 rx 等指代寄存器为真实变量 rd=rs+rt -> R[0]=R[1]+12,两个list的长度必须相等
def get_exec_str(code, old_parm_list, new_parm_list):
    i = 0
    length = len(old_parm_list)
    while i < length:
        code = code.replace(old_parm_list[i], new_parm_list[i])
        i += 1
    return code


# 把指令后面的参数分开，并格式化变量对应的字符串 R0 -> R[0] | #12->12
def change_code2parm_str_list(inst):
    code = inst[1]
    if code=='':
        return []
    parms = code.replace('(', Constant.DIVIDE).replace(')', '').replace('#', '').split(Constant.DIVIDE)
    i = 0
    length = len(parms)
    while i < length:
        if (parms[i][0]) == 'R':
            parms[i] = parms[i][:1] + '[' + parms[i][1:] + ']'
        i += 1
    return parms


# 执行指令 branch操作 ：（读取寄存的值）更新PC
def execute_inst(inst):
    operator = inst[0]
    parms = []
    if inst[1] != '':
        parms = change_code2parm_str_list(inst)
    if operator == 'J' or operator == 'JR':
        use_parms = Constant.USE_PARM_DICT['r']
    elif operator == 'BLTZ' or operator == 'BGTZ':
        use_parms = Constant.USE_PARM_DICT['r,offset']
    elif operator in Constant.OPERATOR_DICT:
        use_parms = Constant.USE_PARM_DICT['rd,rs,rt']
    else:
        print('不识别操作')
    glo = globals()
    exec_str = get_exec_str(Constant.OPERATOR_DICT[inst[0]], use_parms, parms)

    exec (exec_str, glo)
    pass


if __name__ == "__main__":
    str_set = inst_list2str_set([['SLL', 'R16, R1, #2'], ['SLR', 'R16, R1, #2']])
    str_list = str_set2inst_list(str_set)
    pass
