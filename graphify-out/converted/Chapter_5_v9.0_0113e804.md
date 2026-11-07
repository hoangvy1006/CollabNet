<!-- converted from Chapter_5_v9.0.pdf -->

Computer Networking: A 
Top-Down Approach 
9th edition 
Jim Kurose, Keith Ross
Pearson, 2025
Chapter 5
Network Layer:
Control Plane
A note on the use of these PowerPoint slides:
We’re making these slides freely available to all (faculty, students, 
readers). They’re in PowerPoint form so you see the animations; and 
can add, modify, and delete slides  (including this one) and slide content 
to suit your needs. They obviously represent a lot of work on our part. 
In return for use, we only ask the following:
▪ If you use these slides (e.g., in a class) that you mention their 
source (after all, we’d like people to use our book!)
▪ If you post any slides on a www site, that you note that they are 
adapted from (or perhaps identical to) our slides, and note our 
copyright of this material.
For a revision history, see the slide note for this page. 
Thanks and enjoy!  JFK/KWR
     All material copyright 1996-2025
     J.F Kurose and K.W. Ross, All Rights Reserved

Network layer control plane: our goals
▪understand principles 
behind network control 
plane:
• traditional routing algorithms
• SDN controllers
• network management, 
configuration
▪ instantiation, implementation 
in the Internet:
• OSPF, BGP
• OpenFlow, ODL and ONOS 
controllers
• Internet Control Message 
Protocol: ICMP
• SNMP , YANG/NETCONF
Network Layer: 5-2
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ link state
▪ distance vector
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-3

Two approaches to structuring network control plane:
▪ per-router control (traditional)
▪ logically centralized control (software defined networking)
Network-layer functions
Network Layer: 5-4
▪ forwarding: move packets from router’s 
input to appropriate router output data plane
control plane▪ routing: determine route taken by packets from source to destination
Per-router control plane
Individual routing algorithm components in each and every 
router interact in the control plane
Routing
Algorithm
data
plane
control
plane
1
2
0111
values in arriving 
packet header
3
Network Layer: 5-5
Software-Defined Networking (SDN) control plane
Remote controller computes, installs forwarding tables in routers
data
plane
control
plane
Remote Controller
CA
CA CA CA CA
1
2
0111
3
values in arriving 
packet header
Network Layer: 5-6
Per-router 
control plane SDN control plane
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ link state
▪ distance vector
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-8

Routing protocol goal: determine 
“good” paths (equivalently, routes), 
from sending hosts to receiving host, 
through network of routers
▪ path: sequence of routers packets 
traverse from given initial source host 
to final destination host
▪ “good”: least “cost”, “fastest”, “least 
congested”
▪ routing: a “top-10” networking 
challenge!
Routing protocols
mobile network
enterprise
          network
national or global ISP
datacenter 
network
application
transport
network
link
physical
application
transport
network
link
physical
network
link
physical
network
link
physical
network
link
physical
network
link
physical
 network
link
physical
Network Layer: 5-9
Graph abstraction: link costs
Network Layer: 5-10
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
graph: G = (N,E)
ca,b: cost of direct link connecting a and b
             e.g., cw,z = 5, cu,z = ∞
cost defined by network operator: 
could always be 1, or inversely related 
to bandwidth, or inversely related to 
congestion
N: set of routers = { u, v, w, x, y, z }
E: set of links ={ (u,v), (u,x), (v,x), (v,w), (x,w), (x,y), (w,y), (w,z), (y,z) }
Routing algorithm classification
Network Layer: 5-11global or decentralized information?
global: all routers have complete 
topology, link cost info
• “link state” algorithms
decentralized: iterative process of 
computation, exchange of info with neighbors
• routers initially only know link costs to 
attached neighbors
• “distance vector” algorithms
How fast 
do routes 
change?
dynamic: routes change 
more quickly
• periodic updates or in 
response to link cost 
changes
static: routes change 
slowly over time
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ link state
▪ distance vector
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-12

Dijkstra’s link-state routing algorithm
Network Layer: 5-13
▪ centralized: network topology, link 
costs known to all nodes
• accomplished via “link state 
broadcast” 
• all nodes have same info
▪ computes least cost paths from one 
node (“source”) to all other nodes
• gives forwarding table for that node
▪ iterative: after k iterations, know 
least cost path to k destinations
▪ cx,y: direct link cost from node x to y;  = ∞ if not direct 
neighbors
▪ D(v): current estimate of cost 
of least-cost-path from source 
to destination v
▪ p(v): predecessor node along 
path from source to v
▪ N': set of nodes whose least-
cost-path definitively known
notation
Dijkstra’s link-state routing algorithm
Network Layer: 5-14
1  Initialization: 
2   N' = {u}                               /* compute least cost path from u to all other nodes */
3    for all nodes v 
4      if v adjacent to u            /* u initially knows direct-path-cost only to  direct neighbors    */
5          then D(v) = cu,v      /* but may not be minimum cost!                                                    */
6      else D(v) = ∞ 
7 
8   Loop 
9     
10    
11
12
13
14
15  until all nodes in N' 
find w not in N' such that D(w) is a minimum 
add w to N' 
update D(v) for all v adjacent to w and not in N' : 
     D(v) = min ( D(v),  D(w) + cw,v  ) 
/* new least-path-cost to v is either old least-cost-path to v or known 
least-cost-path to w plus direct-cost from w to v */ 
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
D(w),p(w)
D(w),p(w)
5,u
4,x
3,y
3,y
5,u ∞∞1,u2,uu
v w x y z
Initialization (step 0): 
      For all a: if a adjacent to u then D(a) = cu,a 
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
D(w),p(w)
5,u
4,x
3,y
3,y
5,u ∞∞1,u2,uu
8   Loop 
9     
10    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
D(w),p(w)
5,u
4,x
3,y
3,y
5,u ∞∞1,u2,uu
8   Loop 
9     
10
11    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
update D(b) for all b adjacent to a and not in N' : 
     D(b) = min ( D(b), D(a) + ca,b ) 
∞2,x4,x2,u
D(v) = min ( D(v), D(x) + cx,v ) = min(2, 1+2) = 2 
D(w) = min ( D(w), D(x) + cx,w ) = min (5, 1+3) = 4 
D(y) = min ( D(y), D(x) + cx,y ) = min(inf,1+1) = 2  

Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
D(w),p(w)
5,u
4,x
3,y
3,y
5,u ∞∞1,u2,uu
8   Loop 
9     
10
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
11
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy
update D(b) for all b adjacent to a and not in N' : 
     D(b) = min ( D(b), D(a) + ca,b ) 
4,y3,y2,u
D(w) = min ( D(w), D(y) + cy,w ) = min (4, 2+1) = 3 
D(z) = min ( D(z), D(y) + cy,z ) = min(inf,2+2) = 4  

Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv
update D(b) for all b adjacent to a and not in N' : 
     D(b) = min ( D(b), D(a) + ca,b ) 
D(w) = min ( D(w), D(v) + cv,w ) = min (3, 2+3) = 3 
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
11
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv 4,y3,y
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv 4,y3,y
uxyvw
update D(b) for all b adjacent to a and not in N' : 
     D(b) = min ( D(b), D(a) + ca,b ) 
D(z) = min ( D(z), D(w) + cw,z ) = min (4, 3+5) = 4 
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
11
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv 4,y3,y
uxyvw 4,y
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv 4,y3,y
uxyvw 4,y
uxyvwz
Dijkstra’s algorithm: an example
Step
0
1
2
3
4
5
N' D(v),p(v) D(x),p(x) D(y),p(y) D(z),p(z)D(w),p(w)
5,u ∞∞1,u2,uu
8   Loop 
9     
10
11
    
 find a not in N' such that D(a) is a minimum 
 add a to N' 
ux
v w x y z
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
∞2,x4,x2,u
uxy 4,y3,y2,u
uxyv 4,y3,y
uxyvw 4,y
uxyvwz
update D(b) for all b adjacent to a and not in N' : 
     D(b) = min ( D(b), D(a) + ca,b ) 
Dijkstra’s algorithm: an example
Network Layer: 5-27
u
yx
wv
z
2
2
1
3
1
1
2
5
3
5
D(w),p(w)
5,u
4,x
3,y
3,y
u
yx
wv
z
resulting least-cost-path tree from u: resulting forwarding table in u:
v
x
y
w
x
(u,v)
(u,x)
(u,x)
(u,x)
(u,x)
destination outgoing link
route from u to v directly
route from u to all 
other destinations 
via x 
Dijkstra’s algorithm: another example
Network Layer: 5-28
w3
4
v
x
u
5
3
7 4
y
8
z
2
7
9Step N' D(v), p(v)
0
1
2
3
4
5
D(w),
p(w)
D(x),
p(x)
D(y),
p(y)
D(z),
p(z)
u ∞ ∞ 7,u 3,u 5,u
uw ∞ 11,w 6,w 5,u
14,x 11,w 6,wuwx
uwxv 14,x 10,v 
uwxvy 12,y 
notes:
▪ construct least-cost-path tree by tracing predecessor nodes
▪ ties can exist (can be broken arbitrarily)
uwxvyz
v w x y z
Dijkstra’s algorithm: discussion
Network Layer: 5-29
algorithm complexity: n nodes
▪ each of n iteration: need to check all nodes, w, not in N
▪ n(n+1)/2 comparisons: O(n2) complexity
▪ more efficient implementations possible: O(nlogn)
message complexity: 
▪ each router must broadcast its link state information to other n routers 
▪ efficient (and interesting!) broadcast algorithms: O(n) link crossings to disseminate a 
broadcast message from one source
▪ each router’s message crosses O(n) links: overall message complexity: O(n2)
Dijkstra’s algorithm: oscillations possible
Network Layer: 5-30
▪ when  link costs depend on traffic volume, route oscillations possible
a
d
c
b
1 1+e
e0
e
1 1
0 0
initially
a
d
c
b
given these costs,
find new routing….
resulting in new costs
2+e 0
00
1+e 1
a
d
c
b
given these costs,
find new routing….
resulting in new costs
0 2+e
1+e1
0 0
a
d
c
b
given these costs,
find new routing….
resulting in new costs
2+e 0
00
1+e 1
▪ sample scenario:
• routing to destination a, traffic entering at d, c, e with rates 1, e (<1), 1
• link costs are directional, and volume-dependent
e
1 1
e
1 1
e
1 1
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ link state
▪ distance vector
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-31

Based on Bellman-Ford (BF) equation (dynamic programming):
Distance vector algorithm 
Network Layer: 5-32
Let Dx(y): cost of least-cost path from x to y.
Then:
   Dx(y) = minv { cx,v + Dv(y) }
   
Bellman-Ford equation
min taken over all neighbors v of x
v’s estimated least-cost-path cost to y
direct cost of link from x to v
Bellman-Ford Example
Network Layer: 5-33
u
y
z
2
2
1
3
1
1
2
5
3
5
Suppose that u’s neighboring nodes, x,v,w, know that for destination z:
Du(z) = min { cu,v + Dv(z),
                    cu,x + Dx(z),
                    cu,w + Dw(z) }
Bellman-Ford equation says:Dv(z) = 5
v
Dw(z) = 3
w
Dx(z) = 3
x
= min {2 + 5,
           1 + 3,
           5 + 3}  = 4
node achieving minimum (x) is 
next hop on estimated least-
cost path to destination (z)
Distance vector algorithm 
Network Layer: 5-34
key idea: 
▪ from time-to-time, each node sends its own distance vector estimate 
to neighbors
▪ under minor, natural conditions, the estimate Dx(y) converge to the actual least cost dx(y) 
Dx(y) ← minv{cx,v + Dv(y)}  for each node y ∊ N
▪ when x receives new DV estimate from any neighbor, it updates its 
own DV using B-F equation:
Distance vector algorithm:  
Network Layer: 5-35
iterative, asynchronous: each local 
iteration caused by: 
▪ local link cost change 
▪ DV update message from neighbor
wait for (change in local link 
cost or msg from neighbor)
each node:
distributed, self-stopping: each 
node notifies neighbors only when 
its DV changes
▪ neighbors then notify their 
neighbors – only if necessary
▪ no notification received, no 
actions taken!
recompute DV estimates using 
DV received from neighbor
if DV to any destination has 
changed, notify neighbors 
DV in a: 
Da(a)=0
Da(b) = 8
Da(c) = ∞
Da(d) = 1
Da(e) = ∞
Da(f) = ∞
Da(g) = ∞
Da(h) = ∞
Da(i) = ∞
Distance vector: example
Network Layer: 5-36
g h i
1 1
1 1 1
1 1
1 1
8 1
t=0
▪ All nodes have 
distance estimates 
to nearest 
neighbors (only)
A few asymmetries:
▪ missing link
▪ larger cost
d e f
a b c
▪ All nodes send 
their local 
distance vector to 
their neighbors
Distance vector example: iteration
Network Layer: 5-37
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=1
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
Distance vector example: iteration
Network Layer: 5-38
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=1
compute compute compute
compute compute compute
compute compute compute
Distance vector example: iteration
Network Layer: 5-39
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=1
Distance vector example: iteration
Network Layer: 5-40
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=2
Distance vector example: iteration
Network Layer: 5-41
g h i
1 1
1 1 1
1 1
8 1
2 1
d e f
a b c
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=2
compute compute compute
compute compute compute
compute compute compute
Distance vector example: iteration
Network Layer: 5-42
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
All nodes:
▪ receive distance 
vectors from 
neighbors
▪ compute their new 
local  distance 
vector
▪ send their new 
local distance 
vector to neighbors
t=2
Distance vector example: iteration
Network Layer: 5-43
…. and so on
Let’s next take a look at the iterative computations at nodes
DV in a: 
Da(a)=0
Da(b) = 8
Da(c) = ∞
Da(d) = 1
Da(e) = ∞
Da(f) = ∞
Da(g) = ∞
Da(h) = ∞
Da(i) = ∞
Distance vector example: computation
Network Layer: 5-44
g h i
1 1
1 1 1
1 1
1 1
8 1
t=1
DV in b:
Db(f) = ∞
Db(g) = ∞
Db(h) = ∞
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = ∞
Db(e) = 1
▪ b receives DVs 
from a, c, e
a b c
d e f
DV in c:
Dc(a) = ∞
Dc(b) = 1
Dc(c) = 0
Dc(d) = ∞
Dc(e) = ∞
Dc(f) = ∞
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = ∞
DV in e:
De(a) = ∞
De(b) = 1
De(c) = ∞
De(d) = 1
De(e) = 0
De(f) = 1
De(g) = ∞
De(h) = 1
De(i) = ∞
Distance vector example: computation
DV in a: 
Da(a)=0
Da(b) = 8
Da(c) = ∞
Da(d) = 1
Da(e) = ∞
Da(f) = ∞
Da(g) = ∞
Da(h) = ∞
Da(i) = ∞
DV in b:
Db(f) = ∞
Db(g) = ∞
Db(h) = ∞
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = ∞
Db(e) = 1
DV in c:
Dc(a) = ∞
Dc(b) = 1
Dc(c) = 0
Dc(d) = ∞
Dc(e) = ∞
Dc(f) = ∞
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = ∞
DV in e:
De(a) = ∞
De(b) = 1
De(c) = ∞
De(d) = 1
De(e) = 0
De(f) = 1
De(g) = ∞
De(h) = 1
De(i) = ∞
Network Layer: 5-45
g h i
1 1
1 1 1
1 1
1 1
8 1
t=1
▪ b receives DVs 
from a, c, e, 
computes:
a b c
d e f
DV in b:
Db(f) =2
Db(g) = ∞
Db(h) = 2
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = 2
Db(e) = 1
e
computeb
Db(a) = min{cb,a+Da(a), cb,c +Dc(a), cb,e+De(a)}  = min{8,∞,∞} = 8 
Db(c) = min{cb,a+Da(c), cb,c +Dc(c), c b,e +De(c)}  = min{∞,1,∞} = 1 
Db(d) = min{cb,a+Da(d), cb,c +Dc(d), c b,e +De(d)}  = min{9,2,∞} = 2 
Db(f) = min{cb,a+Da(f), cb,c +Dc(f), c b,e +De(f)}  = min{∞,∞,2} = 2 
Db(i) = min{cb,a+Da(i), cb,c +Dc(i), c b,e+De(i)}  = min{∞, ∞, ∞} = ∞ 
Db(h) = min{cb,a+Da(h), cb,c +Dc(h), c b,e+De(h)}  = min{∞, ∞, 2} = 2 
Db(e) = min{cb,a+Da(e), cb,c +Dc(e), c b,e +De(e)}  = min{∞,∞,1} = 1 
Db(g) = min{cb,a+Da(g), cb,c +Dc(g), c b,e+De(g)}  = min{∞, ∞, ∞} = ∞ 
DV in a: 
Da(a)=0
Da(b) = 8
Da(c) = ∞
Da(d) = 1
Da(e) = ∞
Da(f) = ∞
Da(g) = ∞
Da(h) = ∞
Da(i) = ∞
Distance vector example: computation
Network Layer: 5-46
g h i
1 1
1 1 1
1 1
1 1
8 1
t=1
DV in b:
Db(f) = ∞
Db(g) = ∞
Db(h) = ∞
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = ∞
Db(e) = 1
▪ c receives DVs 
from b
a b c
d e f
DV in c:
Dc(a) = ∞
Dc(b) = 1
Dc(c) = 0
Dc(d) = ∞
Dc(e) = ∞
Dc(f) = ∞
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = ∞
DV in e:
De(a) = ∞
De(b) = 1
De(c) = ∞
De(d) = 1
De(e) = 0
De(f) = 1
De(g) = ∞
De(h) = 1
De(i) = ∞
Distance vector example: computation
Network Layer: 5-47
g h i
1 1
8 1
t=1
DV in b:
Db(f) = ∞
Db(g) = ∞
Db(h) = ∞
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = ∞
Db(e) = 1
▪ c receives DVs 
from b computes:
a b c
d e f
DV in c:
Dc(a) = ∞
Dc(b) = 1
Dc(c) = 0
Dc(d) = ∞
Dc(e) = ∞
Dc(f) = ∞
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = ∞
Dc(a) = min{cc,b+Db(a}} = 1 + 8 = 9 
Dc(b) = min{cc,b+Db(b)} = 1 + 0 = 1
Dc(d) = min{cc,b+Db(d)} = 1+ ∞ = ∞ 
Dc(e) = min{cc,b+Db(e)} = 1 + 1 = 2
Dc(f) = min{cc,b+Db(f)} = 1+ ∞ = ∞ 
Dc(g) = min{cc,b+Db(g)} = 1+ ∞ = ∞ 
Dc(i) = min{cc,b+Db(i)} = 1+ ∞ = ∞ 
Dc(h) = min{cbc,b+Db(h)} = 1+ ∞ = ∞ 
DV in c:
Dc(a) = 9
Dc(b) = 1
Dc(c) = 0
Dc(d) = 2
Dc(e) = ∞
Dc(f) = ∞
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = ∞
compute
* Check out the online interactive 
exercises for more examples: 
http://gaia.cs.umass.edu/kurose_ross/interactive/
Distance vector example: computation
Network Layer: 5-48
1 1
1 1 1
1 1
1 1
8 1
t=1
DV in b:
Db(f) = ∞
Db(g) = ∞
Db(h) = ∞
Db(i) = ∞
Db(a) = 8
Db(c) = 1
Db(d) = ∞
Db(e) = 1
▪ e receives DVs 
from b, d, f, h
a b c
DV in f:
Dc(a) = ∞
Dc(b) = ∞
Dc(c) = ∞
Dc(d) = ∞
Dc(e) = 1
Dc(f) = 0
Dc(g) = ∞
Dc(h) = ∞
Dc(i) = 1
DV in e:
De(a) = ∞
De(b) = 1
De(c) = ∞
De(d) = 1
De(e) = 0
De(f) = 1
De(g) = ∞
De(h) = 1
De(i) = ∞
DV in h:
Dc(a) = ∞
Dc(b) = ∞
Dc(c) = ∞
Dc(d) = ∞
Dc(e) = 1
Dc(f) = ∞
Dc(g) = 1
Dc(h) = 0
Dc(i) = 1
DV in d:
Dc(a) = 1
Dc(b) = ∞
Dc(c) = ∞
Dc(d) = 0
Dc(e) = 1
Dc(f) = ∞ 
Dc(g) = 1
Dc(h) = ∞
Dc(i) = ∞
d e f
g h i
Q: what is new DV computed in e at 
t=1?
compute
Distance vector: state information diffusion
t=0 c’s state at t=0 is at c only
g h i
1 1
1 1 1
1 1
1 1
8 1
d e f
a b c
c’s state at t=0 has propagated to b, and 
may influence distance vector computations 
up to 1 hop away, i.e., at b
t=1
c’s state at t=0 may now influence distance 
vector computations up to 2 hops away, i.e., 
at b and now at a, e as well
t=2
c’s state at t=0 may influence distance vector 
computations up to 3 hops away, i.e., at d, f, ht=3
c’s state at t=0 may influence distance vector 
computations up to 4 hops away, i.e., at g, it=4
Iterative communication, computation steps diffuses information through network: 
t=1 
t=2 
t=3 
t=4 
Distance vector: link cost changes
“good news 
travels fast”
t0 : y detects link-cost change, updates its DV, informs its neighbors.
t1 : z receives update from y, updates its DV, computes new least cost 
to x , sends its neighbors its DV.
t2 : y receives z’s update, updates its DV.  y’s least costs do not 
change, so y does not send a message to z. 
link cost changes:
▪ node detects local link cost change 
▪ updates routing info, recalculates local DV
▪ if DV changes, notify neighbors 
x z
14
50
y
1
Distance vector: link cost changes
link cost changes:
▪ node detects local link cost change 
▪ “bad news travels slow” – count-to-infinity 
problem:
x z
14
50
y
60
• y sees direct link to x has new cost 60, but z has said it has a path at cost of 5. So 
y computes “my new cost to x will be 6, via z); notifies z of new cost of 6 to x.
• z learns that path to x via y has new cost 6, so z  computes “my new cost to 
x will be 7 via y), notifies y of new cost of 7 to x.
• y learns that path to x via z has new cost 7, so y  computes “my new cost to 
x will be 8 via y), notifies z of new cost of 8 to x.
• z learns that path to x via y has new cost 8, so z  computes “my new cost to 
x will be 9 via y), notifies y of new cost of 9 to x.
…
▪ see text for solutions.  Distributed algorithms are tricky!
Comparison of LS and DV algorithms
message complexity
LS: n routers, O(n2) messages sent  
DV: exchange between neighbors; 
convergence time varies
speed of convergence
LS: O(n2) algorithm, O(n2) messages
• may have oscillations
DV: convergence time varies
• may have routing loops
• count-to-infinity problem
robustness: what happens if router 
malfunctions, or is compromised?
LS: 
• router can advertise incorrect link cost
• each router computes only its own 
table
DV:
• DV router can advertise incorrect path 
cost (“I have a really low-cost path to 
everywhere”): black-holing
• each router’s DV is used by others: 
error propagate thru network
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-53

our routing study thus far - idealized 
▪ all routers identical
▪ network “flat”
… not true in practice
Making routing scalable
Network Layer: 5-54
scale: billions of destinations:
▪ can’t store all destinations in 
routing tables!
▪ routing table exchange would 
swamp links! 
administrative autonomy:
▪ Internet: a network of networks
▪ each network admin may want to 
control routing in its own network
aggregate routers into regions known as “autonomous 
systems” (AS) (a.k.a. “domains”)
Internet approach to scalable routing
Network Layer: 5-55
intra-AS (aka “intra-domain”): 
routing among routers within same 
AS (“network”)
▪ all routers in AS must run same intra-
domain protocol
▪ routers in different AS can run different 
intra-domain routing protocols
▪ gateway router: at “edge” of its own AS, 
has link(s) to router(s) in other AS’es
inter-AS (aka “inter-domain”): 
routing among AS’es
▪ gateways perform inter-domain 
routing (as well as intra-domain 
routing)
Interconnected ASes
Network Layer: 5-56
3b
1d
3a
1c
2a
AS3
AS1
AS21a
2c
2b
1b
3cintra-AS routing
intra-AS
routing
intra-AS
routing
inter-AS routing
forwarding
table
forwarding table  configured by intra- 
and inter-AS routing algorithms
Intra-AS
Routing 
Inter-AS
Routing ▪ intra-AS routing determine entries for 
destinations within AS
▪ inter-AS & intra-AS determine entries 
for external destinations
Inter-AS routing:  a role in intradomain forwarding
Network Layer: 5-57
3b
1d
3a
1c
2a
AS3
AS1
AS21a
2c
2b
1b
3c
other
networks
other
networks
▪ suppose router in AS1 receives 
datagram destined outside of AS1:
AS1 inter-domain routing must:
1. learn which destinations reachable 
through AS2, which through AS3
2. propagate this reachability info to all 
routers in AS1
• router should forward packet to 
gateway router in AS1, but which 
one?

Intra-AS routing:  routing within an AS
Network Layer: 5-58
most common intra-AS routing protocols:
▪ RIP: Routing Information Protocol [RFC 1723]
• classic DV: DVs exchanged every 30 secs
• no longer widely used
▪ EIGRP: Enhanced Interior Gateway Routing Protocol
• DV based
• formerly Cisco-proprietary for decades (became open in 2013 [RFC 7868])
▪  OSPF: Open Shortest Path First  [RFC 2328]
• link-state routing
• IS-IS protocol (ISO standard, not RFC standard) essentially same as OSPF
OSPF (Open Shortest Path First) routing
Network Layer: 5-59
▪ “open”: publicly available
▪ classic link-state 
• each router floods OSPF link-state advertisements (directly over IP 
rather than using TCP/UDP) to all other routers in entire AS
• multiple link costs metrics possible: bandwidth, delay
• each router has full topology, uses Dijkstra’s algorithm to compute 
forwarding table
▪ security: all OSPF messages authenticated (to prevent malicious 
intrusion) 
Hierarchical OSPF
Network Layer: 5-60
▪ two-level hierarchy: local area, backbone.
• link-state advertisements flooded only in area, or backbone
• each node has detailed area topology; only knows direction to reach 
other destinations
area border routers: 
“summarize” distances  to 
destinations in own area, 
advertise in backbone
area 1
area 2
area 3
backbone
internal
routers
backbone router: 
runs OSPF limited 
to backbone
boundary router: 
connects to other ASes
local routers: 
• flood LS in area only
• compute routing within 
area
• forward packets to outside 
via area border router
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-61

Interconnected ASes
3b
1d
3a
1c
2a
AS3
AS1
AS21a
2c
2b
1b
3cintra-AS routing
intra-AS
routing
intra-AS
routing
inter-AS routing
intra-AS (aka “intra-domain”): routing among routers within same 
AS (“network”)
inter-AS (aka “inter-domain”): routing among AS’es
Network Layer Control Plane: 5-62
▪ BGP (Border Gateway Protocol): the de facto inter-domain routing 
protocol
• “glue that holds the Internet together”
▪ allows subnet to advertise its existence, and the destinations it can 
reach, to rest of Internet: “I am here, here is who I can reach, and how”
▪ BGP provides each AS a means to:
• obtain destination network reachability info from neighboring ASes 
(eBGP)
• determine routes to other networks based on reachability information 
and policy
• propagate reachability information to all AS-internal routers (iBGP)
• advertise (to neighboring networks) destination reachability info
Internet inter-AS routing: BGP
Network Layer Control Plane: 5-63
eBGP , iBGP connections
Network Layer: 5-64
eBGP connectivity
logical iBGP connectivity
1b
1d
1c
1a
2b
2d
2c
2a
3b
3d
3c
3a
AS 2
AS 3AS 1
1c
∂
∂
gateway routers run both eBGP and iBGP protocols
BGP basics
Network Layer: 5-65
▪ when AS3 gateway 3a advertises path AS3,X to AS2 gateway 2c:
• AS3 promises to AS2 it will forward datagrams towards X
▪ BGP session: two BGP routers (“peers”) exchange BGP messages over 
semi-permanent TCP connection:
• advertising paths to different destination network prefixes (BGP  is a “path 
vector” protocol)
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
XBGP advertisement: AS3, X
BGP protocol messages
▪ BGP messages exchanged between peers over TCP connection
▪ BGP messages [RFC 4371]:
• OPEN: opens TCP connection to remote BGP peer and authenticates 
sending BGP peer
• UPDATE: advertises new path (or withdraws old)
• KEEPALIVE: keeps connection alive in absence of UPDATES; also ACKs 
OPEN request
• NOTIFICATION: reports errors in previous msg; also used to close 
connection
Path attributes and BGP routes
Network Layer: 5-67
▪ BGP advertised route:  prefix + attributes 
• prefix: destination being advertised
• two important attributes:
• AS-PATH: list of ASes through which prefix advertisement has passed
• NEXT-HOP: indicates specific internal-AS router to next-hop AS
▪ policy-based routing:
• gateway receiving route advertisement uses import policy to 
accept/decline path (e.g., never route through AS Y).
• AS policy also determines whether to advertise path to other other 
neighboring ASes
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
X
BGP path advertisement
Network Layer: 5-68
▪ based on AS2 policy, AS2 router 2c accepts path AS3,X, propagates (via iBGP) to all 
AS2 routers
AS2,AS3,X 
▪ AS2 router 2c receives path advertisement AS3,X (via eBGP) from AS3 router 3a
▪ based on AS2 policy,  AS2 router 2a advertises (via eBGP)  path AS2, AS3, X  to 
AS1 router 1c
AS3, X
Network Layer: 5-69
AS2,AS3,X 
▪ AS1 gateway router 1c learns path AS2,AS3,X from 2a
gateway router may learn about multiple paths to destination:
AS3,X
▪ AS1 gateway router 1c learns path AS3,X from 3a
▪ based on policy, AS1 gateway router 1c chooses path AS3,X and advertises path 
within AS1 via iBGP
AS3, X
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
X
AS3,X
AS3,X
AS3,X
BGP path advertisement: multiple paths
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
X
BGP: populating forwarding tables 
AS2,AS3,X 
AS3,X
AS3, X
▪ recall: 1a, 1b, 1d learn via iBGP from 1c: “path to X goes through 1c”
▪ at 1d: OSPF intra-domain routing: to get to 1c, use  interface 1
12
1
2
dest interface
…
…
…
…
local link 
interfaces
at 1a, 1d
▪ at 1d: to get to X, use  interface 1
1c 1
X 1
AS3,X
AS3,X
AS3,X
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
X
BGP: populating forwarding tables 
▪ recall: 1a, 1b, 1d learn via iBGP from 1c: “path to X goes through 1c”
▪ at 1d: OSPF intra-domain routing: to get to 1c, use  interface 1
1
2
▪ at 1d: to get to X, use  interface 1
dest interface
…
…
…
…
1c 2
X 2
▪ at 1a: OSPF intra-domain routing: to get to 1c, use  interface 2
▪ at 1a: to get to X, use  interface 2
2b
2d
2c
2a
AS 2
3b
3d
3c
3a
AS 3
1b
1d
1c
1a
AS 1
X
Hot potato routing
Network Layer: 5-72
▪ 2d learns (via iBGP) it can route to X via 2a or 2c
▪ hot potato routing: choose local gateway that has least intra-domain 
cost (e.g., 2d chooses 2a, even though more AS hops to X): don’t worry 
about inter-domain cost!
AS3,X AS1,AS3,X 
OSPF link weights
201
112
263
BGP: achieving policy via advertisements
Network Layer: 5-73
B
legend:
customer 
network:
provider
network
▪ A advertises path Aw to B and to C
▪ B chooses not to advertise BAw to C!  
▪ B gets no “revenue” for routing CBAw, since none of  C, A, w are B’s customers
▪ C does not learn about CBAw path
▪ C will route CAw (not using B) to get to w
ISP only wants to route traffic to/from its customer networks (does not want 
to carry transit traffic between other ISPs – a typical “real world” policy)
w A
yC
x
A,w
A,w
BGP: achieving policy via advertisements (more)
Network Layer: 5-74
B
ISP only wants to route traffic to/from its customer networks (does not want 
to carry transit traffic between other ISPs – a typical “real world” policy)
w A
yC
x
▪ A,B,C are provider networks
▪ x,w,y are customer (of provider networks)
▪ x is dual-homed: attached to two networks
▪ policy to enforce: x does not want to route from B to C via x 
▪ .. so x will not advertise to B a route to C
legend:
customer 
network:
provider
network
▪ router may learn about more than one route to destination 
AS, selects route based on:
1. local preference value attribute: policy decision
2. shortest AS-PATH 
3. closest NEXT-HOP router: hot potato routing
4. additional criteria 
BGP route selection
Network Layer: 5-75
Why different Intra-, Inter-AS routing ? 
Network Layer: 5-76
policy: 
▪ inter-AS: admin wants control over how its traffic routed, who 
routes through its network 
▪ intra-AS: single admin, so policy less of an issue
scale:
▪ hierarchical routing saves table size, reduced update traffic
performance: 
▪ intra-AS: can focus on performance
▪ inter-AS: policy dominates over performance
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-77

▪ Internet network layer: historically implemented via 
distributed, per-router control approach:
• monolithic router contains switching hardware, runs proprietary 
implementation of Internet standard protocols (IP , RIP , IS-IS, OSPF, 
BGP) in proprietary router OS (e.g., Cisco IOS)
• different “middleboxes” for different network layer functions: 
firewalls, load balancers, NAT boxes, ..
▪ ~2005: renewed interest in rethinking network control plane
Software defined networking (SDN)
Network Layer: 5-78
Per-router control plane
Individual routing algorithm components in each and every router 
interact in the control plane to compute forwarding tables
Routing
Algorithm
data
plane
control
plane
1
2
0111
values in arriving 
packet header
3
Network Layer: 4-79
Software-Defined Networking (SDN) control plane
Remote controller computes, installs forwarding tables in routers
data
plane
control
plane
Remote Controller
CA
CA CA CA CA
1
2
0111
3
values in arriving 
packet header
Network Layer: 4-80
Why a logically centralized control plane?
▪ easier network management: avoid router misconfigurations, 
greater flexibility of traffic flows
▪ table-based forwarding (recall OpenFlow API) allows 
“programming” routers
• centralized “programming” easier: compute tables centrally and distribute
• distributed “programming” more difficult: compute tables as result of 
distributed algorithm (protocol) implemented in each-and-every router 
▪ open (non-proprietary) implementation of control plane
• foster innovation: let 1000 flowers bloom
Software defined networking (SDN)
Network Layer: 5-81
SDN analogy: mainframe to PC revolution
Network Layer: 5-82
Vertically integrated
Closed, proprietary
Slow innovation
Small industry
Specialized
Operating
System
Specialized
Hardware
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
Ap
p
App
Specialized
Applications
Horizontal
Open interfaces
Rapid innovation
Huge industry
Microprocessor
Open Interface
* Slide  courtesy: N. McKeown
or or
Open Interface
Windows
 Linux
 MAC OS
2
2
1
3
1
1
2
5
3
5
v
 w
u
 z
y
x
Traffic engineering: difficult with traditional routing
Network Layer: 5-83
Q: what if network operator wants u-to-z traffic to flow along 
uvwz, rather than uxyz?
A: need to re-define link weights so traffic routing algorithm 
computes routes accordingly (or need a new routing algorithm)!
link weights are only control “knobs”: not much control!
2
2
1
3
1
1
2
5
3
5
v
 w
u
 z
y
x
Traffic engineering: difficult with traditional routing
Network Layer: 5-84
Q: what if network operator wants to split  u-to-z 
traffic along uvwz and uxyz (load balancing)?
A: can’t do it (or need a new routing algorithm)
Traffic engineering: difficult with traditional routing
Network Layer: 5-85
Q: what if w wants to route blue and red traffic differently from w to z?
A: can’t do it (with destination-based forwarding, and LS, DV routing)
2
2
1
3
1
1
2
5
3
5
v
 w
u
 z
y
x
We learned in Chapter 4 that generalized forwarding and SDN can 
be used to achieve any routing desired
Software defined networking (SDN)
Network Layer: 5-86
data
plane
control
plane
Remote Controller
CA
CA CA CA CA
1: generalized “flow-based” 
forwarding (e.g., OpenFlow)
2. control, data 
plane separation
3. control plane functions 
external to data-plane 
switches
…routing access control load balance4. programmable 
control 
applications
Software defined networking (SDN)
Network Layer: 5-87
Data-plane switches:
▪ fast, simple, commodity switches 
implementing generalized data-plane 
forwarding (Section 4.4) in hardware
▪ flow (forwarding) table computed, 
installed under controller supervision
▪ API for table-based switch control 
(e.g., OpenFlow)
• defines what is controllable, what is not
▪ protocol for communicating with 
controller (e.g., OpenFlow)
data
plane
control
plane
SDN Controller
(network operating system)
…routing
access 
control
load
balance
southbound API
northbound API
SDN-controlled switches
network-control applications
Software defined networking (SDN)
Network Layer: 5-88
SDN controller (network OS): 
▪ maintain network state 
information
▪ interacts with network control 
applications “above” via 
northbound API
▪ interacts with network switches 
“below” via southbound API
▪ implemented as distributed system 
for performance, scalability, fault-
tolerance, robustness
data
plane
control
plane
SDN Controller
(network operating system)
…routing
access 
control
load
balance
southbound API
northbound API
SDN-controlled switches
network-control applications
Software defined networking (SDN)
Network Layer: 5-89
network-control apps:
▪ “brains” of control:  
implement control functions 
using lower-level services, API 
provided by SDN controller
▪ unbundled: can be provided by 
3rd party: distinct from routing 
vendor, or SDN controller
data
plane
control
plane
SDN Controller
(network operating system)
…routing
access 
control
load
balance
southbound API
northbound API
SDN-controlled switches
network-control applications
Components of SDN controller
Network Layer: 5-90
Network-wide distributed, robust  state management
Communication to/from controlled devices
Link-state info
 switch info
host info
statistics
 flow tables…  
…  
OpenFlow
 SNMP…  
network 
graph
 intent
RESTful
API …  
Interface, abstractions for network control apps
SDN
controller
routing access control load balance
communication: communicate 
between SDN controller and 
controlled switches
network-wide state 
management : state of 
networks links, switches, 
services: a distributed database
interface layer to network 
control apps: abstractions API
OpenFlow protocol
Network Layer: 5-91
▪ operates between controller, switch
▪ TCP used to exchange messages
• optional encryption
▪ three classes of  OpenFlow messages:
• controller-to-switch
• asynchronous (switch to controller)
• symmetric (misc.)
▪ distinct from OpenFlow API
• API used to specify  generalized 
forwarding actions
OpenFlow Controller
OpenFlow: controller-to-switch messages
Network Layer: 5-92
Key controller-to-switch messages
▪ features: controller queries switch 
features, switch replies
▪ configure: controller queries/sets 
switch configuration parameters
▪ modify-state: add, delete, modify flow 
entries in the OpenFlow tables
▪ packet-out: controller can send this 
packet out of specific switch port
OpenFlow Controller
OpenFlow: switch-to-controller messages
Network Layer: 5-93
Key switch-to-controller messages
▪ packet-in: transfer packet (and its 
control) to controller.  See packet-out 
message from controller
▪ flow-removed: flow table entry deleted 
at switch
▪ port status: inform controller of a 
change on a port.
Fortunately, network operators don’t “program” switches by creating/sending 
OpenFlow messages directly.  Instead use higher-level abstraction at controller
OpenFlow Controller
SDN: control/data plane interaction example
Network Layer: 5-94
Link-state info
 switch info
host info
statistics
 flow tables
…  
…  
OpenFlow
 SNMP…  
network 
graph
 intent
RESTful
API
…  
Dijkstra’s link-state 
routing
s1
s2
s3
s4
S1, experiencing link failure uses 
OpenFlow port status message to 
notify controller
1
SDN controller receives OpenFlow 
message, updates link status info
2
Dijkstra’s routing algorithm 
application has previously registered 
to be called when ever link status 
changes.  It is called.
3
Dijkstra’s routing algorithm 
access network graph info, link 
state info in controller,  computes 
new routes
4
1
2
3
4
SDN: control/data plane interaction example
Network Layer: 5-95
Link-state info
 switch info
host info
statistics
 flow tables
…  
…  
OpenFlow
 SNMP…  
network 
graph
 intent
RESTful
API
…  
Dijkstra’s link-state 
routing
s1
s2
s3
s4
link state routing app interacts 
with flow-table-computation 
component in SDN controller, 
which computes new flow tables 
needed
5
controller uses OpenFlow to 
install new tables in switches 
that need updating
6
5
1
2
3
4
ONOS SDN controller
Network Layer: 5-96
Network Applications
Southbound API
Northbound API
Traffic 
Engineering …Firewalling Load Balancing
southbound 
abstractions,
protocols
OpenFlow
 Netconf
 OVSDB
device
 link
 host
 flow
 packet
northbound 
abstractions,
protocols
REST    API
 Intent
ONOS
distributed 
core
statistics
devices
hosts
links
paths
 flow rules
 topology
▪ control apps separate 
from controller
▪ intent framework: high-
level specification of 
service: what rather 
than how
▪ considerable emphasis 
on distributed core: 
service reliability, 
replication performance 
scaling
ONOS:  early, influential open-source SDN controller
Google ORION SDN control plane
ORION: Google’s SDN control plane (NSDI’21): control plane for 
Google’s datacenter (Jupiter) and wide area (B4) networks
Orion SDN architecture and core apps▪ routing (intradomain, iBGP), traffic 
engineering: implemented in applications 
on top of ORION core
▪ edge-edge flow-based controls (e.g., 
CoFlow scheduling) to meet contract SLAs
▪ management: pub-sub distributed 
microservices in Orion core, OpenFlow for 
switch signaling/monitoring 
Note: ORION provides intradomain services within Google’s network
Google, SDN: the value of a logically-centralized abstraction
▪ new opportunities to more formally, 
intentionally manage configuration
“ ... in a single building or even across a private global WAN such that 
we[Google]  were designing, the location and role of every network 
element is known ahead of time.  So - rather than allowing a node to boot, 
exchange messages with neighbors, and learn its role in the global 
network, we knew we could configure the role of all network elements into 
a logically centralized controller that could then inform all relevant 
elements of new and changing configurations. This shifted the problem of 
network management from managing the configuration of individual 
network elements to managing the configuration of a logical network, 
dramatically simplifying the problem both from a technical perspective but 
also from the perspective of the cognitive load on network managers. ”∂
Amin Vahdat, Engineering Fellow, VP for the 
Machine Leaning, Systems, and Cloud AI teamhttps://www.youtube.com/watch?v=qn7d_iK92TI
▪ hardening the control plane: dependable, reliable, performance-
scalable, secure distributed system
• robustness to failures: leverage strong theory of reliable distributed 
system for control plane
• dependability, security: “baked in” from day one? 
▪ networks, protocols meeting mission-specific requirements
• e.g., real-time, ultra-reliable, ultra-secure
▪ Internet-scaling: beyond a single AS
▪ SDN critical in 5G cellular networks
SDN:  selected challenges
Network Layer: 5-99
▪ SDN-computed versus router-computer forwarding tables:
• just one example of logically-centralized-computed versus protocol 
computed
▪ one could imagine SDN-computed congestion control: 
• controller sets sender rates based on router-reported (to 
controller) congestion levels 
SDN and the future of traditional network protocols
Network Layer: 5-100
How will implementation of 
network functionality (SDN 
versus protocols) evolve?

Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-101

ICMP: internet control message protocol
Network Layer: 4-102
▪ used by hosts and routers to 
communicate network-level 
information
• error reporting: unreachable host, 
network, port, protocol
• echo request/reply (used by ping)
▪ network-layer “above” IP:
• ICMP messages carried in IP 
datagrams
▪ ICMP message: type, code plus 
first 8 bytes of IP datagram causing 
error
Type  Code  description
0        0         echo reply (ping)
3        0         dest. network unreachable
3        1         dest host unreachable
3        2         dest protocol unreachable
3        3         dest port unreachable
3        6         dest network unknown
3        7         dest host unknown
4        0         source quench (congestion
                     control - not used)
8        0         echo request (ping)
9        0         route advertisement
10      0         router discovery
11      0         TTL expired
12      0         bad IP header
Traceroute and ICMP
Network Layer: 4-103
▪ when ICMP message arrives at source: record RTTs
stopping criteria:
▪ UDP segment eventually 
arrives at destination host
▪ destination returns ICMP 
“port unreachable” 
message (type 3, code 3)
▪ source stops
3 probes
3 probes
3 probes
▪ source sends sets of UDP segments to 
destination
• 1st  set has TTL =1, 2nd  set has TTL=2, etc.
▪ datagram in nth set arrives to nth router:
• router discards datagram and sends source 
ICMP message (type 11, code 0)
• ICMP message possibly includes name of 
router & IP address
Network layer: “control plane” roadmap
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-104

▪ autonomous systems (aka “network”): 1000s of interacting 
hardware/software components
▪ other complex systems requiring monitoring, configuration, 
control:
• jet airplane, nuclear power plant, others?
What is network management?
Network Layer: 5-105
"Network management includes the deployment, integration 
and coordination of the hardware, software, and human 
elements to monitor, test, poll, configure, analyze, evaluate, 
and control the network and element resources to meet the 
real-time, operational performance, and Quality of Service 
requirements at a reasonable cost." 

Components of network management
Network Layer: 5-106
managed device managed device
managed device
managed device
managed device
agent data
agent data
agent data
agent data
agent data
managing
server/controller
data
Managing server: 
application, typically 
with network
managers (humans) in 
the loop
Managed device: 
equipment with manageable, 
configurable hardware, 
software components
Data: device “state” 
configuration data, 
operational data, 
device statistics
Network 
management 
protocol: used by 
managing server to query, 
configure, manage device; 
used by devices to inform 
managing server of data, 
events.
Network operator approaches to management
Network Layer: 5-107
managed device managed device
managed device
managed device
managed device
agent data
agent data
agent data
agent data
agent data
managing
server/controller
data
CLI (Command Line Interface) 
• operator issues (types, scripts) direct to 
individual devices (e.g., vis ssh)
SNMP/MIB 
• operator queries/sets devices data 
(MIB) using Simple Network 
Management Protocol (SNMP)
NETCONF/YANG
• more abstract, network-wide, holistic
• emphasis on multi-device configuration 
management. 
• YANG: data modeling language 
• NETCONF: communicate YANG-compatible 
actions/data to/from/among remote devices 
SNMP protocol
Network Layer: 5-108
managed device
agent data
managing
server/controller
data
request
response
 trap message
Two ways to convey MIB info, commands:
request/response mode
managed device
agent data
managing
server/controller
data
trap mode
SNMP protocol: message types
Network Layer: 5-109
GetRequest
GetNextRequest
GetBulkRequest
manager-to-agent: “get me data”
(data instance, next data in list, 
                                 block of data). 
Message type Function
SetRequest manager-to-agent: set MIB value
Response Agent-to-manager: value, response 
to Request
Trap Agent-to-manager: inform manager
of exceptional event
SNMP protocol: message formats
Network Layer: 5-110
….
PDU
type
(0-3)
Request
ID
Error
Status
(0-5)
Error
Index Name Value Name Value
Get/set header Variables to get/set
SNMP PDU
message types 0-3
….
PDU
type
4
Enterprise Agent Addr Trap Type (0-7) Specific code Time stamp Name Value
Trap header Trap info
message type 4
▪ managed device’s operational (and some configuration) data
▪ gathered into device MIB module
• 400 MIB modules defined in RFC’s; many more vendor-specific MIBs
SNMP: Management Information Base (MIB)
Network Layer: 5-111
Object ID           Name                      Type                  Comments
1.3.6.1.2.1.7.1     UDPInDatagrams     32-bit counter     total # datagrams delivered 
1.3.6.1.2.1.7.2    UDPNoPorts              32-bit counter     # undeliverable datagrams (no application at port)
1.3.6.1.2.1.7.3    UDInErrors                 32-bit counter     # undeliverable datagrams (all other reasons)
1.3.6.1.2.1.7.4    UDPOutDatagrams   32-bit counter    total  # datagrams sent
1.3.6.1.2.1.7.5    udpTable               SEQUENCE          one entry for each port currently in use
agent data
▪ Structure of Management Information (SMI): data definition language
▪ example MIB variables for UDP protocol:
▪ goal: actively manage/configure devices network-wide
▪ operates between managing server and managed network devices
• actions: retrieve, set, modify, activate configurations
• atomic-commit actions over multiple devices
• query operational data and statistics
• subscribe to notifications from devices
▪ remote procedure call (RPC) paradigm
• NETCONF protocol messages encoded in XML
• exchanged over secure, reliable transport (e.g., TLS) protocol
NETCONF overview
Network Layer: 5-112
NETCONF initialization, exchange, close
Network Layer: 5-113
Session initiation, 
capabilities exchange: <hello>
Session close:  <close-session>
<rpc>
<rpc-reply>
<rpc>
<rpc-reply>
<rpc>
<rpc-reply>
<notification>
………… …
……… …
managing
server/controller
data
agent data
Selected NETCONF Operations
Network Layer: 5-114
NETCONF              Operation Description
<get-config>                Retrieve all or part of a given configuration. A device may have multiple 
configurations. 
<get>                            Retrieve all or part of both configuration state and operational state data.
<edit-config>              Change specified (possibly running) configuration at managed device. 
Managed device <rpc-reply> contains <ok>  or <rpcerror> with rollback.
<lock>, <unlock>        Lock (unlock) configuration datastore at managed device (to lock out 
NETCONF, SNMP , or CLIs commands from other sources).
<create-subscription>,    Enable event notification subscription from managed device
<notification>
Sample NETCONF RPC message
Network Layer: 5-115
note message id
change the running configuration 
change MTU of Ethernet 0/0 interface to 1500
change a configuration
▪ data modeling language used to specify 
structure, syntax, semantics of 
NETCONF network management data
• built-in data types, like SMI
▪ XML document describing device, 
capabilities can be generated from 
YANG description
▪ can express constraints among data that 
must be satisfied by a valid NETCONF 
configuration
• ensure NETCONF configurations satisfy 
correctness, consistency constraints
YANG
Network Layer: 5-116
agent data
managing
server/controller
data
NETCONF RPC message
<edit-config>
  YANG-generated XML
</edit-config> YANG
generated
Network layer:  Summary
Network Layer: 5-117
we’ve learned a lot!
▪ approaches to network control plane
• per-router control (traditional)
• logically centralized control (software defined networking)
▪ traditional routing algorithms
• implementation in Internet: OSPF , BGP
▪ SDN controllers
• implementation in practice: ODL, ONOS
▪ Internet Control Message Protocol
▪ network management
next stop:  link layer!
Network layer, control plane:  Done!
▪ network management, 
configuration 
• SNMP
• NETCONF/YANG
▪ introduction
▪ routing protocols
▪ link state
▪ distance vector
▪ intra-ISP routing: OSPF
▪ routing among ISPs: BGP
▪ SDN control plane
▪ Internet Control Message 
Protocol 
Network Layer: 5-118

Additional Chapter 5 slides
Network Layer: 5-119
Distance vector: another example
Network Layer: 5-120
x   y   z
x
y
z
0  2   7
∞ ∞ ∞
∞ ∞ ∞
from
cost to
fromfrom
x   y   z
x
y
z
0
x   y   z
x
y
z
∞ ∞
∞ ∞ ∞
cost to
x   y   z
x
y
z
∞ ∞ ∞
7 1 0
cost to
∞
2   0   1
∞ ∞  ∞
2   0   1
7   1   0
time
x z
12
7
y
Dx()
Dx(y) = min{cx,y + Dy(y), cx,z+ Dz(y)}
= min{2+0 , 7+1} = 2
Dx(z) = min{cx,y+ Dy(z), cx,z+ Dz(z)} 
= min{2+1 , 7+0} = 3
32 
Dy()
Dz()
cost to
from
Distance vector: another example
Network Layer: 5-121
x   y   z
x
y
z
0  2   7
∞ ∞ ∞
∞ ∞ ∞
cost to
fromfrom
x   y   z
x
y
z
∞ ∞
∞ ∞ ∞
cost to
x   y   z
x
y
z
∞ ∞ ∞
7 1 0
cost to
∞
2   0   1
∞ ∞  ∞
x z
12
7
y
Dx()
Dy()
Dz() from
x   y   z
x
y
z
0  2   3
from
cost to
x   y   z
x
y
z
0  2   7
from
cost to
x   y   z
x
y
z
0  2   3
from
cost to
x   y   z
x
y
z
0  2   3
from
cost to
x   y   z
x
y
z
0  2   7
from
cost to
2  0   1
7   1   0
2  0   1
3  1   0
2   0   1
3  1   0
2  0   1
3  1   0
2  0   1
3  1   0
from
x   y   z
x
y
z
0
2   0   1
7   1   0
32 
cost to
time