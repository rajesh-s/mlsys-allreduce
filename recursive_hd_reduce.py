import argparse
import torch
import logging
import time
import copy

from torch import distributed as dist

DEVICE = "cpu"
#TENSOR_SIZE = 4

def init_process(master_ip, rank, world_size):
    dist.init_process_group(backend="gloo",
                            init_method="tcp://" + master_ip + ":6585",
                            rank=rank,
                            world_size=world_size)

def main(rank, num_nodes, tensor_size):
    # Create a random tensor
    tensor = torch.rand(tensor_size)
    #tensor = torch.arange(TENSOR_SIZE) # TBD: Easier to test with regular integers t = torch.rand(TENSOR_SIZE)
    #tensor = torch.tensor([0,1,2,3])
    s = time.time()
    #print("Split Tensor:",split_tensor)
    #for j in range(len(split_tensor)):
    #print("Rank",rank,"Before",tensor)
    bde_reduce_scatter(rank, tensor, 0, len(tensor)-1, 0, num_nodes-1) # rank-1, rank+1)
    #split_tensor = list(torch.split(tensor, int(tensor_size/num_nodes))) # Split tensor into chunks based on number of participating nodes
    #print("Rank",rank,"After Reduce Scatter",tensor)
    bde_all_gather(rank, tensor, 0, len(tensor)-1, 0 , num_nodes-1)
    #print("Rank",rank,"After All Gather",tensor)
    #split_tensor[rank] = bde_reduce_scatter(rank, tensor, 0, len(tensor)-1, 0, num_nodes-1) # rank-1, rank+1)
    #print("x[",rank,"] = ",split_tensor[rank])
    e = time.time()
    print("Rank",rank,"finished BDE all reduce in ", e-s, " seconds")

# BDE Reduce-Scatter

def bde_reduce_scatter(rank, x, tensor_left, tensor_right, rank_left, rank_right):
    #print("Rank",rank,"x",x,"tensor_left",tensor_left,"tensor_right",tensor_right,"rank_left",rank_left,"rank_right",rank_right)
    #print("Rank:",rank)
    if rank_left == rank_right:
        #val = x[(rank * TENSOR_SIZE)//dist.get_world_size():((rank + 1)*TENSOR_SIZE//dist.get_world_size())]
        return
    rank_size = rank_right - rank_left + 1
    tensor_size = tensor_right - tensor_left + 1
    tensor_mid = (tensor_left + tensor_right) // 2
    rank_mid = (rank_left + rank_right) // 2
    if rank <= rank_mid:
        partner = rank + (rank_size/2)
    else:
        partner = rank - (rank_size/2)
    partner = int(partner)
    #print("Partner of",rank,"is",partner)
    if rank <= rank_mid:
        #print("Rank",rank,"is sending",x[tensor_mid+1:tensor_right+1],"of len",len(x[tensor_mid+1:tensor_right+1]))
        dist.send(x[tensor_mid+1:tensor_right+1], dst=partner)
        #print("Rank",rank,"Sending",x[tensor_mid+1:tensor_right+1])
        recv_buffer =  copy.deepcopy(x[tensor_left:tensor_mid+1]) #torch.zeros(len(x[tensor_left:tensor_mid+1]))
        dist.recv(recv_buffer, src=partner)
        #print("Rank",rank,"Recv Buf",recv_buffer)
        x[tensor_left:tensor_mid+1] = x[tensor_left:tensor_mid+1] + recv_buffer
    else:
        recv_buffer = copy.deepcopy(x[tensor_mid+1:tensor_right+1]) #torch.zeros(len(x[tensor_mid+1:tensor_right+1]))
        #print("Rank",rank,"is expected to receive len",len(x[tensor_mid+1:tensor_right+1]))
        dist.recv(recv_buffer, src=partner)
        #print("Rank",rank,"Recv Buf",recv_buffer)
        x[tensor_mid+1:tensor_right+1] = x[tensor_mid+1:tensor_right+1] + recv_buffer
        dist.send(x[tensor_left:tensor_mid+1], dst=partner)
        #print("Rank",rank,"Sending",x[tensor_left:tensor_mid+1])

    if rank <= rank_mid:
        bde_reduce_scatter(rank, x, tensor_left, tensor_mid, rank_left, rank_mid)
    else:
        bde_reduce_scatter(rank, x, tensor_mid+1, tensor_right, rank_mid+1, rank_right)

# BDE AllGather

def bde_all_gather(rank, x, tensor_left, tensor_right, rank_left, rank_right):
    #print("Rank",rank,"x",x,"tensor_left",tensor_left,"tensor_right",tensor_right,"rank_left",rank_left,"rank_right",rank_right)
    if rank_left == rank_right:
        return

    rank_size = rank_right - rank_left + 1
    tensor_size = tensor_right - tensor_left +1
    tensor_mid = (tensor_left + tensor_right) // 2
    rank_mid = (rank_left + rank_right) // 2

    if rank <= rank_mid:
        partner = rank + (rank_size/2)
    else:
        partner = rank - (rank_size/2)
    partner = int(partner)

    if rank <= rank_mid:
        bde_all_gather(rank, x, tensor_left, tensor_mid, rank_left, rank_mid)
    else:
        bde_all_gather(rank, x, tensor_mid+1, tensor_right, rank_mid+1, rank_right)

    if rank <= rank_mid:
        #print("Rank",rank,"sending",x[tensor_left:tensor_mid+1],"from",x)
        dist.send(x[tensor_left:tensor_mid+1], dst=partner)
        recv_buffer =  x[tensor_mid+1:tensor_right+1]
        dist.recv(recv_buffer, src=partner)
        #print("Rank",rank,"receiving",recv_buffer)
    else:
        recv_buffer = x[tensor_left:tensor_mid+1]
        dist.recv(recv_buffer, src=partner)
        #print("Rank",rank,"receiving",recv_buffer)
        #print("Rank",rank,"sending",x[tensor_left:tensor_mid+1],"from",x)
        dist.send(x[tensor_mid+1:tensor_right+1], dst=partner)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ip", "-m", required=True, type=str)
    parser.add_argument("--num-nodes", "-n", required=True, type=int)
    parser.add_argument("--rank", "-r", required=True, type=int)
    parser.add_argument("--tensor-size", "-t", required=True, type=int)


    args = parser.parse_args()
    #print("Rank",args.rank,"entered main")
    init_process(master_ip=args.master_ip,
                 rank=args.rank,
                 world_size=args.num_nodes)
    main(rank=args.rank, num_nodes=args.num_nodes, tensor_size=args.tensor_size)
