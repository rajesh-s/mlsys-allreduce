## Could you discuss other implications from Figure 7?  Why Ring is faster at smaller number of nodes, but slower later?

There are two possible reasons for the observed behavior of “Ring is faster at smaller number of nodes, but slower):
1.	Ring-AllReduce has more steps involved which adds to latency overhead and underutilize link throughput utilization
a.	Number of steps in Ring AllReduce is proportional to 2*(N-1) where N is the number of nodes. N-1 iteration to perform the summation and N-1 to send the values across nodes. Considering the case of N=4, we have 6 exchanges for Ring
b.	When N=4, at any point of time, ring is only sending/receiving a single piece of the tensor at a time. However, in the first step of recursive halving and the second step of recursive doubling two pieces of the tensor are sent/received.  We have 4 exchanges for BDE as illustrated below
 ![image](https://user-images.githubusercontent.com/35628747/188863775-f9b553c8-6d08-493e-a947-f2ef7ac71838.png)
c.	The 2 extra steps in Ring (i) add to latency cost and (ii)exacerbates the issue of underutilized link throughput. Our intuition is that the underutilization grows as the pieces of tensor get smaller due to more workers making Ring slower than BDE beyond a certain value.
2.	Slight instrumentation differences between BDE and Ring implementation
a.	Ashwin implemented Ring with two separate functions. One for summation and other for transfer. Only the network function was instrumented in the time measurements.
b.	Rajesh implemented BDE in a single function. The measured time included the summation along with the transfer (highlighted in image below). Since we worked on this independently, we realized this during analysis instead of data collection. At the time, we thought it may be a negligible difference, but we did not have access to machines to run the set of experiments with same instrumentation strategy for both.
 ![image](https://user-images.githubusercontent.com/35628747/188863799-264d67fb-6545-4988-bf17-df47c279c3d2.png)


## Not sure I followed how you computed alpha and beta. Did you plugin the values you got from varying vector size into the theoretical bounds from the paper?

I computed alpha and beta using the theoretical bounds/formulae in the paper. Cost is proportional to alpha + n * beta, so I figured the cost associated with alpha would more or less be a constant regardless of data size (or was it number of nodes? I'm pretty sure it was size of data - change this sentence if it was no. Of nodes), while beta would vary. Thus, I figured we could subtract the total time spent on two runs to get eliminate the cost associated with alpha, get the cost associated with beta, then ind alpha. However, both alpha and beta seemed to not be constants, so I wasn't sure if they were also varying with vector size or some other factors, and tried to indicate that in the report.

## Not sure I follow the reasoning for why BW throttling didn't make a difference. Did you see a difference at a larger vector size?

We did not think of trying larger vector sizes at the time. We thought the prompt was specifically asking us to contrast it with the 10MB case from Task 3. In hindsight, we should have attempted it to validate our reasoning stated in the report that “…no single interface reaches the set limit for throughput with splits of 80Mb tensor over a 100Mb/s interface”.
