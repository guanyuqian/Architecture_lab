from constant import  OPERATOR_DICT
# 从Rx 读取到 R[x]
def str2register(code,R):
    num=filter(str.isdigit,code)
    return eval('R['+str(num)+']')
def simulate(dis_assembly_list):
    PC=0
    R=[1]*32
    while dis_assembly_list[PC]!= 'BREAK':
        operator=dis_assembly_list[PC][0]
        eval('R[0]=R[1]+R[2]')
        #exec(OPERATOR_DICT[operator],locals={'rs':R[0],'rt':R[1],'rd':R[2]})


if __name__ == "__main__":
    simulate(   [['ADD','R0,R1,R2'],['ADD','R0,R1,R2']]
)