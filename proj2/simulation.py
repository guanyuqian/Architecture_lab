import threading
import constant as Constant

# doc中对于load store 中store在load前面的情况没有考虑
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
# val: 周期开始时buffer，
# add_val:周期结束前会添加的buffer,
# del_val:周期结束前会删除的buffer,
# del_valout_put_name :用于输出
# buffer_size buffer的大小
synchronize_buffer = {
    'pre_issue': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Pre-Issue Buffer:', 'buffer_size': 4},
    'pre_alu': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Pre-ALU Queue:', 'buffer_size': 2},
    'post_alu': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Post-ALU Buffer:', 'buffer_size': 1},
    'pre_alub': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Pre-ALUB Queue:', 'buffer_size': 2},
    'post_alub': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Post-ALUB Buffer:', 'buffer_size': 1},
    'pre_mem': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Pre-MEM Queue:', 'buffer_size': 2},
    'post_mem': {'val': [], 'add_val': [], 'del_val': [], 'output_name': 'Post-MEM Buffer:', 'buffer_size': 1}
}
wait_inst = None
exec_inst = None
output_result=[]


def simulate(dis_assembly_list, mem_line_num):
    global memory, data_pc
    memory = dis_assembly_list
    data_pc = mem_line_num
    FU_list_init()
    while not is_break:
        pipeline_thread(instruction_fetch)
        pipeline_thread(issue)
        pipeline_thread(execution)
        pipeline_thread(write_back)
        update_data()
        output()
    return '\n'.join(output_result)+'\n'


def pipeline_thread(function):
    thread = threading.Thread(target=function, name='LoopThread')
    thread.start()
    thread.join()


def instruction_fetch():
    global is_break, PC, wait_inst, exec_inst
    exec_inst = None
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
                    exec_inst=inst[:1]
                else:
                    add_pre_issue.append(inst)
                IF_left_count = IF_left_count - 1


def issue():
    pre_issue = synchronize_buffer['pre_issue']['val']
    del_pre_issue = synchronize_buffer['pre_issue']['del_val']
    issue_left_count = Constant.ISSUE_MAX_COUNT
    i = 0
    # 之前没有issue的指令 防止war waw
    pre_no_issue_inst_list = []
    while i < len(pre_issue) and issue_left_count > 0:
        inst = pre_issue[i]
        FU_name = get_FU_name(inst)

        if Fu_pre_buffer_useful_count(FU_name) and mem_in_order(inst,pre_no_issue_inst_list)\
                and no_write_after_write_and_read(inst, pre_no_issue_inst_list):
            add_pre_FU_queue(FU_name, inst)
            del_pre_issue.append(pre_issue[i])
            # 将目标寄存器弹入
            if get_dest_register_str(inst) != None:
                issued_register_list.append(get_dest_register_str(inst))
            issue_left_count -= 1
        else:
            pre_no_issue_inst_list.append(inst)
        i += 1


# 更新周期中删掉和添加，buffer
def update_data():
    global synchronize_buffer, exec_inst
    for key, buffer in synchronize_buffer.items():
        # 如果FU是post_buffer且post_buffer不为空且指令有目标寄存器
        # 将对应的目标寄存器回复可读写
        if key in Constant.POST_BUFFER_NAME and len(buffer['del_val']) and \
                get_dest_register_str(buffer['del_val'][0]) != None:
            issued_register_list.remove(get_dest_register_str(buffer['del_val'][0]))
        # 删除buffer中的待删除元素，在周期末尾
        buffer['val'] = [inst for inst in buffer['val'] if inst not in buffer['del_val']]
        # 添加buffer中的待添加元素，在周期末尾
        buffer['val'].extend(buffer['add_val'])
        buffer['add_val'].clear()
        buffer['del_val'].clear()



def output():
    global cycle,output_result
    cycle += 1
    output_result.append('--------------------')
    output_result.append('Cycle:' + str(cycle))
    output_result.append('\nIF Unit:')
    output_result.append('	Waiting Instruction: ' + inst2str(wait_inst))
    output_result.append('	Executed Instruction: ' + inst2str(exec_inst))

    for key, buffer in synchronize_buffer.items():
        if buffer['buffer_size'] <= 1 and len(buffer['val']) != 0:
            output_result.append(buffer['output_name']+inst2str(buffer['val'][0],True))
        else:
            output_result.append(buffer['output_name'])
            if buffer['buffer_size'] > 1:
                for i in range(buffer['buffer_size']):
                    if i < len(buffer['val']):
                        output_result.append(('	Entry %d:' + inst2str(buffer['val'][i],True) )% i)
                    else:
                        output_result.append('	Entry %d:'% i)

    output_result.append('\nRegisters')
    output_result.append('R00:	'+'	'.join(map(str, R[0:8])))
    output_result.append('R08:	'+'	'.join(map(str, R[8:16])))
    output_result.append('R16:	'+'	'.join(map(str, R[16:24])))
    output_result.append('R24:	'+'	'.join(map(str, R[24:32])))
    output_result.append(data2str())

def data2str():
    global data_pc,memory
    result = '\nData\n'
    length = len(memory)
    line_index = 0
    tmp_data_pc=data_pc
    while tmp_data_pc < length:
        result += str(tmp_data_pc * 4 + 64) + ':	'
        while tmp_data_pc < length and line_index < Constant.LINE_DATA_COUNT:
            result += str(memory[tmp_data_pc]) + Constant.TAB
            line_index += 1
            tmp_data_pc += 1
        result = result[:-1] + '\n'
        line_index = 0
    result = result[:-1]
    return result



# bracket 中括号是否添加
def inst2str(inst, bracket=False):
    result = '	'.join(inst) if inst != None else ''
    return result if not bracket else '[' + result + ']'


#  The load instruction must wait until all the previous stores are issued.
#  The stores must be issued in order.
# if and only if current inst is memory inst and exit 'SW' inst previously
def mem_in_order(inst,pre_no_issue_inst_list):
    operator=inst[0]
    if (operator=='SW' or operator =='LW')\
        and len([v for v in pre_no_issue_inst_list if v[0]=='SW']):
        return False
    return True

def execution():
    global  cycle
    if cycle > 39:
        pass
    for FU_name, FU in FU_list.items():
        pre_FU_buffer = FU['pre_FU_buffer']
        post_FU_buffer = FU['post_FU_buffer']
        if len(pre_FU_buffer['val']):
            FU['FU_cycle'] += 1
        if FU['FU_cycle'] >= FU['FU_cycle_cost']:
            FU['FU_cycle'] = 0
            if len(pre_FU_buffer['val']):
                inst = pre_FU_buffer['val'][0]
                # 不立即更新寄存器，模拟周期
                # execute_inst(inst)
                pre_FU_buffer['del_val'].append(inst)
                if pre_FU_buffer['val'][0][0] != 'SW':
                    post_FU_buffer['add_val'].append(inst)
                # 'SW' 指令在此就立即写回内存
                else:
                    execute_inst_immediately(inst)


def write_back():
    for FU_name, FU in FU_list.items():
        post_FU_buffer = FU['post_FU_buffer']
        # 如果post_FU_buffer中有待写会指令就立即执行
        if len(post_FU_buffer['val']):
            post_FU_buffer['del_val'] .append(post_FU_buffer['val'][0])
            execute_inst_immediately(post_FU_buffer['val'][0])


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


# 操作符对应的FU再上一个周期还有多少位置,是否还有坑
def Fu_pre_buffer_useful_count(FU_name):
    FU = FU_list[FU_name]
    return FU['pre_FU_queue_size']-len(FU['pre_FU_buffer']['val'])-len(FU['pre_FU_buffer']['add_val'])


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
    if inst[0] in Constant.INST_NO_DEST_REGISTER:
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
        execute_inst_immediately(inst)
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
    if code == '':
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
def execute_inst_immediately(inst):
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
    exec(exec_str, glo)

if __name__ == "__main__":
    str_set = inst_list2str_set([['SLL', 'R16, R1, #2'], ['SLR', 'R16, R1, #2']])
    str_list = str_set2inst_list(str_set)
    pass
