#!/bin/bash

# Assumes node0 is at IP 10.10.1.1
# Assumes worker nodes have hostname node1, node2, ... node15
# Assumes you can ssh from node0 to all the other nodes.

python3 main.py --master-ip 10.10.1.1 --num-nodes 16 --rank 0 &

for i in `seq 1 15`
do
        RANK=$i
        echo "Staring rank $RANK"
        ssh -f node$i "nohup python3 main.py --master-ip 10.10.1.1 --num-nodes 16 --rank $RANK"
done
