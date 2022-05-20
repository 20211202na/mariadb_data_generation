#!/bin/bash

server=$1
run_num=$2

for ((j=0;j<$run_num;j++));do
{
    python3 maria.py -f ${j}
    wait
    python3 init.py $server
}
done

python3 group_data.py $run_num
wait
python3 check_rr.py $run_num
