import argparse
import torch
import logging
import time

from torch import distributed as dist

DEVICE = "cpu"
TENSOR_SIZE = 1024
# world size - no. of processes participating in the job i.e. max rank value (+1 if 0 initialized, which I think it is based on the code).
def init_process(master_ip, rank, world_size):
    dist.init_process_group(backend="gloo",
                            init_method="tcp://" + master_ip + ":6585",
                            rank=rank,
                            world_size=world_size)


def main():
    # Create a random tensor 1 dimensional
    t = torch.rand(TENSOR_SIZE)
    # Send the tensor to rank 0
    if dist.get_rank() == 0:
        # Recv tensors from all ranks in an array
        recv_buffers = [torch.zeros(TENSOR_SIZE) for i in range(1, dist.get_world_size())]
        for i in range(1, dist.get_world_size()):
            s = time.time()
            dist.recv(recv_buffers[i-1], src=i)
            e = time.time()
            print("Finished recv from ", i, " in ", e-s, " seconds")
    else:
        dist.send(t, dst=0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ip", "-m", required=True, type=str)
    parser.add_argument("--num-nodes", "-n", required=True, type=int)
    parser.add_argument("--rank", "-r", required=True, type=int)

    args = parser.parse_args()
    init_process(master_ip=args.master_ip,
                 rank=args.rank,
                 world_size=args.num_nodes)
    main()
