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

def main(rank, tensor_size):
    # Create a random tensor
    t = torch.rand(tensor_size)
    send_buffers = [torch.zeros(tensor_size) for i in range(0, dist.get_world_size())]
    recv_buffers = [torch.zeros(tensor_size) for i in range(1, dist.get_world_size())]
    send_buffers[0] = t
    s = time.time()
    for i in range(1, dist.get_world_size()):
        if (rank % 2) == 0:
            # Send a tensor to the next machine
            dist.send(send_buffers[i-1], dst=(dist.get_rank() + 1) % dist.get_world_size())

            # Receive a tensor from the previous machine
            dist.recv(recv_buffers[i-1], src=(dist.get_rank() + dist.get_world_size() - 1) % dist.get_world_size())
        else:
            # Receive a tensor from the previous machine
            dist.recv(recv_buffers[i-1], src=(dist.get_rank() + dist.get_world_size() - 1) % dist.get_world_size())

            # Send a tensor to the next machine
            dist.send(send_buffers[i-1], dst=(dist.get_rank() + 1) % dist.get_world_size())


        # Update send buffer values
        send_buffers[i] = recv_buffers[i-1]
        # Accumulate value in t. At the end of the for loop, t will hold the reduced value
        t += recv_buffers[i-1]
    e = time.time()
    print("Finished allreduce in ", e-s, " seconds")
    #print(recv_buffers)
    #print(t)

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
    main(rank=args.rank, tensor_size=args.tensor_size)
