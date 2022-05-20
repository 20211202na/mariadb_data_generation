import os
import random
import sys
import getopt
import threading
import mariadb
import numpy as np

wo_rate=0.2 # rate of read-only transactions 
ro_rate=0.2 # rate of write-only transactions 
wr_rate = 0.5 # rate of read/write operations in mixing transactions 
transaction_num = 100 # transacion num of each client
operation_num = 25 # operation num in each transaction
threads_num = 20 # client number
folder_num = 0 # the output folder number
server = "127.0.0.1"

try:
    opts, args = getopt.getopt(sys.argv[1:],"hw:r:p:t:o:c:n:f:s:",["help","wo_rate=","ro_rate=","w_percent=","trans_num=","op_num=","client_num=","folder_num=","server="])
    for opt, arg in opts:
        if opt in ('-w','--wo_rate'):
            wo_rate = float(arg)
        elif opt in ('-r','--ro_rate'):
            ro_rate = float(arg)
        elif opt in ('-p','--w_percent'):        
            wr_rate = float(arg)
        elif opt in ('-t','--trans_num'):
            transaction_num = int(arg)
        elif opt in ('-o','--op_num'):
            operation_num = int(arg)
        elif opt in ('-c','--client_num'):
            threads_num = int(arg)
        elif opt in ('-f','--folder_num'):
            folder_num = str(arg)
	elif opt in ('-s','--server'):
            server = str(arg)
        elif opt in ('-h','--help'):
            print("python3 maria.py -w <wo_rate> -r <ro_rate> -p <w_percent> -t <trans_num> -o <op_num> -c <client_num> -f <folder_num> -s <server>")
            sys.exit()
except getopt.GetoptError:
    print("python3 maria.py -w <wo_rate> -r <ro_rate> -p <w_percent> -t <trans_num> -o <op_num> -c <client_num> -s <server>")
    sys.exit()

key_num = 20 # key number in database
total_op_num = 3 * transaction_num * operation_num
folder_name = "./output/"+str(folder_num)+"/" # folder of output transaction record
hist_folder = "./client/"+str(folder_num)+"/" # folder of generated transaction traces



def mk_dir(path):
	folder = os.path.exists(path)
	if not folder:                   
		os.makedirs(path)            

class myThread(threading.Thread):
    def __init__(self,id):
        threading.Thread.__init__(self)
        self.id = id
        pass
    def run(self):
        run_thread(i)

class Operation:
    op_type = True  #true is write
    variable = 0
    value = 0
    
    def __init__(self, op_type, variable, value):
        self.op_type = op_type
        self.variable = variable
        self.value = value

    def Read(self,variable):
        self.op_type = False
        self.variable = variable
        self.value = 0
    def Write(self,variable,value):
        self.op_type = True
        self.variable = variable
        self.value = value


def Zipf(a: np.float64, min: np.uint64, max: np.uint64, size=None):
    """
    Generate Zipf-like random variables,
    but in inclusive [min...max] interval
    """
    if min == 0:
        raise ZeroDivisionError("")

    v = np.arange(min, max+1) # values to sample
    p = 1.0 / np.power(v, a)  # probabilities
    p /= np.sum(p)            # normalized

    return np.random.choice(v, size=size, replace=True, p=p)



def zipf_generator(output_path, client, trans, ops, var):
    '''
    output_path: hist file path
    client: client No.
    trans: trans num for each client
    ops: operation num for each trans
    var: key num
    wr: rate of w/r
    '''
    doc = open(output_path+"hist_"+str(client)+".txt",'w')
    counter = client * total_op_num * 2
    min = np.uint64(1)
    max = np.uint64(var)
    q = Zipf(1, min, max, trans*ops)
    var_list = [int(x)-1 for x in q]
    var_count = 0
    for t in range (0,trans):
        trans_type = random_pick([0,1,2],[wo_rate,ro_rate,1-wo_rate-ro_rate])
        if trans_type == 0:
            for op in range (0,ops):
                variable = var_list[var_count]
                var_count += 1
                counter += 1
                new_op = Operation(True,variable,counter)
                doc.write("write," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        elif trans_type == 1:
            for op in range (0,ops):
                variable = var_list[var_count]
                var_count += 1
                new_op = Operation(False,variable,0)
                doc.write("read," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        elif trans_type == 2:
            w_count = 0
            r_count = 0
            for i in range (0,ops):
                op_type = random_pick([0,1],[wr_rate,1-wr_rate])
                if op_type == 0:
                    w_count += 1
                elif op_type == 1:
                    r_count += 1
                else:
                    print("Error in op_type!")
            for r in range(r_count):
                variable = var_list[var_count]
                var_count += 1
                new_op = Operation(False,variable,0)
                doc.write("read," + str(new_op.variable) + "," + str(new_op.value)+"\n")
            for w in range(w_count):
                variable = var_list[var_count]
                var_count += 1
                counter += 1
                new_op = Operation(True,variable,counter)
                doc.write("write," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        else:
            print("Error in trans_type!")
    doc.close()




def uniform_generator(output_path, client, trans, ops, var):
    '''
    output_path: hist file path
    client: client No.
    trans: trans num for each client
    ops: operation num for each trans
    var: key num
    wr: rate of w/r
    '''
    doc = open(output_path+"hist_"+str(client)+".txt",'w')
    counter = client * total_op_num * 2
    for t in range (0,trans):
        trans_type = random_pick([0,1,2],[wo_rate,ro_rate,1-wo_rate-ro_rate])
        if trans_type == 0:
            for op in range (0,ops):
                variable = random.randint(0,var-1)
                counter += 1
                new_op = Operation(True,variable,counter)
                doc.write("write," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        elif trans_type == 1:
            for op in range (0,ops):
                variable = random.randint(0,var-1)
                new_op = Operation(False,variable,0)
                doc.write("read," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        elif trans_type == 2:
            w_count = 0
            r_count = 0
            for i in range (0,ops):
                op_type = random_pick([0,1],[wr_rate,1-wr_rate])
                if op_type == 0:
                    w_count += 1
                elif op_type == 1:
                    r_count += 1
                else:
                    print("Error in op_type!")
            for r in range(r_count):
                variable = random.randint(0,var-1)
                new_op = Operation(False,variable,0)
                doc.write("read," + str(new_op.variable) + "," + str(new_op.value)+"\n")
            for w in range(w_count):
                variable = random.randint(0,var-1)
                counter += 1
                new_op = Operation(True,variable,counter)
                doc.write("write," + str(new_op.variable) + "," + str(new_op.value)+"\n")
        else:
            print("Error in trans_type!")
    doc.close()


def random_pick(some_list, probabilities): 
    '''
    randon_pick([true,false],[0.5,0.5])
    '''
    x = random.uniform(0,1) 
    cumulative_probability = 0.0 
    for item, item_probability in zip(some_list, probabilities): 
        cumulative_probability += item_probability 
        if x < cumulative_probability:
               break 
    return item 


def generate_opt(hist_file, trans_num): 
    fo = open(hist_file, "r")
    list_line = []
    for line in fo.readlines():
        line = line.strip()                            
        list_line.append(line)
    fo.close()
    list_trans = []
    op_count=0
    for i in range(0,trans_num):
        temp_ops = []
        for j in range(0,operation_num):
            temp_ops.append(list_line[op_count])
            op_count += 1
        list_trans.append(temp_ops)
    return list_trans


def run_ops(list_of_ops, client_no):
    op_num = 0
    result_ops = []
    connect = mariadb.connect(host=server, user="root",password="123456")
    # Disable Auto-Commit
    connect.autocommit = False
    t_count = 0
    e_count = 0
    for i in range(len(list_of_ops)):
        if t_count > transaction_num:
            break
        cursor = connect.cursor()
        cursor.execute("START TRANSACTION;")
        temp_tx_op = []
        e_flag = False
        for j in range(len(list_of_ops[i])):
            op = str.split(list_of_ops[i][j],',',3)
            key = int(op[1])
            if(op[0] == 'write'):
                val = int(op[2])
                try:
                    cursor.execute("UPDATE maria.variables SET val=%d WHERE var=%d;" % (val,key))
                    single_op = 'w(' + str(key) + ',' + str(val) + ',' + str(client_no) + ',' + str(i) + ',' + str(op_num) + ')'
                except Exception as e:
                    single_op = 'w(' + str(key) + ',' + str(val) + ',' + str(client_no) + ',' + str(i) + ',' + str(op_num) + ')'
                    e_flag = True
            elif(op[0] == 'read'):
                try:
                    cursor.execute("SELECT val FROM maria.variables WHERE var=%d;" % key)
                    return_val = cursor.fetchall()
                    record_val = return_val[0][0]
                    single_op = 'r(' + str(key) + ',' + str(record_val) + ',' + str(client_no) + ',' + str(i) + ',' + str(op_num) + ')'
                except Exception as e:
                    single_op = 'r(' + str(key) + ',' + str(record_val) + ',' + str(client_no) + ',' + str(i) + ',' + str(op_num) + ')'
                    e_flag = True
            else:
                print("Unknown wrong type op: '%s'" % op[0])
            op_num += 1
            temp_tx_op.append(single_op)
            
        if e_flag == True:
            cursor.execute("ROLLBACK;")
        else:
            try:
                cursor.execute("COMMIT;")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                e_flag = True
        connect.commit()
        if e_flag == False:
            t_count += 1
            result_ops.append(temp_tx_op)
        else:
            e_count += 1
    cursor.close()
    connect.close()
    if t_count < transaction_num:
        print("UNFINISH")
    return result_ops, e_count

def write_result(result,file_path, error_num):
    '''
        result_single_history is a three dimensional list
        file is the output path
    '''
    f=open(file_path,"w")
    for n_trans in range(len(result)-1):
        for n_ops in range(len(result[0])):
            f.write(result[n_trans][n_ops]+'\n')
    f.close()
    print(file_path + ' is completed, contain error: ', error_num)


def run_thread(id):
    client = int(id)
    zipf_generator(hist_folder, client, 4*transaction_num, operation_num, key_num)
    file_path = hist_folder + "hist_" + str(client) + ".txt"
    hist_list = generate_opt(file_path, 4*transaction_num)
    result_list, error_num = run_ops(hist_list,client)
    result_path = folder_name + "result_" + str(client) + ".txt"
    write_result(result_list, result_path, error_num)


if __name__ == '__main__':
    threads =[]
    tlock=threading.Lock()
    os.makedirs(folder_name, exist_ok=True)
    os.makedirs(hist_folder, exist_ok=True)
    for i in range(threads_num):
        thread = myThread(i)
        threads.append(thread)

    for i in range(threads_num):
        threads[i].start()
