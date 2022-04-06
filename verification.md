t = torch.rand(1024)
print(t[1].dtype) # torch.float32

- Default size 1024 * 4B = 4096B = 4KB
- Task1: Vary TENSOR_SIZE from 256 (1KB) to 26214400 (100MB). Measure time.
- Task2: Set TENSOR_SIZE to 2621440 (10MB). Vary world_size for 2,4,8,16 Measure time.
- Task3: How do we measure bandwidth?

- No information 

Recursive halving/doubling relies on bidirectional exchange between a pair of nodes.

- Output of BDE Reduce Scatter:

```bash
node0:~/allreduce-839> ./run_bde.sh
4
4
Staring rank 1
Staring rank 2
Staring rank 3

Rank 0 Before tensor([0, 1, 2, 3])
Rank 1 After tensor([16, 28,  6,  7])

Rank 2 Before tensor([ 8,  9, 10, 11])
Rank 2 After tensor([ 8,  9, 32, 14])

Rank 3 Before tensor([12, 13, 14, 15])
Rank 3 After tensor([12, 13, 20, 36])

Rank 0 After tensor([24, 10,  2,  3])
Rank 1 Before tensor([4, 5, 6, 7])
```

Output of All Gather
```bash
Rank 0 Before tensor([0, 1, 2, 3])
Rank 0 After Reduce Scatter tensor([24, 10,  2,  3])
Rank 0 After All Gather tensor([24, 28, 32, 36])
Rank 3 Before tensor([12, 13, 14, 15])
Rank 3 After Reduce Scatter tensor([12, 13, 20, 36])
Rank 3 After All Gather tensor([24, 28, 32, 36])
Rank 1 Before tensor([4, 5, 6, 7])
Rank 1 After Reduce Scatter tensor([16, 28,  6,  7])
Rank 1 After All Gather tensor([24, 28, 32, 36])
Rank 2 Before tensor([ 8,  9, 10, 11])
Rank 2 After Reduce Scatter tensor([ 8,  9, 32, 14])
Rank 2 After All Gather tensor([24, 28, 32, 36])
```

cd wondershaper && sudo ./wondershaper -a eth1 -d 102400 -u 102400

cd wondershaper && sudo ./wondershaper -a eth1 -c