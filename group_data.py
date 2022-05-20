import os
import sys
import getopt
import linecache

op_num = 25
r_time = 1

try:
    opts, args = getopt.getopt(sys.argv[1:],"ho:r:",["help","operation_num=","running_times="])
    for opt, arg in opts:
        if opt in ('-o','--operation_num'):
            op_num = int(arg)
        elif opt in ('-r','--running_times'):
            r_time = int(arg)
        elif opt in ('-h','--help'):
            print("python3 group_data.py -o <operation_num> -r <running_times>")
            sys.exit()
except getopt.GetoptError:
    print("python3 group_data.py -o <operation_num> -r <running_times>")
    sys.exit()

def get_op(op):
    op = op.strip('\n')
    arr = op[2:-1].split(',')
    return {
        'op_type': op[0],
        'var': arr[0],
        'val': arr[1],
        'client_id': int(arr[2]),
        'tra_id': int(arr[3]),
    }

for i in range(int(r_time)):
    folder_name = 'output/' + str(i) + '/'
    file_list = [fn for fn in os.listdir(folder_name) if fn.endswith('.txt')]
    ops = []

    for file in file_list:
        ops += linecache.getlines(folder_name + file)
    with open(folder_name + 'result.txt', 'w') as f:
        now_id = 0
        cnt = op_num
        for op in ops:
            op_dict = get_op(op)
            cnt = cnt - 1
            op_dict['tra_id'] = now_id
            if cnt == 0:
                cnt = op_num
                now_id += 1
            f.write(str(op_dict['op_type']) + '(' + str(op_dict['var']) + ',' + str(op_dict['val']) + ',' + str(op_dict['client_id']) + ',' + str(op_dict['tra_id']) + ')\n')
