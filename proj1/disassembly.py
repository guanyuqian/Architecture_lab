import constant as Constant


# 输出文件


# 反汇编入口
def dis_assembly():
    file = open(Constant.MIPS_MACHINE_CODE_PATH)
    dis_assembly_list = []
    dis_assembly_txt = ''
    line_num = 0
    # 内存数据的起始行数
    mem_line_num=0
    break_line_num = 0
    while 1:
        lines = file.readlines(Constant.READ_LINE_NUM_PER_TIME)
        if not lines:
            break
        for line in lines:
            line_num += 1
            if line[-1] != '\n': line += '\n'
            # 没有遇见break
            if break_line_num < 1:
                mem_line_num+=1
                dis_assembly_txt_operator, dis_assembly_txt_seg, break_line_num = dis_assembly_code(line, line_num)
                dis_assembly_list.append([dis_assembly_txt_operator, dis_assembly_txt_seg])
                dis_assembly_txt += device_machine_code(line) + Constant.TAB + \
                                    str(line_num * Constant.CODE_BYTES + Constant.BASE_PC) + Constant.TAB + \
                                    dis_assembly_txt_operator + Constant.SPACE + dis_assembly_txt_seg + Constant.WRAP
            else:
                val=complement_code2int(line)
                dis_assembly_list.append(val)
                dis_assembly_txt += line[:-1] + str(line_num * Constant.CODE_BYTES + Constant.BASE_PC) + \
                                    Constant.TAB + val + Constant.WRAP
    file.close()
    return dis_assembly_txt, dis_assembly_list,mem_line_num


# break之前，进入。返回machine_code分析出来的反汇编语句和是否遇上了break
def dis_assembly_code(machine_code, line_num):
    break_line_num = 0
    dis_assembly_txt_operator = ''
    dis_assembly_txt_seg = ''
    function_code = machine_code[0:6]
    if machine_code == Constant.NOP_CODE:
        dis_assembly_txt_operator += 'NOP'
    elif machine_code[:6] + machine_code[26:32] == Constant.BREAK_CODE:
        dis_assembly_txt_operator += 'BREAK'
        break_line_num = line_num
    elif valid_function_code(function_code):
        operator = Constant.FUNCTION_CODE_DICT[function_code]
        dis_assembly_txt_operator += operator
        # the instr_index field shifted left 2 bits.
        if operator == 'J':
            dis_assembly_txt_seg += '#' + str(int(machine_code[16:32] + '00', 2))
        elif operator == 'BLTZ' or operator == 'BGTZ':
            dis_assembly_txt_seg += machine_code2register(machine_code[6:11]) + Constant.DIVIDE + \
                                    '#' + str(int(machine_code[16:32] + '00', 2))
        elif operator == 'SW' or operator == 'LW':
            dis_assembly_txt_seg += machine_code2register(machine_code[11:16]) + Constant.DIVIDE + \
                                    str(int(machine_code[16:32], 2)) + \
                                    '(' + machine_code2register(machine_code[6:11]) + ')'
        elif operator == 'BEQ':
            dis_assembly_txt_seg += machine_code2register(machine_code[6:11]) + Constant.DIVIDE + \
                                    machine_code2register(machine_code[11:16]) + Constant.DIVIDE \
                                    + '#' + str(int(machine_code[16:32] + '00', 2))
        else:
            dis_assembly_txt_seg += machine_code2register(machine_code[11:16]) + Constant.DIVIDE + \
                                    machine_code2register(machine_code[6:11]) + Constant.DIVIDE \
                                    + '#' + str(int(machine_code[16:32], 2))
    else:
        function_code = machine_code[:6] + machine_code[26:32]
        if not valid_function_code(function_code):
            dis_assembly_txt_operator += "匹配不到操作符"
        else:
            operator = Constant.FUNCTION_CODE_DICT[function_code]
            dis_assembly_txt_operator += operator
            if operator == 'JR':
                dis_assembly_txt_seg += machine_code2register(machine_code[6:11])
            elif operator == 'SLL' or operator == 'SRL' or operator == 'SRA':
                dis_assembly_txt_seg += machine_code2register(machine_code[16:21]) + Constant.DIVIDE + \
                                        machine_code2register(machine_code[11:16]) + Constant.DIVIDE \
                                        + '#' + str(int(machine_code[21:26], 2))
            else:
                dis_assembly_txt_seg += machine_code2register(machine_code[16:21]) + Constant.DIVIDE + \
                                        machine_code2register(machine_code[6:11]) + Constant.DIVIDE \
                                        + machine_code2register(machine_code[11:16])
    return dis_assembly_txt_operator, dis_assembly_txt_seg, break_line_num


# 补码转换成整数
def complement_code2int(complement_code):
    tmp = int(complement_code[1:], 2)
    return str((tmp, tmp - 2147483648)[int(complement_code[0])])


# 把32位机器码分割成 6|5|5|5|5|6
def device_machine_code(machine_code):
    return machine_code[:6] + ' ' + machine_code[6:11] + ' ' + machine_code[11:16] + ' ' \
           + machine_code[16:21] + ' ' + machine_code[21:26] + ' ' + machine_code[26:32]


# 判断是否存在此操作码
def valid_function_code(function_code):
    if function_code in Constant.FUNCTION_CODE_DICT:
        return True
    else:
        return False


# 判断是否存在此操作码
def machine_code2register(machine_code):
    return 'R' + str(int(machine_code, 2))
