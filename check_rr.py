'''
The format of each operation is: read/write(variable, value, client_id, transaction_id), denote as r/w(var, val, cid, tid)
RR Property:
    For multiple Read operations in the same transaction, r(var, val_1, cid, tid) and r(var, val_2, cid, tid), if there is no Write operation to var between them, then val_1 = val_2.
'''

import copy

run_num = sys.argv[1]

class RRChecker:
    def __init__(self, ops):
        self.txns = {}
        self.r_nodes = {}
        current_tra = []
        for i in range(len(ops)):
            op_dict = self.get_op(ops[i])
            if i == len(ops) - 1 or self.get_op(ops[i + 1])['tra_id'] != op_dict['tra_id']:
                current_tra.append(op_dict)
                for op in current_tra:
                    if op['op_type'] == 'r':
                        if op['var'] not in self.r_nodes:
                            self.r_nodes[op['var']] = set()
                        self.r_nodes[op['var']].add(op_dict['tra_id'])
                if op_dict['tra_id'] not in self.txns:
                    self.txns[op_dict['tra_id']] = []
                self.txns[op_dict['tra_id']].extend(current_tra.copy())
                current_tra.clear()
            else:
                current_tra.append(op_dict)

    def get_op(self, op):
        op = op.strip('\n')
        arr = op[2:-1].split(',')
        return {
            'op_type': op[0],
            'var': arr[0],
            'val': arr[1],
            'client_id': int(arr[2]),
            'tra_id': int(arr[3]),
        }

    def check_repeatable_read(self,i):
        rr_violation = []
        for var,r_t_set in self.r_nodes.items():
            for r_tra_id in r_t_set:
                bef_r = False
                bef_w = False
                for r_op in self.txns[r_tra_id]:
                    if r_op['var'] == var and r_op['op_type'] == 'r':
                        if bef_w == False and bef_r == True:
                            if r_op['val'] != r_bef_op['val']:
                                e_txn = {'var': r_op['var'], 'old_val': r_bef_op['val'], 'new_val': r_op['val'], 'tra_id': r_op['tra_id']}
                                rr_violation.append(e_txn)
                                file = open('output/'+str(i)+'/rr_violation.txt','a');
                                file.write('( var: ' + str(e_txn['var']) + ', old_val: ' + str(e_txn['old_val']) + ', new_val: ' + str(e_txn['new_val']) + ', tra_id: ' + str(e_txn['tra_id']) + ')\n')
                                file.close();
                        bef_r = True
                        bef_w = False 
                        r_bef_op = r_op
                    elif r_op['var'] == var and r_op['op_type'] == 'w':
                        bef_w = True
        return rr_violation      


if __name__ == '__main__':
    for i in range(int(run_num)):
        folder_name = "output/"+str(i)+"/result.txt"
        with open(folder_name) as in_file:
            raw_ops = in_file.readlines()

        causal_hist = RRChecker(raw_ops)
        rr_violation = causal_hist.check_repeatable_read(i)
        if rr_violation != []:
            print('find RR violation in trace: ' + str(i))
