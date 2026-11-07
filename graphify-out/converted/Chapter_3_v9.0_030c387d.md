<!-- converted from Chapter_3_v9.0.pdf -->

Chapter 3
Transport Layer
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
Transport Layer: 3-1
Transport layer: overview
Our goal: 
▪ understand principles 
behind transport layer 
services:
• multiplexing, 
demultiplexing
• reliable data transfer
• flow control
• congestion control
▪ learn about Internet transport 
layer protocols:
• UDP: connectionless transport
• TCP: connection-oriented reliable 
transport
• TCP congestion control
Transport Layer: 3-2
Transport layer: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-3

Transport services and protocols
▪ provide logical communication 
between application processes 
running on different hosts
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
application
transport
network
data link
physical
application
transport
network
data link
physical
▪ transport protocols actions in end 
systems:
• sender: breaks application messages 
into segments, passes to  network layer
• receiver: reassembles segments into 
messages, passes to application layer
▪ two transport protocols available to 
Internet applications
• TCP , UDP
Transport Layer: 3-4
Transport vs. network layer services and protocols
household analogy:
12 kids in Ann’s house sending 
letters to 12 kids in Bill’s 
house:
▪ hosts = houses
▪ processes = kids
▪ app messages = letters in 
envelopes
▪ transport protocol = Ann and Bill 
who demux to in-house siblings
▪ network-layer protocol = postal 
service
Transport Layer: 3-5
Transport vs. network layer services and protocols
▪network layer: 
communication between 
hosts
household analogy:
12 kids in Ann’s house sending 
letters to 12 kids in Bill’s 
house:
▪ hosts = houses
▪ processes = kids
▪ app messages = letters in 
envelopes
▪ transport protocol = Ann and Bill 
who demux to in-house siblings
▪ network-layer protocol = postal 
service
Transport Layer: 3-6
▪transport layer: 
communication between 
processes 
• relies on, enhances, network 
layer services
physical
link
network (IP)
application
physical
link
network (IP)
application
transport
Transport Layer Actions
Sender:
app. msg▪ is passed an application-
layer message
▪ determines segment 
header fields values
▪ creates segment
▪ passes segment to IP
transport ThTh app. msg
Transport Layer: 3-7
physical
link
network (IP)
application
physical
link
network (IP)
application
transport
Transport Layer Actions
transport
Receiver:
app.  msg ▪ extracts application-layer 
message
▪ checks header values
▪ receives segment from IP
Th app. msg
▪ demultiplexes message up 
to application via socket
Transport Layer: 3-8
Two principal Internet transport protocols
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
application
transport
network
data link
physical
application
transport
network
data link
physical
▪ TCP: Transmission Control Protocol
• reliable, in-order delivery
• congestion control 
• flow control
• connection setup
▪ UDP: User Datagram Protocol
• unreliable, unordered delivery
• no-frills extension of “best-effort” IP
▪ services not available: 
• delay guarantees
• bandwidth guarantees
Transport Layer: 3-9
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-10

Multiplexing/demultiplexing
process
socket
use header info to deliver
received segments to correct 
socket
demultiplexing as receiver:
transport
application
physical
link
network
P2P1
transport
application
physical
link
network
P4
transport
application
physical
link
network
P3
handle data from multiple
sockets, add transport header 
(later used for demultiplexing)
multiplexing as sender:
Transport Layer: 3-11
transport
physical
link
network transport
application
physical
link
network
transport
application
physical
link
network
HTTP server
client
HTTP msg
Transport Layer: 3-12
HTTP msgHt
HTTP msgHtHn
HTTP msgHtHn
HTTP msgHtHn
transport
physical
link
network transport
application
physical
link
network
transport
application
physical
link
network
client
HTTP msgHt
HTTP msg
Transport Layer: 3-13
HTTP msg
Q: how did transport layer know to deliver message to Firefox 
browser process rather then Netflix process or Skype process?
?
de-multiplexing
?
de-multiplexing
transport
application
Demultiplexing
multiplexing
multiplexing
transport
application
Multiplexing
How demultiplexing works
▪ host receives IP datagrams
• each datagram has source IP 
address, destination IP address
• each datagram carries one 
transport-layer segment
• each segment has source, 
destination port number 
▪ host uses IP addresses & port 
numbers to direct segment to 
appropriate socket
source port # dest port #
32 bits
application
data 
(payload)
other header fields
TCP/UDP segment format
Transport Layer: 3-20
Connectionless demultiplexing
Recall: 
▪ when creating socket, must 
specify host-local port #:
  DatagramSocket mySocket1        
= new DatagramSocket(12534);
when receiving host receives 
UDP segment:
• checks destination port # in 
segment
• directs UDP segment to 
socket with that port #
▪ when creating datagram to 
send into UDP socket, must 
specify
• destination IP address
• destination port #
IP/UDP datagrams with same dest. 
port #, but different source IP 
addresses and/or source port 
numbers will be directed to same 
socket at receiving host
Transport Layer: 3-21
transport
application
physical
link
network
P3
transport
application
physical
link
network
P1
transport
application
physical
link
network
P4
mySocket = 
socket(AF_INET,SOCK_DGRAM)
mySocket.bind(myaddr,9157);
source port: 9157
dest port: 6428
source port: 6428
dest port: 9157
source port: ?
dest port: ?
source port: ?
dest port: ?
A
B
C
D
mySocket = 
socket(AF_INET,SOCK_DGRAM)
mySocket.bind(myaddr,5775);
mySocket = 
socket(AF_INET,SOCK_DGRAM)
mySocket.bind(myaddr,6428);
Connectionless demultiplexing: an example
Connection-oriented demultiplexing
▪ TCP socket identified by 
4-tuple: 
• source IP address
• source port number
• dest IP address
• dest port number
▪ server may support many 
simultaneous TCP sockets:
• each socket identified by its 
own 4-tuple
• each socket associated with 
a different connecting client
▪ demux: receiver uses all 
four values (4-tuple) to 
direct segment to 
appropriate socket
Transport Layer: 3-23
Connection-oriented demultiplexing: example
transport
application
physical
link
network
P1
transport
application
physical
link
P4
transport
application
physical
link
network
P2
host: IP 
address A
host: IP 
address C
network
P6P5
P3
source IP,port: A,9157
dest IP, port: B,80
source IP,port: B,80
dest IP,port: A,9157 source IP,port: C,5775
dest IP,port: B,80
source IP,port: C,9157
dest IP,port: B,80
server: IP 
address B
Three segments, all destined to IP address: B,
 dest port: 80 are demultiplexed to different sockets
Transport Layer: 3-24
Summary
▪ Multiplexing, demultiplexing: based on segment, datagram 
header field values
▪ UDP: demultiplexing using destination port number (only)
▪ TCP: demultiplexing using 4-tuple: source and destination IP 
addresses, and port numbers
▪ Multiplexing/demultiplexing happen at all layers
Transport Layer: 3-25
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-26

UDP: User Datagram Protocol
▪ “no frills,” “bare bones” 
Internet transport protocol
▪ “best effort” service, UDP 
segments may be:
• lost
• delivered out-of-order to app
▪ no connection 
establishment (which can 
add RTT delay)
▪ simple: no connection state 
at sender, receiver
▪ small header size
▪ no congestion control
▪ UDP can blast away as fast as 
desired!
▪ can function in the face of 
congestion
Why is there a UDP?
▪ connectionless:
• no handshaking between UDP 
sender, receiver
• each UDP segment handled 
independently of others
Transport Layer: 3-27
UDP: User Datagram Protocol
▪ UDP use:
▪ streaming multimedia apps (loss tolerant, rate sensitive)
▪ DNS
▪ SNMP
▪ HTTP/3
▪ if reliable transfer needed over UDP (e.g., HTTP/3): 
▪ add needed reliability at application layer
▪ add congestion control at application layer
Transport Layer: 3-28
UDP: User Datagram Protocol [RFC 768]
Transport Layer: 3-29
SNMP serverSNMP client
transport
(UDP)
physical
link
network (IP)
application
UDP: Transport Layer Actions
transport
(UDP)
physical
link
network (IP)
application
Transport Layer: 3-30
SNMP serverSNMP client
transport
(UDP)
physical
link
network (IP)
application
transport
(UDP)
physical
link
network (IP)
application
UDP: Transport Layer Actions
UDP sender actions:
SNMP msg▪ is passed an application-
layer message
▪ determines UDP segment 
header fields values
▪ creates UDP segment
▪ passes segment to IP
UDPhUDPh SNMP msg
Transport Layer: 3-31
SNMP serverSNMP client
transport
(UDP)
physical
link
network (IP)
application
transport
(UDP)
physical
link
network (IP)
application
UDP: Transport Layer Actions
UDP receiver actions:
SNMP msg
▪ extracts application-layer 
message
▪ checks UDP checksum 
header value
▪ receives segment from IP
UDPh SNMP msg ▪ demultiplexes message up 
to application via socket
Transport Layer: 3-32
UDP segment header
source port # dest port #
32 bits
application
data 
(payload)
UDP segment format
length checksum
length, in bytes of 
UDP segment, 
including header
data to/from 
application layer
Transport Layer: 3-33
UDP checksum
Transmitted:            5               6                11
Goal: detect errors (i.e., flipped bits) in transmitted segment
Received:            4               6                11
1st number 2nd number sum
receiver-computed 
checksum
sender-computed 
checksum (as received)
=
Transport Layer: 3-34
Internet checksum
sender:
▪ treat contents of UDP 
segment (including UDP header 
fields and IP addresses) as 
sequence of 16-bit integers
▪ checksum: addition (one’s 
complement sum) of segment 
content
▪ checksum value put into 
UDP checksum field
receiver:
▪ compute checksum of received 
segment
▪ check if computed checksum equals 
checksum field value:
• not equal - error detected
• equal - no error detected. But maybe 
errors nonetheless? More later ….
Goal: detect errors (i.e., flipped bits) in transmitted segment
Transport Layer: 3-35
Internet checksum: an example
example: add two 16-bit integers
sum
checksum
Note: when adding numbers, a carryout from the most significant bit needs to be 
added to the result
* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive/
1 1 1 0 0 1 1 0 0 1 1 0 0 1 1 0
1 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
1 1 0 1 1 1 0 1 1 1 0 1 1 1 0 1 1wraparound
1 0 1 1 1 0 1 1 1 0 1 1 1 1 0 0
0 1 0 0 0 1 0 0 0 1 0 0 0 0 1 1
Transport Layer: 3-36
Internet checksum: weak protection!
example: add two 16-bit integers
sum
checksum
1 1 1 0 0 1 1 0 0 1 1 0 0 1 1 0
1 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
1 1 0 1 1 1 0 1 1 1 0 1 1 1 0 1 1wraparound
1 0 1 1 1 0 1 1 1 0 1 1 1 1 0 0
0 1 0 0 0 1 0 0 0 1 0 0 0 0 1 1
0 1 
1 0 
Even though 
numbers have 
changed (bit 
flips), no change 
in checksum!
Transport Layer: 3-37
Summary: UDP
▪ “no frills” protocol: 
• segments may be lost, delivered out of order
• best effort service: “send and hope for the best”
▪ UDP has its plusses:
• no setup/handshaking needed (no RTT incurred)
• can function when network service is compromised
• helps with reliability (checksum)
▪ build additional functionality on top of UDP in application layer 
(e.g., HTTP/3)
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-39

Principles of reliable data transfer 
sending 
process
data
receiving 
process
data
reliable channel
application
transport
reliable service abstraction
Transport Layer: 3-40
Principles of reliable data transfer 
sending 
process
data
receiving 
process
dataapplication
transport
reliable service implementation
unreliable channel
network
transport
sender-side of
reliable data 
transfer protocol
receiver-side
of reliable data 
transfer protocol
sending 
process
data
receiving 
process
data
reliable channel
application
transport
reliable service abstraction
Transport Layer: 3-41
Principles of reliable data transfer 
sending 
process
data
receiving 
process
dataapplication
transport
reliable service implementation
unreliable channel
network
transport
sender-side of
reliable data 
transfer protocol
receiver-side
of reliable data 
transfer protocolComplexity of reliable data transfer protocol  will depend 
(strongly) on characteristics of 
unreliable channel (lose, 
corrupt, reorder data?)
Transport Layer: 3-42
Principles of reliable data transfer 
sending 
process
data
receiving 
process
dataapplication
transport
reliable service implementation
unreliable channel
network
transport
sender-side of
reliable data 
transfer protocol
receiver-side
of reliable data 
transfer protocolSender, receiver do not know 
the “state” of each other, e.g., 
was a message received?
▪ unless communicated via a 
message
Transport Layer: 3-43
Reliable data transfer protocol (rdt): interfaces
sending 
process
data
receiving 
process
data
unreliable channel
sender-side
implementation of 
rdt reliable data 
transfer protocol
receiver-side
implementation of 
rdt reliable data 
transfer protocol
rdt_send()
udt_send() rdt_rcv()
deliver_data()
dataHeader dataHeader
rdt_send(): called from above, 
(e.g., by app.). Passed data to 
deliver to receiver upper layer
udt_send(): called by rdt
to transfer packet over 
unreliable channel to receiver
rdt_rcv(): called when packet 
arrives on receiver side of 
channel
deliver_data(): called by rdt 
to deliver data to upper layer
Bi-directional communication over 
unreliable channel
data
packet
Transport Layer: 3-44
Reliable data transfer: getting started
We will:
▪ incrementally develop sender, receiver sides of reliable data transfer 
protocol (rdt)
▪ consider only unidirectional data transfer
• but control info will flow in both directions!
state
1
state
2
event causing state transition
actions taken on state transition
state: when in this “state” 
next state uniquely 
determined by next 
event
event
actions
▪ use finite state machines (FSM)  to specify sender, receiver
Transport Layer: 3-45
rdt1.0: reliable transfer over a reliable channel
▪ underlying channel perfectly reliable
• no bit errors
• no loss of packets
packet = make_pkt(data)
udt_send(packet)
rdt_send(data)
extract (packet,data)
deliver_data(data)
rdt_rcv(packet)Wait for 
call from 
below
receiver
▪ separate FSMs for sender, receiver:
• sender sends data into underlying channel
• receiver reads data from underlying channel
sender
Wait for 
call from 
above
Transport Layer: 3-46
rdt2.0: channel with bit errors
▪ underlying channel may flip bits in packet
• checksum (e.g., Internet checksum) to detect bit errors
▪ the question: how to recover from errors?
How do humans recover from “errors” during conversation?
Transport Layer: 3-47
rdt2.0: channel with bit errors
▪ underlying channel may flip bits in packet
• checksum to detect bit errors
▪ the question: how to recover from errors?
• acknowledgements (ACKs): receiver explicitly tells sender that pkt 
received OK
• negative acknowledgements (NAKs): receiver explicitly tells sender 
that pkt had errors
• sender retransmits pkt on receipt of NAK
stop and wait
sender sends one packet,  then waits for receiver  response
Transport Layer: 3-48
rdt2.0: FSM specifications
Wait for 
call from 
above
udt_send(sndpkt)
Wait for 
ACK or 
NAK
udt_send(NAK)
rdt_rcv(rcvpkt) && corrupt(rcvpkt)
Wait for 
call from 
below
extract(rcvpkt,data)
deliver_data(data)
udt_send(ACK)
rdt_rcv(rcvpkt) &&  notcorrupt(rcvpkt)
snkpkt = make_pkt(data, checksum)
udt_send(sndpkt)
rdt_send(data)
rdt_rcv(rcvpkt) && isACK(rcvpkt)

sender
receiver
rdt_rcv(rcvpkt) &&
   isNAK(rcvpkt)
Transport Layer: 3-49
rdt2.0: FSM specification
Wait for 
call from 
above
udt_send(sndpkt)
Wait for 
ACK or 
NAK
udt_send(NAK)
rdt_rcv(rcvpkt) && corrupt(rcvpkt)
Wait for 
call from 
below
extract(rcvpkt,data)
deliver_data(data)
udt_send(ACK)
rdt_rcv(rcvpkt) &&  notcorrupt(rcvpkt)
snkpkt = make_pkt(data, checksum)
udt_send(sndpkt)
rdt_send(data)
rdt_rcv(rcvpkt) && isACK(rcvpkt)

sender
receiver
Note: “state” of receiver (did the receiver get my 
message correctly?) isn’t known to sender unless 
somehow communicated from receiver to sender
▪ that’s why we need a protocol!
rdt_rcv(rcvpkt) &&
   isNAK(rcvpkt)
isNAK(rcvpkt)
isACK(rcvpkt)
Transport Layer: 3-50
rdt2.0: operation with no errors
Wait for 
call from 
above
snkpkt = make_pkt(data, checksum)
udt_send(sndpkt)
udt_send(sndpkt)
udt_send(NAK)
Wait for 
ACK or 
NAK
Wait for 
call from 
below
rdt_send(data)
rdt_rcv(rcvpkt) && corrupt(rcvpkt)
rdt_rcv(rcvpkt) && isACK(rcvpkt)

extract(rcvpkt,data)
deliver_data(data)
udt_send(ACK)
rdt_rcv(rcvpkt) &&  notcorrupt(rcvpkt)
sender
receiver
rdt_rcv(rcvpkt) &&
   isNAK(rcvpkt)
Transport Layer: 3-51
rdt2.0: corrupted packet scenario
Wait for 
call from 
above
snkpkt = make_pkt(data, checksum)
udt_send(sndpkt)
udt_send(sndpkt)
rdt_rcv(rcvpkt) &&
   isNAK(rcvpkt)Wait for 
ACK or 
NAK
Wait for 
call from 
below
rdt_send(data)
udt_send(NAK)
rdt_rcv(rcvpkt) && corrupt(rcvpkt)
extract(rcvpkt,data)
deliver_data(data)
udt_send(ACK)
rdt_rcv(rcvpkt) &&  notcorrupt(rcvpkt)
rdt_rcv(rcvpkt) && isACK(rcvpkt)

sender
receiver
Transport Layer: 3-52
rdt2.0 has a fatal flaw!
what happens if ACK/NAK 
corrupted?
▪ sender doesn’t know what 
happened at receiver!
▪ can’t just retransmit: possible 
duplicate
handling duplicates: 
▪ sender retransmits current pkt 
if ACK/NAK corrupted
▪ sender adds sequence number 
to each pkt
▪ receiver discards (doesn’t 
deliver up) duplicate pkt
stop and wait
sender sends one packet,  then 
waits for receiver  response
Transport Layer: 3-53
rdt2.1: sender, handling garbled ACK/NAKs
Wait for 
call 0 from 
above
Wait for 
ACK or 
NAK 0
sndpkt = make_pkt(0, data, checksum)
udt_send(sndpkt)
rdt_send(data)
udt_send(sndpkt)
rdt_rcv(rcvpkt) &&  
(corrupt(rcvpkt) || 
isNAK(rcvpkt) )
sndpkt = make_pkt(1, data, checksum)
udt_send(sndpkt)
rdt_send(data)
udt_send(sndpkt)
rdt_rcv(rcvpkt) 
&& (corrupt(rcvpkt) ||
isNAK(rcvpkt) )
Wait for
 call 1 from 
above
Wait for 
ACK or 
NAK 1
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt) 

rdt_rcv(rcvpkt)  
&& notcorrupt(rcvpkt) && 
isACK(rcvpkt) 

Transport Layer: 3-54
rdt2.1: receiver, handling garbled ACK/NAKs
Wait for 
0 from 
below
rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) 
  && has_seq1(rcvpkt) 
extract(rcvpkt,data)
deliver_data(data)
sndpkt = make_pkt(ACK, chksum)
udt_send(sndpkt)
Wait for 
1 from 
below
rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) 
  && has_seq0(rcvpkt) 
extract(rcvpkt,data)
deliver_data(data)
sndpkt = make_pkt(ACK, chksum)
udt_send(sndpkt)
sndpkt = make_pkt(NAK, chksum)
udt_send(sndpkt)
rdt_rcv(rcvpkt) && (corrupt(rcvpkt)
rdt_rcv(rcvpkt) && 
   not corrupt(rcvpkt) &&
   has_seq0(rcvpkt)
sndpkt = make_pkt(ACK, chksum)
udt_send(sndpkt)
rdt_rcv(rcvpkt) && 
   not corrupt(rcvpkt) &&
   has_seq1(rcvpkt)
sndpkt = make_pkt(ACK, chksum)
udt_send(sndpkt)
rdt_rcv(rcvpkt) && (corrupt(rcvpkt)
sndpkt = make_pkt(NAK, chksum)
udt_send(sndpkt)
Transport Layer: 3-55
rdt2.1: discussion
sender:
▪ seq # added to pkt
▪ two seq. #s (0,1) will suffice.  
Why?
▪ must check if received ACK/NAK 
corrupted 
▪ twice as many states
• state must “remember” whether 
“expected” pkt should have seq # 
of 0 or 1 
receiver:
▪ must check if received packet 
is duplicate
• state indicates whether 0 or 1 is 
expected pkt seq #
▪ note: receiver can not know if 
its last ACK/NAK received OK 
at sender
Transport Layer: 3-56
rdt2.2: a NAK-free protocol
▪ same functionality as rdt2.1, using ACKs only
▪ instead of NAK, receiver sends ACK for last pkt received OK
• receiver must explicitly include seq # of pkt being ACKed 
▪ duplicate ACK at sender results in same action as NAK: 
retransmit current pkt
As we will see, TCP uses this approach to be NAK-free
Transport Layer: 3-57
rdt2.2: sender, receiver fragments
Wait for 
call 0 from 
above
sndpkt = make_pkt(0, data, checksum)
udt_send(sndpkt)
rdt_send(data)
udt_send(sndpkt)
rdt_rcv(rcvpkt) &&  
( corrupt(rcvpkt) ||
  isACK(rcvpkt,1) )
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt,0) 
Wait for 
ACK
0
sender FSM
fragment
rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) 
  && has_seq1(rcvpkt) 
extract(rcvpkt,data)
deliver_data(data)
sndpkt = make_pkt(ACK1, chksum)
udt_send(sndpkt)
Wait for 
0 from 
below
rdt_rcv(rcvpkt) && 
   (corrupt(rcvpkt) ||
     has_seq1(rcvpkt))
udt_send(sndpkt)
receiver FSM
fragment

Transport Layer: 3-58
rdt3.0: channels with errors and loss
New channel assumption: underlying channel can also lose 
packets (data, ACKs)
• checksum, sequence #s, ACKs, retransmissions will be of help … 
but not quite enough
Q: How do humans handle lost sender-to-
receiver words in conversation?
Transport Layer: 3-59
rdt3.0: channels with errors and loss
Approach: sender waits “reasonable” amount of time for ACK 
▪ retransmits if no ACK received in this time
▪ if pkt (or ACK) just delayed (not lost):
• retransmission will be  duplicate, but seq #s already handles this!
• receiver must specify seq # of packet being ACKed
timeout
▪ use countdown timer to interrupt after “reasonable” amount 
of time
Transport Layer: 3-60
rdt3.0 sender
Wait 
for 
ACK0
sndpkt = make_pkt(0, data, checksum)
udt_send(sndpkt)
start_timer
rdt_send(data)
Wait for 
call 1 from 
above
sndpkt = make_pkt(1, data, checksum)
udt_send(sndpkt)
start_timer
rdt_send(data)
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt,0) 
stop_timer
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt,1) 
stop_timer
Wait for 
call 0 from 
above
Wait 
for 
ACK1
Transport Layer: 3-61
rdt3.0 sender
Wait 
for 
ACK0
sndpkt = make_pkt(0, data, checksum)
udt_send(sndpkt)
start_timer
rdt_send(data)
Wait for 
call 1 from 
above
sndpkt = make_pkt(1, data, checksum)
udt_send(sndpkt)
start_timer
rdt_send(data)
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt,0) 
stop_timer
rdt_rcv(rcvpkt)   
&& notcorrupt(rcvpkt) 
&& isACK(rcvpkt,1) 
stop_timer
udt_send(sndpkt)
start_timer
timeoutWait for call 0 from 
above
Wait 
for 
ACK1

rdt_rcv(rcvpkt)
rdt_rcv(rcvpkt) &&  
( corrupt(rcvpkt) ||
isACK(rcvpkt,1) )
rdt_rcv(rcvpkt)

udt_send(sndpkt)
start_timer
timeout
rdt_rcv(rcvpkt) &&  
( corrupt(rcvpkt) ||
isACK(rcvpkt,0) )

Transport Layer: 3-62
rdt3.0 in action
sender receiver
rcv pkt1
rcv pkt0
send ack0
send ack1
send ack0
rcv ack0
send pkt0
send pkt1
rcv ack1
send pkt0
rcv pkt0
pkt0
pkt0
pkt1
ack1
ack0
ack0
(a) no loss
sender receiver
rcv pkt1
rcv pkt0
send ack0
send ack1
send ack0
rcv ack0
send pkt0
send pkt1
rcv ack1
send pkt0
rcv pkt0
pkt0
pkt0
ack1
ack0
ack0
(b) packet loss
pkt1
X
loss
pkt1
timeout
resend pkt1
Transport Layer: 3-63
rdt3.0 in action
rcv pkt1
send ack1
(detect duplicate)
pkt1
sender receiver
rcv pkt1
rcv pkt0
send ack0
send ack1
send ack0
rcv ack0
send pkt0
send pkt1
rcv ack1
send pkt0
rcv pkt0
pkt0
pkt0
ack1
ack0
ack0
(c) ACK loss
ack1
X
loss
pkt1
timeout
resend pkt1
rcv pkt1
send ack1
(detect duplicate)
pkt1
sender receiver
rcv pkt1
send ack0
rcv ack0
send pkt1
send pkt0
rcv pkt0pkt0
ack0
(d) premature timeout/ delayed ACK
pkt1
timeout
resend pkt1
ack1
ack1
send ack1send pkt0 rcv ack1 pkt0
rcv pkt0
send ack0ack0
pkt1
(ignore)
rcv ack1
Transport Layer: 3-64
Performance of rdt3.0 (stop-and-wait)
▪ example: 1 Gbps link, 15 ms prop. delay, 8000 bit packet
▪U sender: utilization – fraction of time sender busy sending
Dtrans = L R 8000 bits 109 bits/sec= = 8 microsecs
• time to transmit packet into channel:
Transport Layer: 3-65
rdt3.0: stop-and-wait operation
first packet bit transmitted, t = 0
sender receiver
RTT 
first packet bit arrives
last packet bit arrives, send ACK
ACK arrives, send next 
packet, t = RTT + L / R
Transport Layer: 3-66
rdt3.0: stop-and-wait operation
sender receiver
Usender= L / R RTT
RTT 
L/R
+ L / R
= 0.00027
= .008 30.008
▪ rdt 3.0 protocol performance stinks!
▪ Protocol limits performance of underlying infrastructure (channel)
Transport Layer: 3-67
rdt3.0: pipelined protocols operation
pipelining: sender allows multiple, “in-flight”, yet-to-be-acknowledged 
packets
• range of sequence numbers must be increased
• buffering at sender and/or receiver
Transport Layer: 3-68
Pipelining: increased utilization
first packet bit transmitted, t = 0
sender receiver
RTT 
last bit transmitted, t = L / R
first packet bit arrives
last packet bit arrives, send ACK
ACK arrives, send next 
packet, t = RTT + L / R
last bit of 2nd packet arrives, send ACK
last bit of 3rd packet arrives, send ACK
3-packet pipelining increases
 utilization by a factor of 3!
 
U sender = .0024 30.008 = 0.00081  3L / R RTT + L / R = 
Transport Layer: 3-69
Go-Back-N: sender
▪ sender: “window” of up to N, consecutive transmitted but unACKed pkts 
• k-bit seq # in pkt header
▪ cumulative ACK: ACK(n): ACKs all packets up to, including seq # n 
• on receiving ACK(n): move window forward to begin at n+1
▪ timer for oldest in-flight packet
▪ timeout(n): retransmit packet n and all higher seq # packets in window
Transport Layer: 3-70
Go-Back-N: receiver
▪ ACK-only: always send ACK for correctly-received packet so far, with 
highest in-order seq #
• may generate duplicate ACKs
• need only remember rcv_base
▪ on receipt of out-of-order packet: 
• can discard (don’t buffer) or buffer: an implementation decision
• re-ACK pkt with highest in-order seq #
rcv_base
received and ACKed
Out-of-order: received but not  ACKed
Not received
Receiver view of sequence number space:
… …
Transport Layer: 3-71
Go-Back-N in action
send  pkt0
send  pkt1
send  pkt2
send  pkt3
(wait)
sender receiver
receive pkt0, send ack0
receive pkt1, send ack1
 
receive pkt3, discard, 
           (re)send ack1
send  pkt2
send  pkt3
send  pkt4
send  pkt5
Xloss
pkt 2 timeout
receive pkt4, discard, 
           (re)send ack1
receive pkt5, discard, 
           (re)send ack1
rcv pkt2, deliver, send ack2
rcv pkt3, deliver, send ack3
rcv pkt4, deliver, send ack4
rcv pkt5, deliver, send ack5
ignore duplicate ACK
sender window (N=4)
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
rcv ack0, send pkt40 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 rcv ack1, send pkt5
Transport Layer: 3-72
Selective repeat: the approach
▪pipelining: multiple packets in flight
▪receiver individually ACKs all correctly received packets
• buffers packets, as needed, for in-order delivery to upper layer
▪sender:
• maintains (conceptually) a timer for each unACKed pkt
• timeout: retransmits single unACKed packet  associated with timeout
• maintains (conceptually) “window” over N consecutive seq #s
• limits pipelined, “in flight” packets to be within this window
Transport Layer: 3-73
Selective repeat: sender, receiver windows
Transport Layer: 3-74
Selective repeat: sender and receiver
data from above:
▪ if next available seq # in 
window, send packet
timeout(n):
▪ resend packet n, restart timer
ACK(n) in [sendbase,sendbase+N-1]:
▪ mark packet n as received
▪ if n smallest unACKed packet, 
advance window base to next 
unACKed seq # 
sender
packet n in [rcvbase, rcvbase+N-1]
▪ send ACK(n)
▪ out-of-order: buffer
▪ in-order: deliver (also deliver 
buffered, in-order packets), 
advance window to next not-yet-
received packet
packet n in [rcvbase-N,rcvbase-1]
▪ ACK(n)
otherwise: 
▪ ignore 
receiver
Transport Layer: 3-75
Selective Repeat in action
send  pkt0
send  pkt1
send  pkt2
send  pkt3
(wait)
sender receiver
send  pkt2
(but not 3,4,5)
Xloss
pkt 2 timeout
sender window (N=4)
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
rcv ack0, send pkt40 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 
0 1 2 3 4 5 6 7 8 rcv ack1, send pkt5
receive pkt0, send ack0
receive pkt1, send ack1
 
receive pkt3, buffer, 
           send ack3
record ack3 arrived
receive pkt4, buffer, 
           send ack4
receive pkt5, buffer, 
           send ack5
rcv pkt2; deliver pkt2,
pkt3, pkt4, pkt5; send ack2
Q: what happens when ack2 arrives?
Transport Layer: 3-76
Selective repeat: 
a dilemma!
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
pkt0
pkt1
pkt2
0 1 2 3 0 1 2 pkt0
timeout
retransmit pkt0
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
X
X
X
will accept packet
with seq number 0
(b) oops!
receiver window
(after receipt)
sender window
(after receipt)
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
pkt0
pkt1
pkt2
0 1 2 3 0 1 2
pkt0
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
X
will accept packet
with seq number 0
0 1 2 3 0 1 2 pkt3
(a) no problem
example: 
▪ seq #s: 0, 1, 2, 3 (base 4 counting)
▪ window size=3
Transport Layer: 3-77
Selective repeat: 
a dilemma!
Q: what relationship is needed 
between sequence # size and 
window size to avoid problem 
in scenario (b)?
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
pkt0
pkt1
pkt2
0 1 2 3 0 1 2 pkt0
timeout
retransmit pkt0
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
X
X
X
will accept packet
with seq number 0
(b) oops!
receiver window
(after receipt)
sender window
(after receipt)
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
pkt0
pkt1
pkt2
0 1 2 3 0 1 2
pkt0
0 1 2 3 0 1 2
0 1 2 3 0 1 2
0 1 2 3 0 1 2
X
will accept packet
with seq number 0
0 1 2 3 0 1 2 pkt3
(a) no problem
example: 
▪ seq #s: 0, 1, 2, 3 (base 4 counting)
▪ window size=3
▪ receiver can’t 
see sender side
▪ receiver 
behavior 
identical in both 
cases!
▪ something’s 
(very) wrong!
Transport Layer: 3-78
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
• segment structure
• reliable data transfer
• flow control
• connection management
▪ Principles of congestion control
▪ TCP congestion control
Transport Layer: 3-79

TCP: overview  RFCs: 793,1122, 2018, 5681, 7323
▪ cumulative ACKs
▪ pipelining:
• TCP congestion and flow control 
set window size
▪ connection-oriented: 
• handshaking (exchange of control 
messages) initializes sender, 
receiver state before data exchange
▪ flow controlled:
• sender will not overwhelm receiver
▪ point-to-point:
• one sender, one receiver 
▪ reliable, in-order byte 
steam:
• no “message boundaries"
▪ full duplex data:
• bi-directional data flow in 
same connection
• MSS: maximum segment size
Transport Layer: 3-80
TCP segment structure
source port # dest port #
32 bits
not
used receive window flow control: # bytes 
receiver willing to accept
sequence number
segment seq  #: counting 
bytes of data into bytestream 
(not segments!)
application
data 
(variable length)
data sent by 
application into 
TCP socket
A
acknowledgement number
ACK: seq # of next expected 
byte; A bit: this is an ACK
options (variable length)
TCP options
head
lenlength (of TCP header)
checksumInternet checksum
RST, SYN, FIN: connection 
management
FSR
Urg data pointer
PUC E
C, E: congestion notification
Transport Layer: 3-81
TCP sequence numbers, ACKs
Sequence numbers:
• byte stream “number” of 
first byte in segment’s data
source port # dest port #
sequence number
acknowledgement number
checksum
rwnd
urg pointer
outgoing segment from receiver
A
sent 
ACKed
sent, not-
yet ACKed
(“in-flight”)
usable
but not 
yet sent
not 
usable
window size
 N
sender sequence number space 
source port # dest port #
sequence number
acknowledgement number
checksum
rwnd
urg pointer
outgoing segment from sender
Acknowledgements:
• seq # of next byte expected 
from other side
• cumulative ACK
Q: how receiver handles out-of-
order segments
• A: TCP spec doesn’t say, - up 
to implementor
Transport Layer: 3-82
TCP sequence numbers, ACKs
host ACKs receipt 
of echoed ‘C’
host ACKs receipt 
of‘C’, echoes back ‘C’
simple telnet scenario
Host BHost A
User types‘C’
Seq=42, ACK=79, data = ‘C’
Seq=79, ACK=43, data = ‘C’
Seq=43, ACK=80
Transport Layer: 3-83
TCP round trip time, timeout
Q: how to set TCP timeout 
value?
▪ longer than RTT, but RTT varies!
▪ too short: premature timeout, 
unnecessary retransmissions
▪ too long: slow reaction to 
segment loss
Q: how to estimate RTT?
▪SampleRTT:measured time 
from segment transmission until 
ACK receipt
• ignore retransmissions
▪SampleRTT will vary, want 
estimated RTT “smoother”
• average several recent 
measurements, not just current 
SampleRTT
Transport Layer: 3-84
TCP round trip time, timeout
EstimatedRTT = (1- )*EstimatedRTT + *SampleRTT
▪ exponential weighted moving average (EWMA)
▪ influence of past sample decreases exponentially fast
▪ typical value:  = 0.125
RTT: gaia.cs.umass.edu to fantasia.eurecom.fr
100
150
200
250
300
350
1 8 15 22 29 36 43 50 57 64 71 78 85 92 99 106
time (seconnds)
RTT (milliseconds)
SampleRTT Estimated RTT
RTT (milliseconds)
RTT: gaia.cs.umass.edu to fantasia.eurecom.fr
sampleRTT
EstimatedRTT
time (seconds)
Transport Layer: 3-85
TCP round trip time, timeout
▪ timeout interval: EstimatedRTT plus “safety margin”
• large variation in  EstimatedRTT: want a larger safety margin
TimeoutInterval = EstimatedRTT + 4*DevRTT
estimated RTT “safety margin”
* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive/
DevRTT = (1-)*DevRTT + *|SampleRTT-EstimatedRTT|
(typically,  = 0.25)
▪DevRTT: EWMA of SampleRTT deviation from EstimatedRTT: 
Transport Layer: 3-86
TCP Sender (simplified)
event: data received from 
application
▪ create segment with seq #
▪ seq # is byte-stream number 
of first data byte in  segment
▪ start timer if not already 
running 
• think of timer as for oldest 
unACKed segment
• expiration interval: 
TimeOutInterval 
event: timeout
▪ retransmit segment that 
caused timeout
▪ restart timer
 
event: ACK received 
▪ if ACK acknowledges 
previously unACKed segments
• update what is known to be 
ACKed
• start timer if there are  still 
unACKed segments
Transport Layer: 3-87
TCP Receiver: ACK generation [RFC 5681]
Event at receiver
arrival of in-order segment with
expected seq #. All data up to
expected seq # already ACKed
arrival of in-order segment with
expected seq #. One other 
segment has ACK pending
arrival of out-of-order segment
higher-than-expect seq. # .
Gap detected
arrival of segment that 
partially or completely fills gap
TCP receiver action
delayed ACK. Wait up to 500ms
for next segment. If no next segment,
send ACK
immediately send single cumulative 
ACK, ACKing both in-order segments 
immediately send duplicate ACK (acking
 last correctly received in order byte), 
indicating seq. # of next expected byte
immediate send ACK, provided that
segment starts at lower end of gap
Transport Layer: 3-88
TCP: retransmission scenarios
lost ACK scenario
Host BHost A
Seq=92, 8 bytes of data
Seq=92, 8 bytes of data
ACK=100
X
ACK=100
timeout
premature timeout
Host BHost A
Seq=92,  8
bytes of data
ACK=120
timeout
ACK=100
ACK=120
SendBase=100
SendBase=120
SendBase=120
Seq=92, 8 bytes of data
Seq=100, 20 bytes of data
SendBase=92
send cumulative 
ACK for 120
Transport Layer: 3-89
TCP: retransmission scenarios
cumulative ACK covers 
for earlier lost ACK
Host BHost A
Seq=92, 8 bytes of data
Seq=120,  15 bytes of data
Seq=100, 20 bytes of data
X
ACK=100
ACK=120
Transport Layer: 3-90
TCP fast retransmit
Host BHost Atimeout
X
Seq=100, 20 bytes of data
Receipt of three duplicate ACKs 
indicates 3 segments received 
after a missing segment – lost 
segment is likely. So retransmit!
if sender receives 3 additional 
ACKs for same data (“triple 
duplicate ACKs”), resend unACKed 
segment with smallest seq #
▪ likely that unACKed segment lost, 
so don’t wait for timeout
TCP fast retransmit
Transport Layer: 3-91
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
• segment structure
• reliable data transfer
• flow control
• connection management
▪ Principles of congestion control
▪ TCP congestion control
Transport Layer: 3-92

TCP flow control
application
process
TCP socket
receiver buffers
TCP
code
IP
code
receiver protocol stack
Q: What happens if network 
layer delivers data faster than 
application layer removes 
data from socket buffers?
Network layer 
delivering IP datagram 
payload into TCP 
socket buffers
from sender
Application removing 
data from TCP socket 
buffers
Transport Layer: 3-93
TCP flow control
application
process
TCP socket
receiver buffers
TCP
code
IP
code
receiver protocol stack
Q: What happens if network 
layer delivers data faster than 
application layer removes 
data from socket buffers?
Network layer 
delivering IP datagram 
payload into TCP 
socket buffers
from sender
Application removing 
data from TCP socket 
buffers
Transport Layer: 3-94
TCP flow control
application
process
TCP socket
receiver buffers
TCP
code
IP
code
receiver protocol stack
Q: What happens if network 
layer delivers data faster than 
application layer removes 
data from socket buffers?
from sender
Application removing 
data from TCP socket 
buffers
receive window flow control: # bytes 
receiver willing to accept
Transport Layer: 3-95
TCP flow control
application
process
TCP socket
receiver buffers
TCP
code
IP
code
receiver protocol stack
Q: What happens if network 
layer delivers data faster than 
application layer removes 
data from socket buffers?
receiver controls sender, so 
sender won’t overflow 
receiver’s buffer by 
transmitting too much, too fast
flow control
from sender
Application removing 
data from TCP socket 
buffers
Transport Layer: 3-96
TCP flow control
▪ TCP receiver “advertises” free buffer 
space in rwnd field in TCP header
• RcvBuffer size set via socket 
options (typical default is 4096 bytes)
• many operating systems auto-adjust 
RcvBuffer
▪ sender limits amount of unACKed 
(“in-flight”) data to received rwnd
▪ guarantees receive buffer will not 
overflow
buffered data
free buffer spacerwnd
RcvBuffer
TCP segment payloads
to application process
TCP receiver-side buffering
Transport Layer: 3-97
TCP flow control
▪ TCP receiver “advertises” free buffer 
space in rwnd field in TCP header
• RcvBuffer size set via socket 
options (typical default is 4096 bytes)
• many operating systems auto-adjust 
RcvBuffer
▪ sender limits amount of unACKed 
(“in-flight”) data to received rwnd
▪ guarantees receive buffer will not 
overflow
flow control: # bytes receiver willing to accept
receive window
TCP segment format
Transport Layer: 3-98
TCP connection management
before exchanging data, sender/receiver “handshake”:
▪ agree to establish connection (each knowing the other willing to establish connection)
▪ agree on connection parameters (e.g., starting seq #s)
connection state: ESTAB
connection variables:
seq # client-to-server
         server-to-client
rcvBuffer size
   at server,client 
           
application
network
connection state: ESTAB
connection Variables:
seq # client-to-server
          server-to-client
rcvBuffer size
   at server,client 
           
application
network
Socket clientSocket =   
  newSocket("hostname","port number");
Socket connectionSocket = 
welcomeSocket.accept();
Transport Layer: 3-99
Agreeing to establish a connection
Q: will 2-way handshake always 
work in network?
▪ variable delays
▪ retransmitted messages (e.g. 
req_conn(x)) due to message loss
▪ message reordering
▪ can’t “see” other side
2-way handshake:
Let’s talk
OK ESTAB ESTAB
choose x req_conn(x)
ESTAB
ESTAB acc_conn(x)
Transport Layer: 3-100

2-way handshake scenarios
connection 
x completes
choose x req_conn(x)
ESTAB
ESTAB
acc_conn(x)
data(x+1) accept
data(x+1)ACK(x+1)
No problem!
Transport Layer: 3-101
2-way handshake scenarios
ESTAB
retransmit
req_conn(x)
req_conn(x)
client 
terminates
server
forgets x
connection 
x completes
choose x req_conn(x)
ESTAB
ESTAB
acc_conn(x)
acc_conn(x)
Problem: half open 
connection! (no client)
Transport Layer: 3-102
2-way handshake scenarios
client 
terminates
ESTAB
choose x req_conn(x)
ESTAB
acc_conn(x)
data(x+1) accept
data(x+1)
connection 
x completes server
forgets x
Problem: dup data
accepted!
data(x+1)
retransmit
data(x+1)
accept
data(x+1)
retransmit
req_conn(x)
ESTAB
req_conn(x)
TCP 3-way handshake
SYNbit=1, Seq=x
choose init seq num, x
send TCP SYN msg
ESTAB
SYNbit=1, Seq=y
ACKbit=1; ACKnum=x+1
choose init seq num, y
send TCP SYNACK
msg, acking SYN
ACKbit=1, ACKnum=y+1
received SYNACK(x) 
indicates server is live;
send ACK for SYNACK;
this segment may contain 
client-to-server data received ACK(y) 
indicates client is live
SYNSENT
ESTAB
SYN RCVD
Client state
LISTEN
Server state
LISTEN
clientSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((‘’,serverPort))
serverSocket.listen(1)
connectionSocket, addr = serverSocket.accept()
clientSocket.connect((serverName,serverPort))
Transport Layer: 3-104
A human 3-way handshake protocol
1. On belay?
2. Belay on.
3. Climbing.
Transport Layer: 3-105
Closing a TCP connection
▪ client, server each close their side of connection
• send TCP segment with FIN bit = 1
▪ respond to received FIN with ACK
• on receiving FIN, ACK can be combined with own FIN
▪ simultaneous FIN exchanges can be handled
Transport Layer: 3-106
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-107

Congestion:
▪ informally: “too many sources sending too much data too fast for 
network to handle”
▪ manifestations:
• long delays (queueing in router buffers)
• packet loss (buffer overflow at routers)
▪ different from flow control!
Principles of congestion control
congestion control: 
too many senders, 
sending too fast
flow control: one sender 
too fast for one receiver
▪ a top-10 problem!
Transport Layer: 3-108
Causes/costs of congestion: scenario 1 
Simplest scenario:
maximum per-connection 
throughput: R/2
Host A
Host B
throughput: out
large delays as arrival rate 
 approaches capacity
Q: What happens as 
arrival rate in 
approaches R/2? 
original data: in 
R▪ two flows
▪ one router, infinite buffers 
▪ input, output link capacity: R infinite shared output link buffers
R▪ no retransmissions needed
R/2
delay
in
R/2
R/2
R/2
out
in
throughput: 
Transport Layer: 3-109
Causes/costs of congestion: scenario 2
▪ one router, finite buffers 
Host A
Host B
in : original data
'in: original data, plus 
retransmitted data
finite shared output 
link buffers
▪ sender retransmits lost, timed-out packet
• application-layer input = application-layer output: in = out
• transport-layer input includes retransmissions : ’in in
out
RR
Transport Layer: 3-110
Host A
Host B
in : original data
'in: original data, plus 
retransmitted data
finite shared output 
link buffers
Causes/costs of congestion: scenario 2
copy
free buffer space!
Idealization: perfect knowledge
▪ sender sends only when router buffers available 
out
RR
R/2in
R/2
outthroughput: 
Transport Layer: 3-111
Host A
Host B
in : original data
'in: original data, plus 
retransmitted data
finite shared output 
link buffers
RR
Causes/costs of congestion: scenario 2
copy
no buffer space!
Idealization: some perfect knowledge
▪ packets can be lost (dropped at router) due  to 
full buffers
▪ sender knows when packet has been dropped: 
only resends if packet known to be lost
Transport Layer: 3-112
Host A
Host B
in : original data
'in: original data, plus 
retransmitted data
finite shared output 
link buffers
RR
Causes/costs of congestion: scenario 2
free buffer space!
Idealization: some perfect knowledge
▪ packets can be lost (dropped at router) due  to 
full buffers
▪ sender knows when packet has been dropped: 
only resends if packet known to be lost
when sending at 
R/2, some packets 
are needed 
retransmissions
in
R/2
outthroughput: 
R/2
“wasted” capacity due 
to retransmissions
Transport Layer: 3-113
Host A
Host B
in : original data
'in: original data, plus 
retransmitted data
finite shared output 
link buffers
RR
Causes/costs of congestion: scenario 2
copy
timeout
Realistic scenario: un-needed duplicates
▪ packets can be lost, dropped at router due  to 
full buffers – requiring retransmissions
▪ but sender times can time out prematurely, 
sending two copies, both of which are delivered
free buffer space!
when sending at 
R/2, some packets 
are retransmissions, 
including needed 
and un-needed 
duplicates, that are 
delivered!
“wasted” capacity due 
to un-needed 
retransmissions
in
R/2
outthroughput: 
R/2
Transport Layer: 3-114
Causes/costs of congestion: scenario 2
“costs” of congestion: 
▪ more work (retransmission) for given receiver throughput
▪ unneeded retransmissions: link carries multiple copies of a packet
• decreasing maximum achievable throughput
Realistic scenario: un-needed duplicates
▪ packets can be lost, dropped at router due  to 
full buffers – requiring retransmissions
▪ but sender times can time out prematurely, 
sending two copies, both of which are delivered when sending at R/2, some packets 
are retransmissions, 
including needed 
and un-needed 
duplicates, that are 
delivered!
“wasted” capacity due 
to un-needed 
retransmissions
in
R/2
outthroughput: 
R/2
Transport Layer: 3-115
Causes/costs of congestion: scenario 3
▪ four senders
▪ multi-hop paths
▪ timeout/retransmit
Q: what happens as in and in ’ increase ?
A: as red  in ’ increases, all arriving blue pkts at upper 
queue are dropped, blue throughput  0
finite shared 
output link buffers
Host A
out
Host B
Host C
Host D
in : original data
'in: original data, plus retransmitted data
Transport Layer: 3-116
Causes/costs of congestion: scenario 3
another “cost” of congestion: 
▪ when packet dropped, any upstream transmission capacity and 
buffering used for that packet was wasted!
R/2
R/2
out
in ’
Transport Layer: 3-117
Causes/costs of congestion: insights
▪ upstream transmission capacity / buffering 
wasted for packets lost downstream
R/2
R/2
lout
lin’
▪ delay increases as capacity approached 
R/2
delay
lin
▪ un-needed duplicates further decreases 
effective throughput
lin
R/2
loutthroughput: 
R/2
▪ loss/retransmission decreases effective 
throughput
lin
R/2
loutthroughput: 
R/2
▪ throughput can never exceed capacity 
R/2lin
R/2
loutthroughput: 
Transport Layer: 3-118
End-end congestion control:
▪ no explicit feedback from 
network
▪ congestion inferred from 
observed loss, delay
Approaches towards congestion control
datadataACKs ACKs
▪ approach taken by TCP
Transport Layer: 3-119
▪ TCP ECN, ATM, DECbit protocols
Approaches towards congestion control
datadataACKs ACKs
explicit congestion info
Network-assisted congestion 
control:
▪ routers provide direct feedback 
to sending/receiving hosts with 
flows passing through congested 
router
▪ may indicate congestion level or 
explicitly set sending rate
Transport Layer: 3-120
Chapter 3: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-121

TCP congestion control: AIMD
▪ approach: senders can increase sending rate until packet loss 
(congestion) occurs, then decrease sending rate on loss event
AIMD sawtooth
behavior: probing
for bandwidth
TCP sender  Sending rate
time
increase sending rate by 1 
maximum segment size every 
RTT until loss detected
Additive Increase
cut sending rate in half at 
each loss event
Multiplicative Decrease
Transport Layer: 3-122
TCP AIMD: more
Multiplicative decrease detail:  sending rate is 
▪ Cut in half on loss detected by triple duplicate ACK (TCP Reno)
▪ Cut to 1 MSS (maximum segment size) when loss detected by 
timeout (TCP Tahoe)
Why AIMD? 
▪ AIMD – a distributed, asynchronous algorithm – has been 
shown to:
• optimize congested flow rates network wide [Kelly]!
• have desirable stability properties
Transport Layer: 3-123
TCP congestion control: details
▪ TCP sender limits transmission:
▪ cwnd is dynamically adjusted in response to observed 
network congestion (implementing TCP congestion control)
LastByteSent- LastByteAcked < cwnd
last byte
ACKed
last byte sent
cwnd
sender sequence number space 
available but 
not used
TCP sending behavior:
▪ roughly: send cwnd bytes, 
wait RTT for ACKS, then 
send more bytes
TCP rate ~~ cwnd RTT bytes/secsent, but not- yet ACKed 
(“in-flight”)
Transport Layer: 3-124
TCP slow start 
▪ when connection begins, 
increase rate exponentially 
until first loss event:
• initially cwnd = 1 MSS
• double cwnd every RTT
• done by incrementing cwnd 
for every ACK received
Host A Host B
RTT
time
▪ summary: initial rate is 
slow, but ramps up 
exponentially fast
Transport Layer: 3-125
TCP: from slow start to congestion avoidance
Q: when should the exponential 
increase switch to linear? 
A: when cwnd gets to 1/2 of its 
value before timeout.
Implementation:
▪ variable ssthresh 
▪ on loss event, ssthresh is set to 
1/2 of cwnd just before loss event
* Check out the online interactive exercises for more examples: http://gaia.cs.umass.edu/kurose_ross/interactive/
X
Transport Layer: 3-126
Summary: TCP congestion control
timeout
ssthresh = cwnd/2
cwnd = 1 MSS
dupACKcount = 0
retransmit missing segment 

cwnd > ssthresh
congestion
avoidance 
cwnd = cwnd + MSS    (MSS/cwnd)
dupACKcount = 0
transmit new segment(s), as allowed
new ACK
.
dupACKcount++
duplicate ACK
fast
recovery 
cwnd = cwnd + MSS
transmit new segment(s), as allowed
duplicate ACK
ssthresh= cwnd/2
cwnd = ssthresh + 3
retransmit missing segment
dupACKcount == 3
timeout
ssthresh = cwnd/2
cwnd = 1 
dupACKcount = 0
retransmit missing segment 
ssthresh= cwnd/2
cwnd = ssthresh + 3
retransmit missing segment
dupACKcount == 3cwnd = ssthresh dupACKcount = 0
New ACK
slow 
start
timeout
ssthresh = cwnd/2 
cwnd = 1 MSS
dupACKcount = 0
retransmit missing segment 
cwnd = cwnd+MSS
dupACKcount = 0
transmit new segment(s), as allowed
new ACKdupACKcount++
duplicate ACK

cwnd = 1 MSS
ssthresh = 64 KB
dupACKcount = 0
New
ACK!
New
ACK!
New
ACK!
Transport Layer: 3-127
TCP CUBIC
▪ Is there a better way than AIMD to “probe” for usable bandwidth?
Wmax
Wmax/2
classic TCP
TCP CUBIC - higher 
throughput in this 
example
▪ Insight/intuition: 
• Wmax: sending rate at which congestion loss was detected
• congestion state of bottleneck link probably (?) hasn’t changed much
• after cutting rate/window in half on loss, initially ramp to to Wmax faster, but then 
approach Wmax more slowly
Transport Layer: 3-128
TCP CUBIC
▪ K: point in time when TCP window size will reach Wmax
• K itself is tunable
• larger increases when further away from K
• smaller increases (cautious) when nearer K
TCP
sending 
rate
time
TCP Reno
TCP CUBIC
Wmax
t0 t1 t2 t3 t4 
▪ TCP CUBIC default in 
Linux, most popular TCP 
for popular Web servers 
(until ~2024)
▪ increase W as a function of the cube of the distance between current 
time  and K
Transport Layer: 3-129
TCP and the congested “bottleneck link”
▪ TCP (classic, CUBIC) increase TCP’s sending rate until packet loss occurs 
at some router’s output: the bottleneck link
source
application
TCP
network
link
physical
destination
application
TCP
network
link
physical
bottleneck link (almost always busy)
packet queue almost 
never empty, sometimes 
overflows packet (loss)
Transport Layer: 3-130
TCP and the congested “bottleneck link”
▪ TCP (classic, CUBIC) increase TCP’s sending rate until packet loss occurs 
at some router’s output: the bottleneck link
source
application
TCP
network
link
physical
destination
application
TCP
network
link
physical
▪ understanding congestion: useful to focus on congested bottleneck link
insight: increasing TCP sending rate will 
not increase end-end throughout at 
congested bottleneck, which is 
already transmitting at full rate, R
insight: increasing TCP sending 
rate will increase measured 
RTT (increased queueing 
delay at bottleneck link)
RTT
Goal: “keep the end-end pipe just full, but not fuller” Transport Layer: 3-131
R
TCP and the congested “bottleneck link”
▪ multiple flows collectively congest bottleneck link:
• each their executing own TCP congestion control
• each of N flows should ideally receive throughput of R/N 
Transport Layer: 3-132
1
2
N
...
...
Keeping pipe “just full enough, but no fuller”: keep bottleneck link busy 
transmitting, but avoid high delays/buffering
RTT
measured 
throughput =
# bytes sent (inflight) 
in RTT interval
Transport Layer: 3-133
Keeping the pipe just full enough
RTTmeasured
Intuition:
connection’s share of bottleneck_bandwidth • min_RTT  
ideal amount of 
inflight data for a 
connection
=
connection’s “bandwidth-delay product”ninflight
Keeping the pipe just full, but no fuller
Transport Layer: 3-134
bandwith•delay 
product
ninflight: amount of in-flight data
bandwith•delay 
product + queueing delay in 
full bottleneck buffer 
increasing ninflight in this 
region will not increase 
RTT, since arrival rate of 
packet data to queue is 
less that transmission rate
Increasing ninflight in this 
region increases RTT since 
arrival rate of packet data 
to bottleneck link exceeds 
link transmission rate
Here, arrival rate 
of packet data to 
bottleneck link is 
equals link 
transmission rate
RTT
Keeping the pipe just full, but no fuller
Transport Layer: 3-135
bandwith•delay 
product
bandwith•delay 
product + queueing delay in 
full bottleneck buffer 
throughput
ninflight: amount of in-flight data
RTT
Here, arrival rate of packet 
data to bottleneck link is 
equals link transmission rate
loss-based TCP seeks to operate here
BBR TCP seeks to operate here - the 
pipe is kept just full, but no fuller 
▪ regulates ninflight
▪ at longer time intervals:
• reduces ninflight to drain pipe, measure new min_RTT
▪ at shorter time intervals:
BBR (Bottleneck Bandwidth and RTT) 
Transport Layer: 3-136
• acceleration: increases  sending rate, ninflight, until reaches throughput 
plateau, (saturating available per-flow link capacity)
• cruising: sends at the rate that network is delivering data, as 
evidenced through received ACKs.
• deceleration: purposefully reduces ninflight, decreasing queue pressure, 
looking for lower min_RTT
source
application
TCP
network
link
physical
destination
application
TCP
network
link
physical
Explicit congestion notification (ECN)
TCP deployments often implement network-assisted congestion control:
▪ two bits in IP header (ToS field) marked by network router to indicate congestion
• policy to determine marking chosen by network operator
▪ congestion indication carried to destination
▪ destination sets ECE bit on ACK segment to notify sender of congestion
▪ involves both IP (IP header ECN bit marking) and TCP (TCP header C,E bit marking)
ECN=10 ECN=11
ECE=1
IP datagram
TCP ACK segment
Transport Layer: 3-137
TCP fairness
Fairness goal: if K TCP sessions share same bottleneck link of 
bandwidth R, each should have average rate of R/K
TCP connection 1
bottleneck
router
capacity RTCP connection 2
Transport Layer: 3-138
Q: is TCP Fair?
Example: two competing TCP sessions:
▪ additive increase gives slope of 1, as throughout increases
▪ multiplicative decrease decreases throughput proportionally 
R
R
equal bandwidth share
Connection 1 throughput
congestion avoidance: additive increase
loss: decrease window by factor of 2
congestion avoidance: additive increase
loss: decrease window by factor of 2
A: Yes, under idealized 
assumptions:
▪ same RTT
▪ fixed number of sessions 
only in congestion 
avoidance 
Is TCP fair?
Transport Layer: 3-139
Fairness: must all network apps be “fair”?
Fairness and UDP
▪ multimedia apps often do not 
use TCP
• do not want rate throttled by 
congestion control
▪ instead use UDP:
• send audio/video at constant rate, 
tolerate packet loss
▪ there is no “Internet police” 
policing use of congestion 
control
Fairness, parallel TCP 
connections
▪ application can open multiple 
parallel connections between two 
hosts
▪ web browsers do this , e.g., link of 
rate R with 9 existing connections:
• new app asks for 1 TCP , gets rate R/10
• new app asks for 11 TCPs, gets R/2 
Transport Layer: 3-140
Transport layer: roadmap
▪ Transport-layer services
▪ Multiplexing and demultiplexing
▪ Connectionless transport: UDP
▪ Principles of reliable data transfer 
▪ Connection-oriented transport: TCP
▪ Principles of congestion control
▪ TCP congestion control
▪ Evolution of transport-layer 
functionality
Transport Layer: 3-141

▪ TCP , UDP: principal transport protocols for 40 years
▪ different “flavors” of TCP developed, for specific scenarios:
Evolving transport-layer functionality
▪ moving transport–layer functions to application layer, on top of UDP
• HTTP/3: QUIC
Scenario Challenges
Long, fat pipes (large data 
transfers)
Many packets “in flight”; loss shuts down 
pipeline
Wireless networks Loss due to noisy wireless links, mobility; 
TCP treat this as congestion loss
Long-delay links Extremely long RTTs
Data center networks Latency sensitive
Background traffic flows Low priority, “background” TCP flows 
Transport Layer: 3-142
▪ application-layer protocol, on top of UDP
• increase performance of HTTP
• deployed on many Google servers, apps (Chrome, mobile YouTube app) 
QUIC: Quick UDP Internet Connections
IP
TCP
TLS
HTTP/2
Network
Transport
Application
HTTP/2 over TCP
IP
UDP
QUIC
HTTP/2 (slimmed)
HTTP/3
HTTP/3 over UDP
Transport Layer: 3-143
QUIC: Quick UDP Internet Connections
adopts approaches we’ve studied in this chapter for 
connection establishment, error control, congestion control
▪ multiple application-level “streams” multiplexed over single QUIC 
connection
• separate reliable data transfer, security
• common congestion control
• error and congestion control: “Readers familiar with TCP’s loss 
detection and congestion control will find algorithms here that parallel 
well-known TCP ones.” [from QUIC specification]
• connection establishment: reliability, congestion control, 
authentication, encryption, state established in one (or even zero) RTT 
(recall HTTP3 discussion in Chapter 2)
Transport Layer: 3-144
QUIC: streams: parallelism, no HOL blocking
(a) HTTP 1.1
TLS encryption
TCP RDT
TCP Cong. Contr.
transport application
(b) HTTP/2 with QUIC: no HOL blocking
TCP RDT
TCP Cong. Contr.
TLS encryption
error!
HTTP 
GET 
HTTP 
GET 
HTTP 
GET 
QUIC Cong. Cont.
QUIC 
encrypt
QUIC
 RDT
QUIC
 RDT
QUIC
 RDT
QUIC 
encrypt
QUIC 
encrypt
UDP UDP
QUIC Cong. Cont.
QUIC 
encrypt
QUIC
 RDT
QUIC
 RDT
QUIC
 RDT
QUIC 
encrypt
QUIC 
encrypt
error!
HTTP 
GET HTTP 
GET HTTP 
GET 
Transport Layer: 3-145
Chapter 3: summary
Transport Layer: 3-146
▪ principles behind transport 
layer services:
• multiplexing, demultiplexing
• reliable data transfer
• flow control
• congestion control
▪ instantiation, implementation 
in the Internet
• UDP
• TCP
Up next:
▪ leaving the network 
“edge” (application, 
transport layers)
▪ into the network “core”
▪ two network-layer 
chapters:
• data plane
• control plane
Additional Chapter 3 slides
Transport Layer: 3-147
Go-Back-N: sender extended FSM
Transport Layer: 3-148
Wait
start_timer
udt_send(sndpkt[base])
udt_send(sndpkt[base+1])
…
udt_send(sndpkt[nextseqnum-1])
timeout
rdt_send(data) 
if (nextseqnum < base+N) {
    sndpkt[nextseqnum] = make_pkt(nextseqnum,data,chksum)
    udt_send(sndpkt[nextseqnum])
    if (base == nextseqnum)
       start_timer
    nextseqnum++
    }
else
  refuse_data(data)
base = getacknum(rcvpkt)+1
If (base == nextseqnum)
    stop_timer
  else
    start_timer
rdt_rcv(rcvpkt) && 
   notcorrupt(rcvpkt) 
base=1
nextseqnum=1
rdt_rcv(rcvpkt) 
   && corrupt(rcvpkt) 

Go-Back-N: receiver extended FSM
Transport Layer: 3-149
Wait
rdt_rcv(rcvpkt)
  && notcorrupt(rcvpkt)
  && hasseqnum(rcvpkt,expectedseqnum) 
extract(rcvpkt,data)
deliver_data(data)
sndpkt = make_pkt(expectedseqnum,ACK,chksum)
udt_send(sndpkt)
expectedseqnum++
udt_send(sndpkt)
any other event 
expectedseqnum=1
sndpkt =    
  make_pkt(expectedseqnum,ACK,chksum)

ACK-only: always send ACK for correctly-received packet with highest 
in-order seq #
• may generate duplicate ACKs
• need only remember expectedseqnum
▪ out-of-order packet: 
• discard (don’t buffer): no receiver buffering!
• re-ACK pkt with highest in-order seq #
TCP sender (simplified)
Transport Layer: 3-150
wait
for 
event
NextSeqNum = InitialSeqNum
SendBase = InitialSeqNum

retransmit not-yet-acked segment         
with smallest seq. #
start timer
timeout
if (y > SendBase) { 
    SendBase = y 
    /* SendBase–1: last cumulatively ACKed byte */
    if (there are currently not-yet-acked segments)
         start timer
       else stop timer 
     } 
ACK received, with ACK field value y 
create segment, seq. #: NextSeqNum
pass segment to IP (i.e., “send”)
NextSeqNum = NextSeqNum + length(data) 
if (timer currently not running)
    start timer
                 
data received from application above
TCP 3-way handshake FSM
Transport Layer: 3-151
closed

listen
SYN
rcvd
SYN
sent
ESTAB
Socket clientSocket =   
  newSocket("hostname","port number");
SYN(seq=x)
Socket connectionSocket = 
welcomeSocket.accept();
SYN(x)
SYNACK(seq=y,ACKnum=x+1)
create new socket for communication 
back to client
SYNACK(seq=y,ACKnum=x+1)
ACK(ACKnum=y+1)ACK(ACKnum=y+1)

Transport Layer: 3-152
Closing a TCP connection
FIN_WAIT_2
CLOSE_WAIT
FINbit=1, seq=y
ACKbit=1; ACKnum=y+1
ACKbit=1; ACKnum=x+1
wait for server
close
can still
send data
can no longer
send data
LAST_ACK
CLOSED
TIMED_WAIT
timed wait 
for 2*max 
segment lifetime
CLOSED
FIN_WAIT_1 FINbit=1, seq=xcan no longer
send but can
 receive data
clientSocket.close()
client state server state
ESTABESTAB

TCP throughput
▪ avg. TCP thruput as function of window size, RTT?
• ignore slow start, assume there is always data to send
▪ W: window size (measured in bytes) where loss occurs
• avg. window size (# in-flight bytes) is ¾ W
• avg. thruput is 3/4W per RTT
W
W/2
avg TCP thruput = 3 4 W RTT bytes/sec
TCP over “long, fat pipes”
Transport Layer: 3-154
▪ example: 1500 byte segments, 100ms RTT, want 10 Gbps throughput
▪ requires W = 83,333 in-flight segments
▪ throughput in terms of segment loss probability, L [Mathis 1997]:
➜ to achieve 10 Gbps throughput, need a loss rate of L = 2·10-10  – a 
very small loss rate!
▪ versions of TCP for long, high-speed scenarios
TCP throughput = 1.22 . MSS RTT L