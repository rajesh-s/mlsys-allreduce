import argparse
import torch
import logging
import time

from torch import distributed as dist

DEVICE = "cpu"
#TENSOR_SIZE = 1024

def init_process(master_ip, rank, world_size):
    dist.init_process_group(backend="gloo",
                            init_method="tcp://" + master_ip + ":6585",
                            rank=rank,
                            world_size=world_size)

def main(tensor_size):
    # Get world size and rank
    world_size = dist.get_world_size()
    rank = dist.get_rank()
    # Create a random tensor
    t = torch.rand(tensor_size)
    t = list(t.split(int(tensor_size/world_size)))
    #print(len(t))
    #print(tensor_size)
    #print(world_size)
    #print(t)
    # Create send and receive buffers
    zero_buffer = torch.zeros(tensor_size)
    recv_buffers = list(zero_buffer.split(int(tensor_size/world_size)))
    #s = time.time()
    # Reduce-scatter loop
    for i in range(1, world_size):
        if (rank % 2) == 0:
            # Send a tensor to the previous machine
            #print((rank + i) % world_size)
            dist.send(t[(rank + i) % world_size], dst=(rank + world_size - 1) % world_size)

            # Receive a tensor from the next machine
            dist.recv(recv_buffers[i-1], src=(rank + 1) % world_size)
        else:
            # Receive a tensor from the next machine
            dist.recv(recv_buffers[i-1], src=(rank + 1) % world_size)

            # Send a tensor to the previous machine
            dist.send(t[(rank + i) % world_size], dst=(rank + world_size - 1) % world_size)
        # Accumulate value in t. At the end of the for loop, t will hold the reduced value
        t[(rank + i + 1) % world_size] += recv_buffers[i-1]
    # All-gather loop
    for i in range(1, world_size):
        if (rank % 2) == 0:
            # Send a tensor to the next machine
            dist.send(t[(rank + 1 - i + world_size) % world_size], dst=(rank + 1) % world_size)

            # Receive a tensor from the previous machine
            dist.recv(t[(rank - i + world_size) % world_size], src=(rank + world_size - 1) % world_size)
            else:
            # Receive a tensor from the previous machine
            dist.recv(t[(rank - i + world_size) % world_size], src=(rank + world_size - 1) % world_size)

            # Send a tensor to the next machine
            dist.send(t[(rank + 1 - i + world_size) % world_size], dst=(rank + 1) % world_size)
    #e = time.time()
    #print("Finished allreduce in ", e-s, " seconds")
    #print(recv_buffers)
    print(torch.cat(t))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ip", "-m", required=True, type=str)
    parser.add_argument("--num-nodes", "-n", required=True, type=int)
    parser.add_argument("--rank", "-r", required=True, type=int)
    parser.add_argument("--tensor-size", "-t", required=True, type=int)

    args = parser.parse_args()
    init_process(master_ip=args.master_ip,
                 rank=args.rank,
                 world_size=args.num_nodes)
    main(tensor_size=args.tensor_size)
