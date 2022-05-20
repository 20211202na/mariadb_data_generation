# Checking Repeatable Read Consistency for MariaDB


```
MariaDB version == 10.4.22
```
Parameters:
```
key_num = 20
client_num = 10
transactions_per_client = 100
operations_per_transaction = 25
```
Requirements:
```
pip3 install mariadb==1.0.11
```

# Running Steps

### 1. Run [setup_server.sh](./setup_server.sh) on server node.
Make sure to change the `client_ip_address` in line 15 to grant access for client node.
```
bash setup_server.sh
```
### 2. Run [setup_client.sh](./setup_client.sh) on client node.
```
bash setup_client.sh <server_ip_address, e.g., 155.155.155.155>
```
### 2. Run [init.sh](./init.sh) to initialize the Database in MariaDB.

Need to change the parameter `key` if you want to customize the key number.
```
python3 init.py <server_ip_address, e.g., 155.155.155.155>
```
### 3. Run [maria.py](./maria.py) to generate transaction workloads. 

Please make sure the `key_num` is same with settings in `init.py`. Then run
```
python3 maria.py -s <server_id> -w <wo_rate> -r <ro_rate> -p <w_percent> -t <trans_num> -o <op_num> -c <client_num> -n <thread_no> -f <folder_num>
```
With the original parameters:
```
python3 maria.py -s <server_ip_address, e.g., 155.155.155.155>
```
The collected traces will be stored in folder `output/folder_num/` where the trace for each client will be stored in a separate txt file; The default `folder_num` is 0.

To be noticed, all the read-write transactions generated by this script has been customized, that is, for each transaction, all the read operations will happen before write operations. This part can be modified in function `zipf_generator` and `uniform_generator`.

### 4. Run [group_data.py](./group_data.py) to normalize the collected data into one file result.txt.
```
python3 group_data.py -o <operation_num, e.g., 25> -r <running_times>
```
The parameter `running_times` refers to running_times in [run.sh](./run.sh).

### 5. Run [check_rr.py](./check_rr.py) to check if the execution run violates Repeatable Read consistency.

The format of each operation is: `read/write(variable, value, client_id, transaction_id)`, denote as `r/w(var, val, cid, tid)`
* RR Property:

    For multiple Read operations in the same transaction, `r(var, val_1, cid, tid)` and `r(var, val_2, cid, tid)`, if there is no Write operation to `var` between them, then `val_1 = val_2`.
  
### (Optional) Run [run.sh](./run.sh) to automatically generate workloads and results.
```
bash run.sh <server_ip_address, e.g., 155.155.155.155> <running_times, e.g., 300>
```
