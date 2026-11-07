<!-- converted from Chapter_1_v9.0.pdf -->

Introduction: 1-1
Chapter 1
Introduction
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
Computer Networking: A 
Top-Down Approach 
9th edition 
Jim Kurose, Keith Ross
Pearson, 2025

Chapter 1: introduction
Chapter goal: 
▪ Get “feel,” “big picture,” 
introduction to terminology
• more depth, detail later in 
course
Overview/roadmap:
▪ What is the Internet? What is a 
protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit switching, 
internet structure
▪ Performance: loss, delay, throughput
▪ Protocol layers, service models
▪ Security
▪ History
Introduction: 1-2

Internet
The Internet: a “nuts and bolts” view
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Packet switches: forward 
packets (chunks of data)
▪ routers, switches
Communication links
▪ fiber, copper, radio, satellite
▪ transmission rate: bandwidth
Billions of connected 
computing devices: 
▪ hosts = end systems 
▪ running network apps at 
Internet’s “edge”
Networks
▪ collection of devices, routers, 
links: managed by an organization
Introduction: 1-3
“Fun” Internet-connected devices
Web-enabled toaster +
weather forecaster
Internet phones
Slingbox: remote
control cable TV
Security Camera
IP picture frame
Internet 
refrigerator
Tweet-a-watt: 
monitor energy use
sensorized,
bed
mattress
Amazon Echo
Gaming devices
cars
scooters
bikes
Introduction: 1-4
Pacemaker & Monitor
AR devices
Fitbit
diapers
▪ Internet: “network of networks”
• Interconnected ISPs
The Internet: a “nuts and bolts” view
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
▪ protocols are everywhere
• control sending, receiving of 
messages
• e.g., HTTP (Web), streaming video, 
Zoom, TCP , IP , WiFi, 4/5G, Ethernet
Ethernet
HTTP
Skype IP
WiFi
4G
TCP
Streaming
video
▪ Internet  standards
• RFC: Request for Comments
• IETF: Internet Engineering Task 
Force
Introduction: 1-5
▪ Infrastructure that provides 
services to applications:
• Web, streaming video, multimedia 
teleconferencing, email, games, e-
commerce, social media, inter-
connected appliances, …
The Internet: a “services” view
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
HTTP
Skype
Streaming
video
▪ provides programming interface 
to distributed applications:
• “hooks” allowing sending/receiving  
apps to “connect” to, use  Internet 
transport service
• provides service options, analogous 
to postal service
Introduction: 1-6
What’s a protocol?
Human protocols:
▪ “what’s the time?”
▪ “I have a question”
▪ introductions
Network protocols:
▪ computers (devices) rather than humans
▪ all communication activity in Internet 
governed by protocols
Protocols define the format, order of 
messages sent and received among 
network entities, and actions taken 
on message transmission, receipt 
Rules for:
… specific messages sent
… specific actions taken 
when message received, 
or other events
Introduction: 1-7
What’s a protocol?
A human protocol and a computer network protocol:
Q: other human protocols? 
Hi
Hi
Got the
time?
2:00
time
TCP connection
response
<file>
TCP connection
request
GET http://gaia.cs.umass.edu/kurose_ross
Introduction: 1-8

Chapter 1: roadmap
Introduction: 1-9
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History
A closer look at Internet structure
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Network edge:
▪ hosts: clients and servers
▪ servers often in data centers
Introduction: 1-10
A closer look at Internet structure
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Network edge:
▪ hosts: clients and servers
▪ servers often in data centers
Access networks, physical media:
▪wired, wireless communication links 
Introduction: 1-11
A closer look at Internet structure
Network edge:
▪ hosts: clients and servers
▪ servers often in data centers
Access networks, physical media:
▪wired, wireless communication links 
Network core: 
▪ interconnected routers
▪ network of networks
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Introduction: 1-12
Access networks and physical media
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Q: How to connect end systems 
to edge router?
▪ residential access nets
▪ institutional access networks (school, 
company)
▪ mobile access networks (WiFi, 4G/5G)
Introduction: 1-13
Access networks: cable-based access
cable
modem
splitter
…
cable headend
Channels
V
I
D
E
O
V
I
D
E
O
V
I
D
E
O
V
I
D
E
O
V
I
D
E
O
V
I
D
E
O
D
A
T
A
D
A
T
A
C
O
N
T
R
O
L
1 2 3 4 5 6 7 8 9
frequency division multiplexing (FDM): different channels transmitted in 
different frequency bands
Introduction: 1-14
Access networks: cable-based access
cable
modem
splitter
…
cable headend
data, TV transmitted at different 
frequencies over shared cable 
distribution network
▪ HFC: hybrid fiber coax
• asymmetric: up to 40 Mbps – 1.2 Gbps downstream transmission rate, 30-100 Mbps 
upstream transmission rate
▪ network of cable, fiber attaches homes to ISP router
• homes share access network to cable headend 
cable modem
termination systemCMTS
ISP
Introduction: 1-15
ISP
Access networks: digital subscriber line (DSL)
central office telephone
network
DSLAM
voice, data transmitted
at different frequencies over
dedicated line to central office
▪ use existing telephone line to central office DSLAM
• data over DSL phone line goes to Internet
• voice over DSL phone line goes to telephone net
▪ 24-52 Mbps dedicated downstream transmission rate 
▪ 3.5-16 Mbps dedicated upstream transmission rate
DSL
modem
splitter
DSL access 
multiplexer
Introduction: 1-16
Access networks: home networks
to/from headend or 
central office
cable or DSL modem
router, firewall, NAT
wired Ethernet (1 Gbps)
WiFi wireless access 
point (54, 450 Mbps)
Wireless and wired
devices
often combined 
in single box
Introduction: 1-17
Wireless access networks
Shared wireless access network connects end system to router
▪ via base station aka “access point”
Wireless local area networks 
(WLANs)
▪ typically within or around 
building (~100 ft)
▪ 802.11b/g/n (WiFi): 11, 54, 450 
Mbps transmission rate
to Internet
to Internet
Wide-area cellular access networks
▪ provided by mobile, cellular network 
operator (10’s km)
▪ 10’s Mbps 
▪ 4G/5G cellular networks
Introduction: 1-18
Access networks: enterprise networks
▪ companies, universities, etc.
▪ mix of wired, wireless link technologies, connecting a mix of switches 
and routers (we’ll cover differences shortly)
▪ Ethernet: wired access at 100Mbps, 1Gbps, 10Gbps 
▪ WiFi: wireless access points at 11, 54, 450 Mbps 
Ethernet 
switch
institutional mail,
web servers
institutional router
Enterprise link to 
ISP (Internet)
Introduction: 1-19
Access networks: data center networks
▪ high-bandwidth links (10s to 100s 
Gbps) connect hundreds to thousands 
of servers together, and to Internet
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Courtesy: Massachusetts Green High Performance Computing 
Center (mghpcc.org)
Introduction: 1-20
Host: sends packets of data
host sending function:
▪ takes application message
▪ breaks into smaller chunks, 
known as packets, of length L bits
▪ transmits packet into access 
network at transmission rate R
• link transmission rate, aka link 
capacity, aka link bandwidth R: link transmission rate
host
12
two packets, 
L bits each
packet
transmission
delay
time needed to
transmit L-bit
packet into link
L (bits)
R (bits/sec)
= =
Introduction: 1-21
Links: physical media
▪ bit: propagates between
transmitter/receiver pairs
▪ physical link: what lies 
between transmitter & 
receiver
▪ guided media: 
• signals propagate in solid 
media: copper, fiber, coax
▪ unguided media: 
• signals propagate freely, 
e.g., radio
Twisted pair (TP)
▪ two insulated copper wires
• Category 5: 100 Mbps, 1 Gbps Ethernet
• Category 6: 10Gbps Ethernet
Introduction: 1-22
Links: physical media
Coaxial cable:
▪ two concentric copper conductors
▪ bidirectional
▪ broadband:
• multiple frequency channels on cable
• 100’s Mbps per channel
Fiber optic cable:
▪ glass fiber carrying light pulses, each 
pulse a bit
▪ high-speed operation:
• high-speed point-to-point 
transmission (10’s-100’s Gbps)
▪ low error rate: 
• repeaters spaced far apart 
• immune to electromagnetic noise
Introduction: 1-23
Links: physical media
Wireless radio
▪ signal carried in various 
“bands” in electromagnetic 
spectrum
▪ no physical “wire”
▪ broadcast, “half-duplex” 
(sender to receiver)
▪ propagation environment 
effects:
• reflection 
• obstruction by objects
• Interference/noise
Radio link types:
▪ Wireless LAN (WiFi)
• 10-100’s Mbps; 10’s of meters
▪ wide-area (e.g., 4G/5G cellular)
• 100’s Mbps (4G/5G) over ~10 Km 
▪ Bluetooth: cable replacement
• short distances, limited rates
▪ terrestrial  microwave
• point-to-point; 45 Mbps channels
▪ satellite
• up to < 100 Mbps (Starlink) downlink
• 270 msec end-end delay (geostationary)
Introduction: 1-24
Chapter 1: roadmap
Introduction: 1-25
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History

The network core
▪ mesh of interconnected routers
▪ packet-switching: hosts break 
application-layer messages into 
packets
• network forwards packets from one 
router to the next, across links on 
path from source to destination
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network
Introduction: 1-26
Two key network-core functions
1
23
destination address in arriving
packet’s header
routing algorithm
header value output link
0100
0101
0111
1001
3
2
2
1
local forwarding tableForwarding: 
▪ aka “switching”
▪ local action: 
move arriving 
packets from 
router’s input link 
to appropriate 
router output link
local forwarding table
Routing: 
▪ global action: 
determine source-
destination paths 
taken by packets
▪ routing algorithms
routing algorithm
Introduction: 1-27
routing
Introduction: 1-28
forwarding
 forwarding
Introduction: 1-29
Packet-switching: store-and-forward
▪ packet transmission delay: takes L/R seconds to 
transmit (push out) L-bit packet into link at R bps
▪ store and forward: entire packet must  arrive at 
router before it can be transmitted on next link
source
R bps
destination123
L bits
per packet
R bps
One-hop numerical example:
▪ L = 10 Kbits
▪ R = 100 Mbps
▪ one-hop transmission delay 
= 0.1 msec
Introduction: 1-30
Packet-switching: queueing
A
B
CR = 100 Mb/s
R = 1.5 Mb/s D
E
queue of packets
waiting for transmission 
over output link
Queueing occurs when work arrives faster than it can be serviced:
Introduction: 1-31
Packet-switching: queueing
A
B
CR = 100 Mb/s
R = 1.5 Mb/s D
E
queue of packets
waiting for transmission 
over output link
Packet queuing and loss: if arrival rate (in bps) to link exceeds 
transmission rate (bps) of link for some period of time:
▪ packets will queue, waiting to be transmitted on output link 
▪ packets can be dropped (lost) if memory (buffer) in router fills up
Introduction: 1-32
Alternative to packet switching: circuit switching
end-end resources allocated to, 
reserved for “call” between source 
and destination
▪ in diagram, each link has four circuits. 
• call gets 2nd circuit in top link and 1st 
circuit in right link.
▪ dedicated resources: no sharing
• circuit-like (guaranteed) performance
▪ circuit segment idle if not used by call (no 
sharing)
* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive
▪ commonly used in traditional telephone networks
Introduction: 1-33
Circuit switching: FDM and TDM
frequency
time
frequency
time
4 usersFrequency Division Multiplexing (FDM)
▪ optical, electromagnetic frequencies 
divided into (narrow) frequency 
bands
Time Division Multiplexing (TDM)
▪ time divided into slots
▪ each call allocated its own band, can 
transmit at max rate of that narrow 
band 
▪ each call allocated periodic slot(s), can 
transmit at maximum rate of (wider) 
frequency band (only)  during its time 
slot(s)
Introduction: 1-34
Packet switching versus circuit switching
example:
▪ 1 Gb/s link
▪ each user: 
• 100 Mb/s when “active”
• active 10% of time
Q: how many users can use this network under circuit-switching and packet switching?
* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive
N 
users 1 Gbps link
▪ circuit-switching: 10 users
Q: how did we get value 0.0004?
A: HW problem (for those with 
course in probability only)
▪ packet switching:  with 35 users, 
probability > 10 active at same time 
is less than .0004 *
Introduction: 1-35
Packet switching versus circuit switching
▪ great for “bursty” data – sometimes has data to send, but at other times not
• resource sharing
• simpler, no call setup
▪ excessive congestion possible: packet delay and loss due to buffer overflow
• protocols needed for reliable data transfer, congestion control
▪ Q: How to provide circuit-like behavior with packet-switching?
• “It’s complicated.” We’ll study various techniques that try to make packet 
switching as “circuit-like” as possible.
Is packet switching a “slam dunk winner”?
Q:  human analogies of reserved resources (circuit switching) versus 
on-demand allocation (packet switching)?
Introduction: 1-36
Internet structure: a “network of networks”
▪ hosts connect to Internet via access 
Internet Service Providers (ISPs)
▪ access ISPs in turn must be 
interconnected
• so that any two hosts (anywhere!) 
can send packets to each other
▪ resulting network of networks is 
very complex
• evolution driven by economics, 
national policies
Let’s take a stepwise approach to describe current Internet structure
mobile network
home network
enterprise
          network
national or global ISP
local or 
regional ISP
datacenter 
network
content 
provider 
network

Internet structure: a “network of networks”
Question: given millions of access ISPs, how to connect them together?
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
netaccess
net
access
net
Introduction: 1-38
Internet structure: a “network of networks”
Question: given millions of access ISPs, how to connect them together?
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
netaccess
net
access
net
connecting each access ISP to 
each other directly doesn’t scale: 
O(N2) connections.
Introduction: 1-39
Internet structure: a “network of networks”
Option: connect each access ISP to one global transit ISP? 
Customer and provider ISPs have economic agreement.
global
ISP
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
netaccess
net
access
net
Introduction: 1-40
ISP A
ISP C
ISP B
Internet structure: a “network of networks”
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
netaccess
net
access
net
But if one global ISP is viable business, there will be competitors ….
Introduction: 1-41
ISP A
ISP C
ISP B
Internet structure: a “network of networks”
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
netaccess
net
access
net
But if one global ISP is viable business, there will be competitors …. who will 
want to be connected
IXP
peering link
Internet exchange point 
IXP
Introduction: 1-42
ISP A
ISP C
ISP B
Internet structure: a “network of networks”
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
… and regional networks may arise to connect access nets to ISPs 
IXP
IXP
access
net
access
net
regional ISP
access
net access
net
access
net
Introduction: 1-43
ISP A
ISP C
ISP B
Internet structure: a “network of networks”
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
access
net
… and content provider networks  (e.g., Google, Microsoft,  Akamai) may 
run their own network, to bring services, content close to end users
IXP
IXP
access
net
access
net
access
net access
net
access
net
Content provider network
regional ISP
Introduction: 1-44
Internet structure: a “network of networks”
access
ISP
access
ISP
access
ISP
access
ISP
access
ISP
access
ISP
access
ISP
access
ISP
At “center”: small # of well-connected large networks
▪ “tier-1” commercial ISPs (e.g., Level 3, Sprint, AT&T, NTT), national & international coverage
▪ content provider networks (e.g., Google, Facebook): private network that connects its 
data centers to Internet, often bypassing tier-1, regional ISPs
Regional ISP Regional ISP
Tier 1 ISP Tier 1 ISP
IXP
Google
IXPIXP
Introduction: 1-45
Chapter 1: roadmap
Introduction: 1-46
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History

How do packet delay and loss occur?
▪ packets queue in router buffers, waiting for turn for transmission
▪ queue length grows when arrival rate to link (temporarily) exceeds output link 
capacity 
▪ packet loss occurs when memory to hold queued packets fills up
A
B
packet being transmitted (transmission delay)
packets in buffers (queueing delay)
free (available) buffers: arriving packets 
dropped (loss) if no free buffers
Introduction: 1-47
Packet delay: four sources
dproc: nodal processing 
▪ check bit errors
▪ determine output link
▪ typically < microsecs
dqueue: queueing delay
▪ time waiting at output link for 
transmission 
▪ depends on congestion level of 
router
propagation
nodal
processing queueing
dnodal = dproc + dqueue + dtrans +  dprop
A
B
transmission
Introduction: 1-48
Packet delay: four sources
propagation
nodal
processing queueing
dnodal = dproc + dqueue + dtrans +  dprop
A
B
transmission
dtrans: transmission delay:
▪ L: packet length (bits) 
▪ R: link transmission rate (bps)
▪ dtrans = L/R
dprop: propagation delay:
▪ d: length of physical link
▪ s: propagation speed (~2x108 m/sec)
▪ dprop = d/s dtrans and dprop
very different
Introduction: 1-49
Caravan analogy
▪ car ~ bit; caravan ~ packet; toll 
service ~ link transmission
▪ toll booth takes 12 sec to service 
car (bit transmission time)
▪ “propagate” at  100 km/hr
▪ Q: How long until caravan is lined 
up before 2nd toll booth?
▪ time to “push” entire caravan 
through toll booth onto 
highway = 12*10 = 120 sec
▪ time for last car to propagate 
from 1st to 2nd toll both: 
100km/(100km/hr) = 1 hr
▪ A: 62 minutes
toll boothtoll  booth
(aka link)
ten-car caravan
(aka 10-bit packet)
100 km 100 km
toll boothtoll  booth
(aka link)
toll booth
Introduction: 1-50
Caravan analogy
toll boothtoll  booth
(aka router)
ten-car caravan
(aka 10-bit packet)
100 km 100 km
▪ suppose cars now “propagate” at 1000 km/hr
▪ and suppose toll booth now takes one min to service a car
▪ Q: Will cars arrive to 2nd booth before all cars serviced at first booth?
A: Yes!  after 7 min, first car arrives at second booth; three cars still at 
first booth
Introduction: 1-51
Packet queueing delay (revisited)
▪ a: average packet arrival rate
▪ L: packet length (bits)
▪ R: link bandwidth (bit transmission rate)
▪ La/R ~ 0: avg. queueing delay small
▪ La/R -> 1: avg. queueing delay large
▪ La/R > 1: more “work” arriving  is 
more than can be serviced -  average 
delay infinite!
La/R ~ 0
La/R -> 1
traffic intensity = La/R
average  queueing delay
1service rate of bitsR
arrival rate of bitsL a. : “traffic 
intensity”
Introduction: 1-52
“Real” Internet delays and routes
▪ what do “real” Internet delay & loss look like? 
▪ traceroute program: provides delay measurement from 
source to router along end-end Internet path towards 
destination.  For all i:
3 probes
3 probes
3 probes
• sends three packets that will reach router i on path towards 
destination (with time-to-live field value of i)
• router i will return packets to sender
• sender measures time interval between transmission and reply
Introduction: 1-53
Real Internet delays and routes
1  cs-gw (128.119.240.254)  1 ms  1 ms  2 ms
2  border1-rt-fa5-1-0.gw.umass.edu (128.119.3.145)  1 ms  1 ms  2 ms
3  cht-vbns.gw.umass.edu (128.119.3.130)  6 ms 5 ms 5 ms
4  jn1-at1-0-0-19.wor.vbns.net (204.147.132.129)  16 ms 11 ms 13 ms 
5  jn1-so7-0-0-0.wae.vbns.net (204.147.136.136)  21 ms 18 ms 18 ms 
6  abilene-vbns.abilene.ucaid.edu (198.32.11.9)  22 ms  18 ms  22 ms
7  nycm-wash.abilene.ucaid.edu (198.32.8.46)  22 ms  22 ms  22 ms
8  62.40.103.253 (62.40.103.253)  104 ms 109 ms 106 ms
9  de2-1.de1.de.geant.net (62.40.96.129)  109 ms 102 ms 104 ms
10  de.fr1.fr.geant.net (62.40.96.50)  113 ms 121 ms 114 ms
11  renater-gw.fr1.fr.geant.net (62.40.103.54)  112 ms  114 ms  112 ms
12  nio-n2.cssi.renater.fr (193.51.206.13)  111 ms  114 ms  116 ms
13  nice.cssi.renater.fr (195.220.98.102)  123 ms  125 ms  124 ms
14  r3t2-nice.cssi.renater.fr (195.220.98.110)  126 ms  126 ms  124 ms
15  eurecom-valbonne.r3t2.ft.net (193.48.50.54)  135 ms  128 ms  133 ms
16  194.214.211.25 (194.214.211.25)  126 ms  128 ms  126 ms
17  * * *
18  * * *
19  fantasia.eurecom.fr (193.55.113.142)  132 ms  128 ms  136 ms
traceroute: gaia.cs.umass.edu to www.eurecom.fr
* Do some traceroutes from exotic countries at www.traceroute.org
* means no response (probe lost, router not replying)
3 delay measurements from 
gaia.cs.umass.edu to cs-gw.cs.umass.edu 
3 delay measurements
to border1-rt-fa5-1-0.gw.umass.edu 
looks like delays 
decrease! Why?
trans-oceanic link
Introduction: 1-54
Packet loss
▪ queue (aka buffer) preceding link in buffer has finite capacity
A
B
packet being transmittedbuffer (waiting area)
* Check out the Java applet for an interactive animation (on publisher’s website) of queuing and loss
packet arriving to
full buffer is lost
▪ packet arriving to full queue dropped (aka lost)
▪ lost packet may be retransmitted by previous node, by source end 
system, or not at all
Introduction: 1-55
Throughput
▪ throughput: rate (bits/time unit) at which bits are being sent from 
sender to receiver
• instantaneous: rate at given point in time
• average: rate over longer period of time
server, with
file of F bits 
to send to client
link capacity
 Rs bits/sec
link capacity
 Rc bits/secserver sends bits 
(fluid) into pipe
pipe that can carry
fluid at rate
 (Rs bits/sec)
pipe that can carry
fluid at rate
 (Rc bits/sec)
Introduction: 1-56
Throughput
Rs < Rc  What is average end-end throughput?
Rs bits/sec Rc bits/sec
Rs > Rc  What is average end-end throughput?
link on end-end path that constrains  end-end throughput
bottleneck link
Rs bits/sec Rc bits/sec
Introduction: 1-57
Throughput: network scenario
10 connections (fairly) share 
backbone bottleneck link R bits/sec
Rs
Rs
Rs
Rc
Rc
Rc
R
▪ per-connection end-
end throughput: 
min(Rc,Rs,R/10)
▪ in practice: Rc or Rs is often bottleneck
* Check out the online interactive exercises for more 
examples: http://gaia.cs.umass.edu/kurose_ross/
Introduction: 1-58
Chapter 1: roadmap
Introduction: 1-59
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History

Network security
▪ Internet not originally designed with (much) security in 
mind
• original vision: “a group of mutually trusting users attached to a 
transparent network” ☺
• Internet protocol designers playing “catch-up”
• security considerations in all layers!
▪ We now need to think about:
• how bad guys can attack computer networks
• how we can defend networks against attacks
• how to design architectures that are immune to attacks
Introduction: 1-60
Network security
▪ Internet not originally designed with (much) security in 
mind
• original vision: “a group of mutually trusting users attached to a 
transparent network” ☺
• Internet protocol designers playing “catch-up”
• security considerations in all layers!
▪ We now need to think about:
• how bad guys can attack computer networks
• how we can defend networks against attacks
• how to design architectures that are immune to attacks
Introduction: 1-61
Bad guys: packet interception
packet “sniffing”: 
▪ broadcast media (shared Ethernet, wireless)
▪ promiscuous network interface reads/records all packets (e.g., 
including passwords!) passing by
A
B
C
src:B dest:A     payload
Wireshark software used for our end-of-chapter labs is a (free) packet-sniffer
Introduction: 1-62
Bad guys:  fake identity
IP spoofing: injection of packet with false source address
A
B
C
src:B dest:A     payload
Introduction: 1-63
Bad guys: denial of service
target
Denial of Service (DoS): attackers make resources (server, 
bandwidth) unavailable to legitimate traffic by 
overwhelming resource with bogus traffic
1. select target
2. break into hosts 
around the network 
(see botnet)
3. send packets to target 
from compromised 
hosts
Introduction: 1-64
Lines of defense:
▪ authentication: proving you are who you say you are
• cellular networks provides hardware identity via SIM card; no such 
hardware assist in traditional Internet
▪ confidentiality: via encryption
▪ integrity checks: digital signatures prevent/detect tampering
▪ access restrictions:  password-protected VPNs
▪ firewalls: specialized “middleboxes” in access and core 
networks:
▪ off-by-default: filter incoming packets to restrict senders, receivers, 
applications 
▪ detecting/reacting to DOS attacks
… lots more on security (throughout, Chapter 8)
Introduction: 1-65
Chapter 1: roadmap
Introduction: 1-66
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History

Protocol “layers” and reference models
Networks are complex,
with many “pieces”:
▪hosts
▪routers
▪links of various media
▪applications
▪protocols
▪hardware, software
Question: is there any 
hope of organizing 
structure of network?
▪and/or our discussion 
of networks?
Introduction: 1-67
Example: organization of air travel
▪ a series of steps, involving many services
ticket (purchase)
baggage (check)
gates (load)
runway takeoff
airplane routing
ticket (complain)
baggage (claim)
gates (unload)
runway landing
airplane routing
airplane routing
How would you define/discuss the system of airline travel?
end-to-end transfer of person plus baggage
Introduction: 1-68
Example: organization of air travel
ticket (purchase)
baggage (check)
gates (load)
runway takeoff
airplane routing
ticket (complain)
baggage (claim)
gates (unload)
runway landing
airplane routingairplane routing
ticketing service
baggage service
gate service
runway service
routing service
layers: each layer implements a service
▪ via its own internal-layer actions
▪ relying on services provided by layer below
Introduction: 1-69
Why layering?
Approach to designing/discussing complex systems:
▪ explicit structure allows identification, 
relationship of system’s pieces
• layered reference model for discussion
▪ modularization eases maintenance, 
updating of system
• change in layer's service implementation: 
transparent to rest of system
• e.g., change in gate procedure doesn’t 
affect rest of system
Introduction: 1-70
Layered Internet protocol stack
▪ application: supporting network applications
• HTTP , IMAP , SMTP , DNS
▪ transport: process-process data transfer
• TCP , UDP
▪ network: routing of datagrams from source to 
destination
• IP , routing protocols
▪ link: data transfer between neighboring  
network elements
• Ethernet, 802.11 (WiFi), PPP
▪ physical: bits “on the wire”
link
application
network
transport
physical
application
transport
network
link
physical
Introduction: 1-71
Services, Layering and Encapsulation
source
▪ transport-layer protocol encapsulates 
application-layer message, M, with 
transport layer-layer header Ht to create a 
transport-layer segment
• Ht used by transport layer protocol to 
implement its service
application
transport
network
link
physical
destination
application
transport
network
link
physical
Transport-layer protocol transfers M (e.g., reliably) from 
one process to another, using services of network layer
Ht M
Application exchanges messages to implement some 
application service using services of transport layer
M
Introduction: 1-72
Services, Layering and Encapsulation
source
Transport-layer protocol transfers M (e.g., reliably) from 
one process to another, using services of network layer
Ht M
▪ network-layer protocol encapsulates 
transport-layer segment  [Ht | M] with 
network layer-layer header Hn to create a 
network-layer datagram 
• Hn used by network layer protocol to 
implement its service
application
transport
network
link
physical
destination
M
application
transport
network
link
physical
MHtHn
Network-layer protocol transfers transport-layer segment 
[Ht | M] from one host to another, using link layer services
Introduction: 1-73
Services, Layering and Encapsulation
source
Ht M
▪ link-layer protocol encapsulates network 
datagram [Hn| [Ht |M], with link-layer header 
Hl to create a link-layer frame 
application
transport
network
link
physical
destination
M
application
transport
network
link
physical
MHtHn
Link-layer protocol transfers datagram [Hn| [Ht |M] from host to neighboring host, using network-layer services
MHtHnHl
MHtHn
Network-layer protocol transfers transport-layer segment 
[Ht | M] from one host to another, using link layer services
Introduction: 1-74
Encapsulation
Introduction: 1-75
message segment datagram frame
Matryoshka dolls (stacking dolls)
Credit: https://dribbble.com/shots/7182188-Babushka-Boi
Services, Layering and Encapsulation
source
application
transport
network
link
physical
destination
application
transport
network
link
physical
MHtHnHl
MHtHn
Ht M
MMmessage
Ht Msegment
MHtHndatagram
frame MHtHnHl
Introduction: 1-76

network
link
physical
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
Encapsulation: an 
end-end view
source
HtHn M
segment Ht
datagram
destination
HtHnHl M
HtHn M
Ht M
M
 HtHnHl M
HtHn M
HtHn M
HtHnHl M
router
switch
message M
Ht M
Hn
frame
link
physical
Introduction: 1-77
Chapter 1: roadmap
Introduction: 1-78
▪ What is the Internet?
▪ What is a protocol?
▪ Network edge: hosts, access network, 
physical media
▪ Network core: packet/circuit 
switching, internet structure
▪ Performance: loss, delay, throughput
▪ Security
▪ Protocol layers, service models
▪ History

Internet history
▪ 1961: Kleinrock - queueing 
theory shows effectiveness of 
packet-switching
▪ 1964: Baran - packet-switching 
in military nets
▪ 1967: ARPAnet conceived by 
Advanced Research Projects 
Agency
▪ 1969: first ARPAnet node 
operational
▪ 1972: 
• ARPAnet public demo
• NCP (Network Control Protocol) 
first host-host protocol 
• first e-mail program
• ARPAnet has 15 nodes
1961-1972: Early packet-switching principles
Internet history
▪ 1970: ALOHAnet satellite 
network in Hawaii
▪ 1974: Cerf and Kahn - 
architecture for interconnecting 
networks
▪ 1976: Ethernet at Xerox PARC
▪ late70’s: proprietary 
architectures: DECnet, SNA, XNA
▪ 1979: ARPAnet has 200 nodes
1972-1980: Internetworking, new and proprietary networks
Cerf and Kahn’s internetworking 
principles:
▪ minimalism, autonomy - no 
internal changes required to 
interconnect networks
▪ best-effort service model
▪ stateless routing
▪ decentralized control
define today’s Internet architecture
Introduction: 1-80
Internet history
▪ 1983: deployment of TCP/IP
▪ 1982: smtp e-mail protocol 
defined 
▪ 1983: DNS defined for name-
to-IP-address translation
▪ 1985: ftp protocol defined
▪ 1988: TCP congestion control
▪ new national networks: CSnet, 
BITnet, NSFnet, Minitel
▪ 100,000 hosts connected to 
confederation of networks
1980-1990: new protocols, a proliferation of networks
Introduction: 1-81
Internet history
▪ early 1990s: ARPAnet 
decommissioned
▪ 1991: NSF lifts restrictions on 
commercial use of NSFnet 
(decommissioned, 1995)
▪ early 1990s: Web
• hypertext [Bush 1945, Nelson 1960’s]
• HTML, HTTP: Berners-Lee
• 1994: Mosaic, later Netscape
• late 1990s: commercialization of the 
Web
late 1990s – 2000s:
▪ more killer apps: instant 
messaging, P2P file sharing
▪ network security to forefront
▪ est. 50 million host, 100 million+ 
users
▪ backbone links running at Gbps
1990, 2000s: commercialization, the Web, new applications
Introduction: 1-82
Internet history
▪ aggressive deployment of broadband home access (10-100’s Mbps)
▪ 2008: software-defined networking (SDN)
▪ increasing ubiquity of high-speed wireless access: 4G/5G, WiFi
▪ service providers (Google, FB, Microsoft) create their own networks
• bypass commercial Internet to connect “close” to end user, providing 
“instantaneous” access to social media, search, video content, …
▪ enterprises run their services in “cloud” (e.g., Amazon Web Services, 
Microsoft Azure)
▪ rise of smartphones: more mobile than fixed devices on Internet (2017)
▪ ~15B devices attached to Internet (2023, statista.com)
2005-present: scale, SDN, mobility, cloud
Introduction: 1-83
Chapter 1: summary
Introduction: 1-84
We’ve covered a “ton” of material!
▪ Internet overview
▪ what’s a protocol?
▪ network edge, access network, core
• packet-switching versus circuit-
switching
• Internet structure
▪ performance: loss, delay, throughput
▪ layering, service models
▪ security
▪ history
You now have: 
▪ context, overview, 
vocabulary,  “feel” 
of networking
▪ more depth, 
detail, and fun to 
follow!
Additional Chapter 1 slides
Introduction: 1-85
ISO/OSI reference model
Introduction: 1-86
Two layers not found in  Internet 
protocol stack!
▪ presentation: allow applications to 
interpret meaning of data, e.g., encryption, 
compression, machine-specific conventions
▪ session: synchronization, checkpointing, 
recovery of data exchange
▪ Internet stack “missing” these layers!
• these services, if needed, must be 
implemented in application
• needed?
application
presentation
session
transport
network
link
physical
The seven layer OSI/ISO 
reference model
More than seven OSI layers
Introduction: 1-87

Services, Layering and Encapsulation
source
application
transport
network
link
physical
destination
application
transport
network
link
physical
Ht M
M
MHtHn
MHtHnHl
MHtHn
Ht M
M
message
segment
datagram
frame
MHtHnHl
Introduction: 1-88
Wireshark
Introduction: 1-89
Transport (TCP/UDP)
Network (IP)
Link (Ethernet)
Physical
application
(www browser, 
email client)
application
OS
packet
capture
(pcap)
packet
analyzer
copy of all 
Ethernet frames 
sent/received
