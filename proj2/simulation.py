import threading

import constant as Constant
import copy

memory = []
PC = 0
data_pc = 0
R = [0] * 32
register_result_status = [None] * 32
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
pre_issue = synchronize_buffer['pre_issue']['val']
add_pre_issue = synchronize_buffer['pre_issue']['add_val']
del_pre_issue = synchronize_buffer['pre_issue']['del_val']

wait_inst = None
exec_inst = None


def update_data():
    global synchronize_buffer
    for buffer in synchronize_buffer:
        buffer['val']=list(set(buffer['val']).union( buffer['add_val']).difference(set(buffer['del_val'])))
        buffer['add_val'].clear()
        buffer['del_val'].clear()
def simulate(dis_assembly_list, mem_line_num):
    global memory, data_pc
    memory = dis_assembly_list
    data_pc = mem_line_num
    FU_list_init()
    while True:
        instruction_fetch()
        issue()
        execution()
        update_data()
    # IF_begin_event = threading.Event()
    # IF_end_event = threading.Event()
    # IF_thread = threading.Thread(target=instruction_fetch_thread, args=(IF_begin_event, IF_end_event))
    # thread_list = [{'thread': IF_thread, 'begin_event': IF_begin_event, 'end_event': IF_end_event}]
    # for thread in thread_list:
    #     thread['thread'].start()
    # while True:
    #     if is_break:
    #         break
    #     for thread in thread_list:
    #         thread['begin_event'].set()
    #     for a in range(len(thread_list)):
    #         thread['end_event'].wait()


#
# def instruction_fetch_thread(begin_event, end_event):
#     pre_issue = []
#     wait_inst = None
#     exec_inst = None
#     print('in instruction_fetch_thread')
#
#     while True:
#         if is_break:
#             break
#         print(' event.wait()')
#         begin_event.wait()
#         instruction_fetch(pre_issue, wait_inst)
#         print(pre_issue)
#         print(wait_inst)
#         print(exec_inst)
#         print('end_event.set')
#         end_event.set()
#

def instruction_fetch():
    global pre_issue, is_break, PC, wait_inst, exec_inst
    left_slot=Constant.PRE_ISSUE_SIZE-len(pre_issue)
    # 可以添加的数是2或者上周期剩余的slot
    IF_left_count =(Constant.IF_MAX_COUNT, left_slot)[Constant.IF_MAX_COUNT>left_slot]
    while IF_left_count > 0:
        if wait_inst is not None:
            execute_branch(wait_inst)
        else :
            inst = memory[int(PC)]
            PC += 1
            operator = inst[0]
            if operator in Constant.BRANCH_INST:
                execute_branch(inst)
            else:
                if operator in ['Break', 'Nop']:
                    is_break = operator == 'Break'
                else:
                    add_pre_issue.append(inst)
                IF_left_count = IF_left_count - 1
    exec_inst = None


def issue():
    global pre_issue
    issue_left_count = Constant.ISSUE_MAX_COUNT
    mem_stall = False
    i = 0
    while i < len(pre_issue) and issue_left_count > 0:
        inst = pre_issue[i]
        FU_name = get_FU_name(inst)
        if not mem_stall and FU_pre_queue_is_useful_in_previous_cycle(FU_name) \
                and is_register_all_ready_in_previous_cycle(inst) and not mem_stall:
            add_pre_FU_queue(FU_name, inst)
            del_pre_issue.append(pre_issue[i])
            set_register_status_2_FU_name(inst, FU_name)
            issue_left_count -= 1
        else:
            mem_stall = (inst[0] == 'LW' | 'SW')
            i += 1


def execution():
    for FU_name, FU in FU_list.items():
        print (FU_name, ' value : ', FU)
        FU['pre_FU_buffer']['val'].clear()


#   初始化功能单元
def FU_list_init():
    global FU_list
    FU_Names = ['ALU', 'ALUB', 'MEM']
    FU_list = {
        'ALU': {'pre_FU_buffer': synchronize_buffer['pre_alu'], 'pre_FU_queue_size': 2, 'post_FU_buffer': synchronize_buffer['post_alu'], 'FU_cycle_cost': 1, 'FU_cycle': 0},
        'ALUB': {'pre_FU_buffer': synchronize_buffer['pre_alub'], 'pre_FU_queue_size': 2, 'post_FU_buffer': synchronize_buffer['post_alu'], 'FU_cycle_cost': 2, 'FU_cycle': 0},
        'MEM': {'pre_FU_buffer': synchronize_buffer['pre_mem'], 'pre_FU_queue_size': 2, 'post_FU_buffer': synchronize_buffer['post_alu'], 'FU_cycle_cost': 1, 'FU_cycle': 0}
    }


# 将指令加入FU_name 的pre_FU队列
def add_pre_FU_queue(FU_name, inst):
    FU_list[FU_name]['pre_FU_buffer']['add_val'].append(inst)


# 获取inst对应的FU
def get_FU_name(inst):
    dict = Constant.FU_OP_DICT
    for FU_name in dict:
        if inst[0] in dict[FU_name]:
            return dict[FU_name]
    return 'ALU'


# 操作符对应的FU再上一个周期还有没有位置
def FU_pre_queue_is_useful_in_previous_cycle(FU_name):
    FU = FU_list[FU_name]
    return len(FU['pre_FU_buffer']['val']) < FU['pre_FU_queue_size']


# 指令需要的所以寄存器都准备好了吗[operator,operands]
def is_register_all_ready_in_previous_cycle(inst):
    global register_result_status
    register_id_list = inst[1].split('#')[0].replace('R', '').split(Constant.DIVIDE)
    print(register_id_list)
    for register_id in register_id_list:
        if register_id.isdigit() and \
                register_result_status[int(register_id)] is not None:
            return False
    return True


# 从指令中取出第一个寄存器，将他的状态设为FU_name
def set_register_status_2_FU_name(inst, FU_name):
    rid = get_dest_register_id(inst)
    R[rid] = FU_name


# 获取目标寄存器ID 即第一个寄存器ID
def get_dest_register_id(inst):
    return int(inst[1].split(Constant.DIVIDE)[0].replace('R', ''))


def execute_branch(inst):
    global wait_inst, exec_inst
    if is_register_all_ready_in_previous_cycle(inst):
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
def change_code2parm_str_list(code):
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
    parms_str = inst[1]
    if parms_str != '':
        parms = change_code2parm_str_list(parms_str)
        parms_str = Constant.TAB + parms_str
    if operator == 'J' or operator == 'JR':
        use_parms = Constant.USE_PARM_DICT['r']
    elif operator == 'BLTZ' or operator == 'BGTZ':
        use_parms = Constant.USE_PARM_DICT['r,offset']
    elif operator in Constant.OPERATOR_DICT:
        use_parms = Constant.USE_PARM_DICT['rd,rs,rt']
    else:
        print('不识别操作')
    glo = globals()
    exec_str = Constant.OPERATOR_DICT[inst[0]]
    exec (get_exec_str(exec_str, use_parms, parms), glo)


if __name__ == "__main__":
    inst_register_all_ready(['SLL', 'R16, R1, #2'])
