# Assignment 2: Collective Communication

## Background

**Environment:**

-   We will be using NSF CloudLab for this assignment. If you don't have a Cloudlab account, please visit [http://cloudlab.us (Links to an external site.)](http://cloudlab.us) and create an account using your Wisconsin email address as login. Click on Join Existing Project and enter  [(Links to an external site.)](https://www.cloudlab.us/signup.php?pid=UWMadison744-F20)**UWMadison839Sp22** as the project name. Then click on Submit Request. The project leader will approve your request. 
-   If you already have a CloudLab account, simply request to join the **UWMadison839Sp22** project.
-   We have created a 4 machine profile for this assignment, where every machine hosts 4VMs leading to 16VMs per group. We have reserved 48 c220g5 nodes at Wisconsin for this assignment from 03/25/22 at 10am to 04/03/22 at 6pm.
-   **For every group, please launch only one active experiment at a time.**

**Setup:**

Once the machines have started, install Python3, pip, numpy and PyTorch on every VM.

1.  sudo apt-get update --fix-missing
2.  sudo apt install python-pip3
3.  pip3 install numpy 
4.  pip3 install torch==1.4.0+cpu -f https://download.pytorch.org/whl/torch\_stable.html

You can use tools like **parallel-ssh** to do this in parallel across all nodes. 

**Background reading**

-   The core of this assignment involves implementing AllReduce on PyTorch using two strategies and measuring their performance characteristics. 
-   The two algorithms you will implement are Ring allreduce and Recursive halving/doubling. Please see [https://www.cs.utexas.edu/~pingali/CSE392/2011sp/lectures/Conc\_Comp.pdf (Links to an external site.)](https://www.cs.utexas.edu/~pingali/CSE392/2011sp/lectures/Conc_Comp.pdf) for description of the algorithms and their performance bounds.
-   To implement the methods you will use simple **send**, **recv** functions that are implemented in the PyTorch distributed module. Please see https://pytorch.org/docs/stable/distributed.html for details.
-   We have created a sample file that shows how you can use **send, recv** and launch a distributed PyTorch program at [https://gist.github.com/shivaram/9fb652d5548b58b3cfa49636fce89b1d (Links to an external site.)](https://gist.github.com/shivaram/9fb652d5548b58b3cfa49636fce89b1d)

**Tasks**

There are four main tasks that you will need to perform for this assignment. 

-   Task 1: Implement AllReduce using two algorithms:

-   (a) “Ring” AllReduce algorithm 
-   (b) Recursive Halving and Doubling algorithm

In both cases, the input should be a random vector on every machine and the output on each machine should be the sum of all the input vectors.  The vector size should be configurable on the command line

-   Task 2: Vary the size of the vector used from 1KB to 100MB and measure the time taken for AllReduce across 16 VMs. Report how the time taken varies and analyze the performance you observe.

-   Task 3: Consider a fixed vector size of 10MB and vary the number of VMs used from 2, 4, 8, 16. Analyze your results with respect to theoretical bounds that have been established in the papers we discussed in class.
-   Task 4: The performance model we discussed in class has terms for latency (alpha) and bandwidth (beta). Try to calculate the values for alpha and beta for the default CloudLab network based on your performance measurements and the theoretical bounds.
-   \[Extra Credit\]: Task 5: Optionally, change the network bandwidth to 100 mbps for each VM using Wondershaper ([https://github.com/magnific0/wondershaper/blob/master/wondershaper (Links to an external site.)](https://github.com/magnific0/wondershaper/blob/master/wondershaper)) – Repeat experiments in Task 3 and report on how the values of alpha and beta change. 

**Deliverables**

-   Source code: Your source code should be in two Python files; one for ring allreduce and the other for recursive halving & doubling. 

-   Summarize your observations for Task 2, 3, 4 in a report up to 3 pages in length. You can use additional pages for tables, figures or any other supporting data.
-   At the end of the report, please include a short section on contributions from each student in the group.
-   Create a zip file with both of the above and upload to Canvas.

## Setup

- Install the pytorch packages that he mentioned on all nodes
- Able to ssh from node0 to all other nodes
- Generated keys on all the nodes and added the public keys to authorized_keys on all nodes. This means we should be able to ssh from one node to any other node
- main.py should be present on all nodes
