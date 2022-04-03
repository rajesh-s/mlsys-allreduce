#!/bin/bash

# Assumes node0 is at IP 10.10.1.1
# Assumes worker nodes have hostname node1, node2, ... node15
# Assumes you can ssh from node0 to all the other nodes.

num_nodes=16
tensor_size=1024

while getopts ":hn:t:" arg; do
        case $arg in
                h)
                        echo "Usage: $0 -n total_no_of_nodes -t tensor_size"
                        exit 0;
                        ;;
                n) # Specify number of nodes
                        num_nodes=${OPTARG};;
                t) # Specify size of tensor
                        tensor_size=${OPTARG};;
                *)
                        echo "Usage: $0 -n total_no_of_nodes -t tensor_size"
                        exit 1;
                        ;;
        esac
done

echo $num_nodes
echo $tensor_size
python3 ring_allreduce.py --master-ip 10.10.1.1 --num-nodes $num_nodes --rank 0 --tensor-size $tensor_size &

for i in `seq 1 $(($num_nodes - 1))`
do
        RANK=$i
        echo "Staring rank $RANK"
        ssh -f node$i "nohup python3 ring_allreduce.py --master-ip 10.10.1.1 --num-nodes $num_nodes --rank $RANK --tensor-size $tensor_size"
done
