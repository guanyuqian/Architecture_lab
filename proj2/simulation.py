import threading

import constant as  Constant

memory = []
PC = 0
data_pc = 0
R = [0] * 32
register_result_status = [None] * 32

is_break = False


def simulate(dis_assembly_list, mem_line_num):
    global memory
    global data_pc
    memory = dis_assembly_list
    data_pc = mem_line_num

    pre_issue = []
    wait_inst = None
    exec_inst = None
    while True:
        instruction_fetch(pre_issue, wait_inst, exec_inst)
        print(pre_issue)
        print(wait_inst)
        print(exec_inst)
        print('end_event.set')
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


def instruction_fetch_thread(begin_event, end_event):
    pre_issue = []
    wait_inst = None
    exec_inst = None
    print('in instruction_fetch_thread')

    while True:
        if is_break:
            break
        print(' event.wait()')
        begin_event.wait()
        instruction_fetch(pre_issue, wait_inst, exec_inst)
        print(pre_issue)
        print(wait_inst)
        print(exec_inst)
        print('end_event.set')
        end_event.set()


def instruction_fetch(pre_issue, wait_inst, exec_inst):
    global is_break
    global PC
    exec_inst = None
    IF_left_count = Constant.IF_MAX_COUNT
    while IF_left_count > 0:
        if wait_inst is not None:
            execute_branch(wait_inst, wait_inst, exec_inst)
        elif len(pre_issue) < Constant.PRE_ISSUE_SIZE:
            inst = memory[int(PC)]
            PC += 1
            operator = inst[0]
            if operator in Constant.BRANCH_INST:
                execute_branch(inst, wait_inst, exec_inst)
            else:
                if operator in ['Break', 'Nop']:
                    is_break = operator == 'Break'
                else:
                    pre_issue.append(inst)
                IF_left_count = IF_left_count - 1
        else:
            break


# 指令需要的所以寄存器都准备好了吗[operator,operands]
def inst_register_all_ready(inst):
    register_id_list = inst[1].split('#')[0].replace('R', '').split(Constant.DIVIDE)
    print(register_id_list)
    for register_id in register_id_list:
        if register_id.isdigit() and \
                register_result_status[int(register_id)] is not None:
            return False
    return True


def execute_branch(inst, wait_inst, exec_inst):
    if inst_register_all_ready(inst):
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
    exec(get_exec_str(exec_str, use_parms, parms), glo)


if __name__ == "__main__":
    inst_register_all_ready(['SLL', 'R16, R1, #2'])
