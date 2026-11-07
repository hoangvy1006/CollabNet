<!-- converted from Chapter_7_v9.0.pdf -->

Computer Networking: A 
Top-Down Approach 
9th edition 
Jim Kurose, Keith Ross
Pearson, 2025
Chapter 7
Wireless and 
Mobile Networks
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
Wireless and Mobile Networks: 7-1
Wireless and mobile networks: overview
Chapter goals: 
▪ understand principles of wireless networks: 
• physical layer: radio, influence on higher layers
• access network:  link-layer challenges/solutions in any wireless networks
• core network: the “network” layer in a wireless network
• user/device mobility: among access networks
• application-specific wireless networks: Bluetooth, satellite, IoT
▪ wireless networks in practice:
• WiFi
• 5G (with a bit of 4G)
• Bluetooth, satellite, IoT
Wireless and Mobile Networks 7- 2
For a more extensive treatment of wireless and mobile networks visit:  https://gaia.cs.umass.edu/wireless_and_mobile_networks 
Chapter 7 outline
▪introduction
▪ radio: the physical layer
▪ the wireless access network
• principles, WiFi, 5G
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-3
Wireless and Mobile Networks: context
▪ more mobile-broadband-
connected (cellular) devices 
than fixed-broadband-
connected devices devices (5-1 
in 2019)!
• wireless connectivity even great 
when WiFi users considered (80% 
of broadband homes use WiFi)
• 60% of Internet traffic from 
major web sites destinated to 
mobile device
2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022
1000
2000
3000
4000
5000
6000
7000
8000
Mobile broadband subscribers (M)
Fixed (wired) broadband subscribers (M)
Broadband subscribers (M)
Data source: www.statista.com (1/25)
2023
Wireless and Mobile Networks: 7-4
Wireless applications their needs
Six application areas : 
▪ Wide-area Mobile Wireless Internet 
Access
▪ Local-area Mobile Wireless Internet 
Access 
▪ Fixed Wireless Internet Access 
▪ Satellite Networks for Internet 
Access and Sensing
▪ Cable replacement 
▪ Internet of Things (IoT)  
user data 
rate
energy
efficiency
device 
density
latency
area traffic 
capacity
mobility
high importance
medium
low
Application needs: 
mobility user data rate
energy 
efficiency
device 
densitylatency
area traffic 
capacity
Wireless and Mobile Networks: 7-5
Elements of a wireless network
wired network 
infrastructure
Wireless and Mobile Networks 7- 6
Elements of a wireless network
wired network 
infrastructure
wireless hosts
▪ laptop, smartphone, IoT
▪ run applications
▪ may be stationary (non-mobile) or mobile
• wireless does not always mean mobility! 
Wireless and Mobile Networks 7- 7
Elements of a wireless network
wired network 
infrastructure
base station
▪ typically connected to wired network
▪ relay - responsible for sending packets 
between wired network and wireless 
host(s) in its “area”
• e.g., 4G/5G cell towers,  802.11 (WiFi) 
access points  (APs)
Wireless and Mobile Networks 7- 8
Elements of a wireless network
wired network 
infrastructure
wireless link
▪ typically used to connect device(s) to base 
station, also used as backbone link 
▪ multiple access protocol coordinates link 
access (random access, FDMA, TDMA, CDMA, 
polling)
▪ various transmission rates and distances, 
frequency bands
Ad hoc networks: 
not all wireless 
networks are 
connected into a 
larger network
Wireless and Mobile Networks 7- 9
Elements of a wireless network
wired network 
infrastructure
wireless device radio
▪ wireless device has different 
radios for different networks
▪ iPhone16: has ~11 different 
radios, many antennae
▪ 5 different cellular radios, WiFi, 
Bluetooth, UWB, satellite NFC, 
GPS 
Ad hoc networks: 
not all wireless 
networks are 
connected into a 
larger network
Wireless and Mobile Networks 7- 10
Characteristics of selected wireless links
Indoor Outdoor Midrange
outdoor
Long range
outdoor
10-30m 50-200m 200m-4Km 4Km-15Km
2 Mbps
4G LTE, 5G eMBB
802.11ac
802.11n
802.11g
802.11b
3.5 Gbps
600 Mbps
54 Mbps
11 Mbps
Bluetooth
802.11ax14 Gbps
5G10 Gbps
802.11 af,ah
Space (100’s  
of Km)
LEOS 
Wireless and Mobile Networks 7- 11
…
Mobile device  
  (UE)
Base station
(eNode-B)  
…
Mobile device  
  
 Base station
(gNode-B)  
Mobility 
Management 
Entity (MME)
Internet
Institutional 
wired network
=
WLAN 1
WLAN 2
Internet
edge core edge core
Wireless networks: edge and core networks
WiFi: 5G:
Wireless and Mobile Networks 7- 12
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ radio principles
▪ radio channels
▪ antennas: MIMO
▪ radio spectrum
▪ coding and modulation
▪ the wireless access network
▪ the wireless core network
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-13
receiver
Electromagnetics: enabling communication
(1) current at one location (transmitter) ....
(2) creates an EM field in space ....
(3) induces a current at remote 
location (receiver)....
transmitter
slide concept: S. Rangan  (NYU) Wireless and Mobile Networks: 7-14
Radio basics: electromagnetic waves
: wavelength
amplitude
Electromagnetic wave has:
▪ wavelength ()
▪ frequency: speed of light / wavelength = c/
▪ directionality (of propagation)
▪ time-varying amplitude
wave propagation:
slide concept: S. Rangan  (NYU) Wireless and Mobile Networks: 7-15
Radio basics: phase
The phase of a periodic signal, 
represents the fraction of the 
period covered up until time t
▪ often measured in angular units 
(0  to 360)
0 90 180 270 360 degrees
time
we can code information into 
signal by changing signal’s 
phase (keeping frequency the 
same!)
bit value 0 0 1 0 1 1
time
signal
Wireless and Mobile Networks: 7-16
Radio signal characteristics
Power: antenna receive/transmit 
energy per unit time
▪ linear: measured in watts (or 
milliwatts)
▪ logarithmic: measured in decibels (db)
PdBm = 10 . log10 PmW
1mW( (
▪ example:
PmW = 250 mW (typical max
 mobile transmit power)
PdBm = 10 . log10 250mW 1mW( (
= 24 dBm
1.00 1.0025.9975 frequency (GHz)
power spectral density
Power spectral density:
▪ power present in signal as a function 
of frequency
carrier (center) frequency
Wireless and Mobile Networks: 7-17
Radio signal characteristics
Bandwidth: width (measured in Hz) of 
range of frequencies use by radio signal 
▪ radio frequency usage characterized by power 
spectral density (psd of zero means no signal 
power at that frequency)
▪ bandwidth = “band” + “width” (width of 
frequency band used)
2.438 2.4492.427
power spectral density (psd)
frequency (GHz)
carrier (center) frequency
22 MHz
bandwidth
Radio signal with 22 MHz bandwidth, 
evenly spread between 2.427, 2.429 GHz. 
This 22 MHz bandwidth channel 
corresponds to channel 6 in WiFi network)
Radio signal “bandwidth” different from link 
“bandwidth” (maximum transmission rate) 
term used by network engineers!
two meanings/usage of “bandwidth”
Wireless and Mobile Networks: 7-18
Signals and  Noise
▪ interference: other transmitters/EM 
radiaters in same frequency band
• hundreds of consumer devices operate in 
unlicensed 2.4 GHz band (aka: Industrial, 
Scientific, and Medical band): WiFi, 
Bluetooth, Zigbee, satellite TV, microwave 
ovens, garage-door openers, baby 
monitors, cordless phones, wireless 
mics/speakers, radio-controlled drones 
and toys, amateur radio, ...  
▪ thermal and electronic noise in receiver:
• natural thermal variations, imperfections 
in electronics
Original signal, noise, and noisy received signal
Wireless and Mobile Networks: 7-19
Signal to Noise Ratio (SNR)
SNR: ratio of signal power to noise power (often measured in dB)
SNR (dB)  = 10 . log10 received signal power noise power( (
▪ fundamental measure of channel “quality”
▪ SNR of 0 implies equal signal and noise
▪ high (or low) SNR: easy (or hard) to extract 
signal from signal+noise
▪ Typical ranges for current radios: 
• lower limit for cellular: -10 to -6 dB
• lower limit for WiFi: 20dB 
Original signal, noise, and noisy received signal
Wireless and Mobile Networks: 7-20
Channel Capacity 
Shannon capacity (of a communication channel): maximum rate at 
which data can be transmitted, given bandwidth, SNR constraints 
C  = B  . log2 received signal power noise power1+( (
where:
• C is capacity (bits/sec) 
• B is bandwidth (in Hz)
• power measured linearly 
(e.g., in mW)
Observations:
• C scales linearly with B (for constant SNR)
• high SNR: C scales logarithmically: little value 
in increasing SNR beyond a certain point
• Shannon: classic 1948 paper
Wireless and Mobile Networks: 7-21
Wireless link characteristics: path loss
Wireless radio signal attenuates (loses power) as it propagates 
f: frequency
d: distance
(aka fading) reduction in power density (attenuation) of an 
electromagnetic wave as it propagates from transmitter to receiver
path loss
Generalized path loss ~  (fd)n :
• n=2 (free space), n=(2.7,3.5) urban, n= (3,6) in building
Wireless and Mobile Networks 7- 22
“Hidden terminal problem” recalling  ~ (fd)2 path loss
Signal fading with~ (d)2 path loss, causes a “hidden terminal” problem:
A B C
space
Signal strength 
(log scale)
signal detection 
threshold
hidden terminals: A and B can hear each other, B and C can hear each 
other, but A  and C can not hear each other
▪ complicates wireless channel sharing among A, B, C
Wireless and Mobile Networks: 7-23
A
B
C
Objects cause ”hidden terminals”
▪ B, A hear each other
▪ B, C hear each other
▪ A, C can not hear each other means A, 
C unaware of their interference at B
Wireless link characteristics: hidden terminals
Path loss causes “hidden terminals”
▪ B, A hear each other
▪ B, C hear each other
▪ A, C can not hear each other interfering 
at B
A B C
space
Signal strength 
(log scale)
signal detection 
threshold
Wireless and Mobile Networks 7- 24
Wireless link characteristics: multipath
multipath propagation: radio signal reflects off objects ground, built 
environment, arriving at destination at slightly different times
line of sight 
(LOS) path
reflected path
reflected path
Wireless and Mobile Networks 7- 25
Wireless link characteristics: multipath
Tc: coherence time
Coherence time:
▪ amount of time bit is present 
in channel to be received
▪ influences maximum possible 
transmission rate, since 
coherence times can not 
overlap
▪ inversely proportional to
• frequency
• receiver velocity
transmitted
pulses
received
pulse
received
LOS pulse
received
multipath
 pulses
time
time
received
LOS pulse
received
multipath
 pulses
multipath propagation: radio signal reflects off objects ground, built 
environment, arriving at destination at slightly different times
Wireless and Mobile Networks 7- 26
Antennas
Antennas both transmit and receive radio waves
single antenna: old school
▪ Gigabit LTE with 4x4 
MIMO 
▪ Wi-Fi 6 (802.11ax) 
with 2x2 MIMO
multiple antenna: common now in wireless networks
MIMO: Multiple input
              multiple output 
              antenna
Wireless and Mobile Networks 7- 27
MIMO transmission: single user
Single User MIMO: spatial diversity
▪ multiple transmit/receive antenna to/at one user at same time
▪ exploit multipath: use multiple antennas to increase number of 
paths for transmitted signal between transmitter and receiver
• multipath: signals arriving at 
receiver not the same (e.g., 
some at higher quality) 
• antenna gain: increase SNR 
by combining multiple signals
12 signal paths from one sender (with two 
antennae) to one receiver (with two antennae) 
sender receiver
Wireless and Mobile Networks 7- 28
MIMO: spatial diversity
▪ increase reliability, range by 
sending / receiving redundant 
streams of information in 
parallel along different spatial 
paths between transmit and 
receive antennas 
▪ improved reliability: unlikely that all paths degraded at same time
▪ improved range: multiple antennas gather more signal at receiver
sender receiver
Wireless and Mobile Networks 7- 29
MIMO: spatial diversity
transmitter
H1,1(x) 
x
x
H2,1(x) 
y1= H1,1(x) 
       + H2,1(x) 
y2= H1,2(x) 
       + H2,2(x) 
x: signal transmitted
yj: signal received at antenna j
Hi,j(x): transformation of signal x from transmitter antenna i to 
receiver antenna j
• estimated by receiver (perhaps 
with sender’s help)
receiver
Transmitter
x
x
x
Receiver
y1= H1,1(x) + H2,1(x) H1,1() 
x
H1,2() 
H2,2() 
H2,1() 
y2= H1,2(x) + H2,2(x) 
x
Signal processing at receiver?
▪ don’t want to just add y1, y2
▪ take stronger or smaller SNR  of y1, y2?
▪ re-align phases, coherently add?
Wireless and Mobile Networks 7- 30
MIMO: spatial multiplexing
transmitter
H1,1(x1) 
x2
x1
H2,1(x2) 
y1= H1,1(x1) 
       + H2,1(x2) 
y2= H1,2(x1) 
       + H2,2(x2) 
receiver
▪ send two different streams of 
information, x1 and x2 in parallel 
along different spatial paths 
from transmitter to receiver
▪ spatial multiplexing differs from 
spatial diversity
Transmitter
x1
x2
x1
Receiver
y1= H1,1(x1) + H2,1(x2) H1,1() 
x2
H1,2() 
H2,2() 
H2,1() 
y2= H1,2(x1) + H2,2(x2) 
Wireless and Mobile Networks 7- 31
MIMO: spatial multiplexing
transmitter
H1,1(x1) 
x2
x1
H2,1(x2) 
y1= H1,1(x1) 
       + H2,1(x2) 
y2= H1,2(x1) 
       + H2,2(x2) 
Two equations in two unknowns
▪ but Hi,j(xi) are time-varying 
stochastic quantities
receiver
Transmitter
x1
x2
x1
Receiver
y1= H1,1(x1) + H2,1(x2) H1,1() 
x2
H1,2() 
H2,2() 
H2,1() 
y2= H1,2(x1) + H2,2(x2) 
y1= H1,1(x1) + H2,1(x2) 
y2= H1,2(x1) + H2,2(x2) 
Wireless and Mobile Networks 7- 32
Multi-user MIMO
▪ multiple transmit antenna send to 
different users at same time
• “spatial multiplexing”
▪ exploit directional antenna: send to 
geographically separated users at same 
time via beamforming
single user 
MIMO
multi-user 
MIMO
Wireless and Mobile Networks 7- 33
Wireless radio spectrum:
▪ radio spectrum: national asset, owned by the nation 
▪ national government determine how spectrum is used “locally”
▪ different spectrum use types:
licensed:
▪ dedicated use, 
typically by one 
“owner” (e.g., cellular 
carrier such as AT&T, 
Verizon)
▪ often allocated by 
spectrum auction
shared: 
▪ spectrum dynamically 
shared among users
▪ “incumbent” may get 
preferential access, 
others “back off”
unlicensed: 
▪ open (free) for anyone 
to use, conforming to 
rules (e.g., power 
transmission levels)
▪ 2.4GHz and 5 Ghz 
WiFi
▪ 3.5GHz “Private 5G” 
(aka CBRS)
Wireless and Mobile Networks: 7-34
WiFi spectrum bands
2.4 GHz
▪ Divided into 11-14 channels, depending on country 802.11
b/g/n/ax
5 GHz range 
▪ more than 150(configurable/selectable WiFi channels) of 
different transmission rates
802.11
a/h/n/ac/ax
6 GHz range 
▪ most recently added
▪ more than 250 configurable/selectable WiFi 
channels of different transmission rates
802.11
ax/be
▪ other 802.11 WiFi spectrum bands, but not in widespread use
Wireless and Mobile Networks: 7-35
Low band frequencies: (< 1 GHz range)
▪ covers longer distances (10’s of miles), but at lower speeds (50–250 
Mbps)
5G spectrum:  three spectrum bands*
* No single, well-accepted 
ranges for “low”, “mid” 
and “high”
Mid-band frequencies: 1 - 6 GHz ranges 
▪ balance distances (~5 miles ?) and transmission rates 
(100–900 Mbps)
▪ 1.8, 3.3 GHz to 3.8 GHz, 6 GHz bands popular
High band frequencies:  25–66 GHz range (aka mmwave)
▪ 26 GHz, 40 GHz, 50 GHz,  66 GHz bands popular
▪ short distances (< mile), high speeds (<3 Gbps)
▪ line of sight transmission: poor penetration of trees, buildings, ...
2G3G
2G3G
1-2.6 GHz
3.4 - 6 GHz
4G
4G
4G
5G
5G
5G
5G
Wireless and Mobile Networks: 7-36
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ radio principles
▪ radio channels
▪ antennas: MIMO
▪ radio spectrum
▪ coding and modulation
▪ the wireless access network
▪ the wireless core network
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-37
Physical Layer: coding and modulation
Coding
Coding
Add error detection, correction 
bits at physical layer
Digital 
Modulation
Modulation
Choose digital modulation technique 
that maximizes number of reliably 
transmitted bits/sec based on 
observed channel impairments
e.g., in family of Quadrature 
amplitude modulation (QAM)
Pulse Shaping
match transmission 
bandwidth to channel 
bandwidth using pulse 
shaping
RF Modulation
transmit signal as an 
electromagnetic wave 
over assigned carrier 
frequency
Carrier: waveform at a given frequency, fc (carrier frequency), modified 
(modulated) with an information-bearing signal
1010001011100110101
d: original data
We won’t cover this
 (look at ECE for courses)
Wireless and Mobile Networks 7- 38
Physical Layer: Error detection, correction coding
Coding
101000100110101 01101
EDC
EDC: error detection, correction bits 
▪ additionally transmitted bits (in 
addition to d) 
▪ added so receiver can detect and 
possibly correct errors in d bits
▪ example: parity bits, redundancy bits
d: original data
101000100110101
noisy channel
EDC’ d’
error-free
?
Y
N
01101
EDC’ d’: received data
101001100110101
▪ received EDC’ and 
received d’ bits may 
contain errors
errors
correctable
?
Y
N
EDC used at many layers: channel (physical), link, network, transport, application layers
Wireless and Mobile Networks 7- 39
Wireless physical layer may add EDC bits, into addition to:
application
transport
network
link
physical
MHtHn
M
application-layer EDC bits
Ht M
transport-layer EDC bits
link-layer EDC bits
MHtHnHl
original bits101000100110101
01101 EDC+original bits101000100110101
adding physical-layer EDC 
makes sense!
▪ detect/recover locally, rather 
than wait for end-end
▪ physical layer techniques 
adapted to local radio error 
characteristics
Physical Layer: Error detection, correction coding
Wireless and Mobile Networks 7- 40
Link
physical
coding
original bits from link layer, including EDC
Physical Layer: EDC shuffling example
d1 d2 d3 d4 d5 d6 d7 d8
d1 d1 ’ d2 d2 ’ d3 d3 ’ d4 d4 ’ d5  d5 ’ d6 d6 ’ d7 d7 ’ d8 d8 ’
d1 d5 ’ d2 d6 ’ d3 d7 ’ d4 d8 ’ d5 d1 ’ d6 d2 ’ d7 d3 ’ d8 d4 ’
add EDC duplicate bits in PHY 
shuffle for resistance to burst errors
modulation modulation:  from bits to symbols to waveforms
A burst of noise in this interval, causing 3 bits to be unintelligible 
still allows receiver to determine all original bits
A burst of noise in this interval causing 3 bits to be unintelligible , 
with no shuffling, would mean receiver can not determine  d4
Wireless and Mobile Networks 7- 41
Modulation
Coding
Coding
Digital 
Modulation
Modulation
Pulse Shaping RF Modulation
1010001011100110101
d: original data
encoding bits (1’s, 0’s) into analog RF 
carrier signal by changing (“modulating”) 
a characteristic of the RF carrier signal: 
amplitude, frequency, or phase. 
digital modulation 
time
bit value 0 0 1 0 1 1
time
amplitude 
modulation
time
frequency 
modulation
time
phase 
modulation
Wireless and Mobile Networks 7- 42
Modulation schemes: ASK, PSK
time
signal
Amplitude shift keying (ASK): 
signal’s amplitude encodes bits
1:
0:
Binary Phase shift keying 
(BPSK): signal’s phase encode bits
1:
0:
PSK: 0 and 1 signals out of phase by 
180o, but at same carrier frequency
time
signal
bit value 0 0 1 0 1 1
time
Wireless and Mobile Networks: 7-43
Modulation schemes: QPSK
Why stop at just two phases? 
▪ two bits grouped to become one “symbol” (2 bits -> 4 symbols)
▪ QPSK: Quadrature Phase Shift Keying: 4 symbols encoded using 4 phases
QPSK frequency same as BPSK, 
but twice the data rate!
Fun interactive QPSK tool:  https://www.geogebra.org/m/enkymjtg 
“00”
“01”
symbol signal
∂
∂
“10”
“11”
∂ ∂
∂
∂
∂
time
signal
“00”
0 0
“10”
1 0
“01”
0 1
“01”
0 1
“11”
1 1
“11”
1 1
Wireless and Mobile Networks: 7-44
Constellation diagrams
graphical characterization of modulation: amplitude, phase of symbols
45o135o
225o 315o
a
▪ point in constellation diagram 
depicts symbol’s phase (degrees 
counterclockwise from east) and  
amplitude (distance from origin)
▪ QPSK constellation diagram: four 
symbols represented by four signal 
waveforms:
▪ four different phases
▪ identical amplitude QPSK constellation diagram
Wireless and Mobile Networks: 7-45
QAM: Quadrature Amplitude Modulation 
bit encodings for 4-QAM, 16-QAM, 64-QAM (for WiFi)
▪ generalizing QPSK
▪ m-QAM: using m different 
amplitude/phase values to encode 
log2(m) bits
64-QAM b0b1b2b3b4b5
b0b1b2b316-QAM
b0b14-QAM
Wireless and Mobile Networks 7- 46
Constellation diagrams: how bit errors occur
phase/amplitude of transmitted signal
phase/amplitude of received signals
16-QAM b0b1b2b3
▪ receiver measures amplitude, phase of 
received signal
▪ receiver classifies symbol as bit pattern 
with amplitude, phase closest to 
received signal amplitude, phase 
Transmitter transmits waveforms for 12 1111 
symbols, sequentially
This received signal, is misclassified as 1011 since its 
amplitude, phases are closer to 1011 than 1111 These received signals correctly classified as 1111 (received 
amplitude, phases closest to 1111)
Wireless and Mobile Networks 7- 47
Adaptive modulation
given modulation scheme :
▪ has nominal data rate (assuming no 
errors)
▪ SNR can increase/decrease:
• changing interference
• sender transmitter power
▪ move along SNR vs BER tradeoff curve
Idea: change modulation scheme, power 
on the fly, getting highest data rate 
possible (at acceptable BER, acceptable 
energy expenditure), as SNR changes
Max data rate:
16 QAM: 11.5 Mbps
64 QAM: 26.9 Mbps
Wireless and Mobile Networks 7- 48
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• sharing a wireless access channel: 
OFDMA, CSMA/CA
• WiFi wireless LAN
• 5G radio access network
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-49
Recall: MAC protocols
multiple access protocols
channel partitioning random access taking turns
type of MAC
OFDMA
CSMA/CATDMA FDMA Aloha
slotted 
Aloha
CSMA
CSMA/CD
(Ethernet)
polling
type of protocolsystem
OFDMA: 4/5G, WiFi6; 
Bluetooth; satellite
WiFi; satellite; control 
plane: 4/5G, Bluetooth
 (and many wired technologies)
Bluetooth, satellite
 (and many wired technologies)
Wireless and Mobile Networks: 7-50
FDM: Frequency Division Multiplexing
0.00 0.25 0.50- 0.25- 0.50
frequency (Hz)
rather than one fat 
“wideband” channel:
divide into multiple 
thin “narrowband” 
subchannels
▪ separated by 
“guard bands” 
to  avoid 
interference
Narrowband channels:
▪ each subchannel has lower 
bit transmission rate than 
wideband channel:
• making multipath easier 
to accommodate
• lower rate 
implementations easier
▪ transmissions can happen 
on different subchannels at 
same time (in parallel)
Wireless and Mobile Networks: 7-51
OFDM: Orthogonal FDM
∂
∂
▪ subcarriers:  again close 
together
▪ slightly overlapping, 
but no guard bands
0.00 0.25 0.50- 0.25- 0.50
frequency (Hz)
▪ orthogonal: carefully 
designed, modulated 
so crosstalk among 
subcarriers cancels at 
center of each 
subcarrier frequency
envelope of spectrum
Wireless and Mobile Networks: 7-52
OFDM: Subcarriers
∂
0.00 0.25 0.50- 0.25- 0.50
frequency (Hz)
# subcarriers in an 4G / 
5G channel depends on 
channel’s bandwidth
Channel 
bandwidth
(MHz)
Number of 
subcarriers
1.25
2.5
5
10
15
20
76
150
300
600
900
1200
Wireless Jargon:
“carrier” ~ “channel”
“subcarrier” ~ “subchannel”
Wireless and Mobile Networks: 7-53
Time
15 kHz
180 kHz
frequency
OFDMA: subcarriers, time
Wireless and Mobile Networks: 7-54
frequency
time
66.6 umsec
0.5 msec slot
one “symbol” can be 
transmitted per 66.6 usec 
(4G) at given subcarrier 
frequency
▪ number of bits (between 
2-8) in symbol depends on 
modulation technique 
chosen (which depends 
on channel quality)
OFDMA: symbols
Wireless and Mobile Networks: 7-55
frequency
time
66.6 umsec
0.5 msec slot
resource block (RB):
▪ symbols grouped 
into resource blocks
▪ 84 symbols (7 
symbols/slot over 12 
subcarriers) in 4G
▪ smallest unit of data 
that can be sent to 
(assigned to) a user
OFDMA: resource blocks
Wireless and Mobile Networks: 7-56
Base station decides which RBs get 
assigned (over all frequencies) to 
which devices at 1 msec intervals
1 msec
..........................................
... ... ... ... ... ... ... ... ... ... ... ... ... ...
frequencies
4G / 5G scheduling interval
OFDMA: resource blocks
Wireless and Mobile Networks: 7-57
Commonalities, differences:
From 4G LTE to 5G New Radio (NR)
4G, 5G both use OFDMA
▪ Subcarrier bandwidths:
• 4G: 15 kHz
• 5G: 15, 30, 60, 120 kHz 
▪ Max carrier bandwidth:
• 4G: 20 MHz
• 5G: 100 MHz
4G, 5G: resource blocks (RB)
▪ smallest scheduling unit of 
transmission to device
14 symbols/subcarrier
1 msec
1 5G NR PRB
..........................................
... ... ... ... ... ... ... ... ... ... ... ... ... ...
7 symbols/subcarrier
0.5 msec
1 LTE PRB
12 (or configurable) number of 
subcarriers per carrier 
4G 5G
configurable bandwidth 
per sub carrier 
Wireless and Mobile Networks 7- 58
A
B
C
Objects cause ”hidden terminals”
▪ B, A hear each other
▪ B, C hear each other
▪ A, C can not hear each other means A, 
C unaware of their interference at B
CSMA/CA: addressing the “hidden terminals” problem
Path loss causes “hidden terminals”
▪ B, A hear each other
▪ B, C hear each other
▪ A, C can not hear each other interfering 
at B
A B C
space
Signal strength 
(log scale)
signal detection 
threshold
Wireless and Mobile Networks 7- 59
CSMA/CA: collisions happen
DIFS
data data
A senses channel 
empty, transmits
DIFS B senses channel empty 
(A’s’ transmission has 
not reached B yet), 
transmitscollision
data
A senses channel 
empty, transmits
DIFS B senses channel empty 
(does not hear A’s 
transmission due to 
fading), transmits
collision
data
A B
Wireless and Mobile Networks 7- 60
IEEE 802.11 MAC Protocol: CSMA/CA
802.11 sender
1 if sense channel idle for DIFS  then 
transmit entire frame (no collision detection)
sender receiver
DIFS
data
SIFS
ACK
802.11 receiver
 if frame received OK
   return ACK after SIFS (ACK needed due to hidden 
terminal problem) 
2 if sense channel busy then 
start random backoff time
timer counts down while channel idle
transmit when timer expires
3. if no ACK, increase random backoff interval, 
repeat 2 (see next slide)
Wireless and Mobile Networks 7- 61
CSMA/CA: randomization after collision
DIFS
data data
A senses channel 
empty, transmits
DIFS Channel sensed idle for DIFS time
collision
A B
data
data
Transmit (successfully)
NO ACK, loss or collision detected No ACK: loss or collision detected
DIFS Wait DIFS time DIFSWait DIFS time
Wait randomized backoffWait randomized backoff [0, 
~200 sec], depending on PHY .  
Backoff interval doubles after 
each collision
random 
backoff
random 
backoff
Wireless and Mobile Networks 7- 62
Avoiding collisions: using RTS/CTS
idea: sender “reserves” channel use for data frames using small 
reservation packets
▪ sender first transmits small request-to-send (RTS) packet to BS using 
CSMA
• RTSs may still collide with each other (but they’re short)
• contains duration for following data transmission
▪ BS broadcasts clear-to-send (CTS) packet  in response to RTS
• contains duration for following data transmission
▪ RTS and/or CTS heard by all nodes
• All nodes except transmitter defer transmissions 
•  transmits data frame
Wireless and Mobile Networks 7- 63
Collision Avoidance: RTS-CTS exchange
APA B
DATA (A)
reservation collision
defer
time
Wireless and Mobile Networks 7- 64
Backwards compatibility: challenging
IEEE 
standard
WiFi 
gen
Year Max data 
rate 
(theoretical)
Freque
ncy
(GHz)
Bandwidth PHY
802.11b 1999 11 Mbps 2.4 22 spread spectrum
802.11g 2003 54 Mbps 2.4 20 OFDM
802.11n WiFi 4 2009 600 Mbps 2.4, 5 20, 40 OFDM
802.11ac WiFi 5 2013 6.9 Gbps 5 20, 40, 80,160 OFDM, MIMO
802.11ax WiFi 6 2020 9.5 Gbps 2.4, 5 20, 40, 80,160 OFDM, OFDMA,  MIMO
802.11be WiFi 7 2024 30+ Gbps 2.4, 5, 6 20, 40, 80,160, 
320
OFDM, OFDMA, MIMO
Challenge:  WiFi 6/7 APs support OFDM (FDMA) and OFDMA (FDMA+TDMA)
▪ How can a WiFi 6/7 AP do both FDMA and TDMA at the same time?
▪ How can WiFi 6/7 AP support user device radios that only do FDMA?
Wireless and Mobile Networks 7- 65
Extending RTS/CTS: Multiuser RTS
idea: create new type of RTS message Multiuser RTS (MU-RTS)
▪ transmitter must use MU-RTS before OFDMA transmissions
▪ transmit MU-RTS using full FDMA channel, with duration info (as usual )
• heard by all 802.11* devices (both OFDM- and OFDMA-capable)
• contains additional OFDMA assignment info for receivers (so receivers 
will know which OFDMA RUs to listen to)
▪ receivers respond with CTS, sent on assigned OFDMA subchannel
▪ transmitter sends resource blocks to OFDMA receivers, according to 
assignment
Wireless and Mobile Networks 7- 66
Extending RTS/CTS: Multiuser RTS
Example scenario: 
▪ AP wants to send to 
seven devices
▪ two legacy devices 
a, b (OFDM only) 
▪ five OFDMA-capable 
devices 1, ... 5
RTS
(business-as-usual for devices a,b)
MU-RTS
(for OFDMA devices 1 ... 5)
Wireless and Mobile Networks 7- 67
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• sharing a wireless access channel: 
OFDMA, CSMA/CA
• WiFi wireless LAN
• 5G radio access network
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-68
802.11 wireless link layer 
data 
plane
WLAN
Link layer
Application
Network
Physical
Transport
802.11 MAC
control 
plane
802.3 
MAC
PHY
802.11 
MAC
PHY
data 
plane
control 
plane
802.3 
MAC
PHY
802.11 802.3
Wireless and Mobile Networks: 7-69
AP
UEs
to/from institutional 
network, Internet
reliable
data transfer
energy
management
channel
measurement
discovery,
attachment
RTS/CTS
...
control planedata plane
PHY
control frame
mngmnt frame
mngmnt frame
control frame
IP datagram
IP datagram
IP datagram
data frame
data frame
data frame
queue of frames 
awaiting transmission
(MAC scheduling)
802.11 downlink (AP-to-device) frame flow
▪ data frames: containing 
IP datagrams
▪ Control, management 
frames
Wireless and Mobile Networks: 7-70
802.11 frame: addressing
2 2 6 6 6 2 6 0 - 2312 4
Address 1: MAC address 
of wireless host or AP  to 
receive this frame
Address 4: used only in 
ad hoc mode
frame
control duration address 1 address 2 address 4 address 3 payload CRCseq control
Address 2: MAC address
of wireless host or AP 
transmitting this frame
Address 3: MAC address of 
router interface to which AP 
is attached
Wireless and Mobile Networks 7- 71
802.11 frame: addressing
Internet
H1 R1
AP MAC addr
address 1 address 2 address 3
802.11 WiFi  frame
R1 MAC addrH1 MAC addr
R1 MAC addr
MAC dest addr MAC source addr
802.3 Ethernet frame
H2 MAC addr
Wireless and Mobile Networks 7- 72
802.11 frame
2 2 6 6 6 2 6 0 - 2312 4
frame
control duration address 1 address 2 address 4 address 3 payload CRCseq control
duration of reserved 
transmission time (RTS/CTS)
frame sequence # (for 
reliable data transfer)
2 2 4 1 1 1 1 1 11 1
type from APsubtype to AP more frag WEPmore data power mgtretry rsvdprotocol version
0: management 
1: control
2: data
IP datagram, link-layer control or 
management message
type of management, control, or data frame
Wireless and Mobile Networks 7- 73
Retrospective: “A day in the life”* (WiFi)
Application
Network
Physical
Transport
802.11 MAC
control 
plane
802.11 MAC
Physical
data 
plane
control 
plane
data plane
*https://gaia.cs.umass.edu/kurose_ross/videos/6/
HTTP1
1 HTTP/3 request in UDP 
segment, in IP datagram, into 
802.11 frame.  Enter, wait, 
MAC frame scheduling queue
RTS CTS
2 Device sends RTS control 
frame (using CSMA/CA); AP 
responds with CTS.  
3 Device sends DATA frame to 
AP . Buffers DATA frame
23 ACK
4 AP responds with ACK, device 
removes transmitted frame 
4
AP can now forward frame to 
router 
Wireless and Mobile Networks: 7-74
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• sharing a wireless access channel: 
OFDMA, CSMA/CA
• WiFi wireless LAN
• 5G radio access network (RAN)
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-75
Architectural Elements of 5G
radio access 
Network (RAN)
to 
Internet
5G core network
gNodeB
User device 
Core Network Functions
Wireless and Mobile Networks 7- 76
5G Radio Access Network (RAN)
gNodeB
User equipment 
(UEs)
5G RAN: edge network connecting devices to 
base station
▪ provides link-layer service, as first hop between 
devices and larger network
▪ limited geographic scope
▪ under control of a single service provider
▪ somewhat analogous to WiFi LAN
▪ RAN components: 
• many devices (User Equipment: UE)
• radio channel (New Radio: NR)
• one base station (Next Generation Node B: gNodeB, gNB)
Wireless and Mobile Networks 7- 77
5G Core Network
to 
Internet
Core Network Functions
▪ Core situated between RAN and other 
endpoints (Core, larger Internet)
• single Core; multiple RANs
▪ consist of links, routers, servers, 
providing services to devices and base 
stations 
• “all IP” Core, but very different 
services than traditional Internet apps
▪ clear logical separation between 
control-plane, user plane:
• CUPS: Control-Plane and User-Plane 
Separation
Wireless and Mobile Networks 7- 78
Resource Blocks (RB)
▪ Resource Element (RE): holds one 
transmitted OFDMA symbol, in 
one time minislot on one 
subcarrier frequency
▪ Resource Block (RB): bundle of 
neighboring (time, frequency) 
Resource Elements
• 4G: 84 symbols  (12 neighboring 
subcarriers, 7 consecutive minislots)
• 5G: multiple bundlings possible  
• RB is smallest unit of transmission 
scheduling: all symbols in RB have 
same source, destination
180
kHz
1 ms
10 MHz channel with 50 RBs.
each RB spanning 180 kHz subchannel time
4G Resource Block (RB): 84 
Resource Elements (REs), 
each carrying one symbol.  
... ... ........................
Wireless and Mobile Networks 7- 79
... and it’s about to get more confusing
180
kHz
1 ms
10 MHz channel with 50 RBs.
each RB spanning 180 kHz subchannel time
... ... ........................
5G Bands, Channels, Subchannels: it confusing!
channel N
channel 1
one band multiple channels multiple subchannels
per channel
...
...... ...
Wireless and Mobile Networks 7- 80
Downlink physical channels
▪ downlink RBs transmitted from base station to 
devices 
▪ three 5G downlink physical channels:
• Physical Downlink Shared Channel (PDSCH)
• Physical Downlink Control Channel (PDCCH)
• Physical Broadcast Channel (PBCH)
base station
set of Resource Blocks (RBs) carrying similar type of 
data (channel  information RBs, user and control RBs, 
RB allocation information)
Physical channel
...
Wireless and Mobile Networks 7- 81
Uplink physical channels
▪ uplink RBs transmitted from devices to base station
▪ three 5G uplink physical channels:
• Physical Uplink Shared Channel (PUSCH) 
• Physical Random-Access Channel (PRACH)
• Physical Uplink Control Channel (PUCCH) 
set of Resource Blocks (RBs) carrying similar type of 
data (radio channel information RBs, user and control 
RBs, RB allocation information)
Physical channel
...
Wireless and Mobile Networks 7- 82
base station
Uplink/downlink logical channels
Set of Resource Blocks (RBs) carrying similar type of 
data.  Logical channels are mapped onto physical 
channels, with one or more logical channel mapped to 
same physical channel
▪ individual, per-device logical channels, as well as 
shared logical channels among devices
logical channel
6 physical channels
many logical channels
...
...
Wireless and Mobile Networks 7- 83
base station
RAN
link
layer
PDCP
RLC
MAC
Physical
RRC SDAP
control 
plane Network
user plane
device
base 
station
PDCP
RLC
MAC
Physical
RRC
RAN
link
layer
SDAP
control 
planeNetwork
user plane
Transport
Application
RAN protocol stack (at device, base station)
PDCP
RLC
MAC
Physical
RRC SDAP
control 
plane Network
user plane
device base station
PDCP
RLC
MAC
Physical
RRCSDAP
control 
planeNetwork
user plane
Transport
ApplicationHTTP1
SR DCI
Retrospective: “A day in the life”* (5G RAN)
1 HTTP/3 request in UDP 
segment, in IP datagram, into 
5G frame.  Enter, wait, 5G 
MAC frame scheduling queue
2 device’s control plane sends SR 
Scheduling Req) on Physical 
Uplink Control Channel 
(PUCCH) to base station
3 base station control plane send 
DCI message Physical Downlink 
Control Channel (PDCCH) 
granting upstream RBs
4 device sends frame in 
allocated RBs
2 3
Base station
(gNode-B)  
RAN: transfers datagrams between mobile core and devices
RAN packet processing pipeline: context
IP datagrams
 device
datagrams
protocol processing pipeline in UE
Wireless and Mobile Networks 7- 86
RAN packet processing pipeline
RRC
PDCP RLC MAC D/A conversion RF front endPHY
base station
control 
plane
user 
plane
mobile 
core
traditional 3GPP view
datagrams
RRC (Radio Resource Control) 
▪ configures coarse-grained, policy-related aspects of pipeline (e.g., 
scheduling prioritization, security)
▪ this implements the RAN’s control plane
▪ does not process user plane packets 
Wireless and Mobile Networks 7- 87
RAN packet processing pipeline
RRC
PDCP RLC MAC D/A conversion RF front endPHY
base station
control 
plane
user 
plane
mobile 
core
PDCP (Packet Data Convergence Protocol)
▪ compress/decompress IP headers
▪ ciphering, integrity protection
datagrams
Wireless and Mobile Networks 7- 88
RAN packet processing pipeline
RRC
PDCP RLC MAC D/A conversion RF front endPHY
base station
control 
plane
user 
plane
mobile 
core
RLC (radio link control)
▪ link-layer frame segmentation/reassembly
▪ reliable data transfer (ARQ)
datagrams
Wireless and Mobile Networks 7- 89
RAN packet processing pipeline
RRC
PDCP RLC MAC D/A conversion RF front endPHY
base station
control 
plane
user 
plane
mobile 
core
MAC (Media Access Control)
▪ buffering, multiplexing/demultiplexing frames
▪ scheduling: real-time scheduling frame decisions 
I msec scheduling control loop
datagrams
Wireless and Mobile Networks 7- 90
RAN packet processing pipeline
RRC
PDCP RLC MAC D/A conversion RF front endPHY
base station
control 
plane
user 
plane
mobile 
core
PHY (Physical Layer)
▪ modulation, coding 
datagrams
Wireless and Mobile Networks 7- 91
Split RAN
▪ Q: how is RAN functionality partitioned between physical elements (i.e.,., 
“split” across centralized and distributed locations)? 
▪ historically: no split - implemented in base station
RRC
PDCP RLC MAC D/A conversion RF front endPHY
Monolithic base station
control 
plane
user 
plane
 datagrams
Wireless and Mobile Networks 7- 92
Split RAN
▪ Q: how is RAN functionality partitioned between physical elements (i.e,., 
“split” across centralized and distributed locations)? 
▪ historically: no split - implemented in base station
RRC
PDCP RLC MAC D/A conversion RF front endPHY
Central Unit (CU)
control 
plane
user 
plane
Distributed Unit (DU) Radio Unit (RU)
▪ O-RAN: three “units” - where units are implemented is an 
implementation choice
datagrams
Wireless and Mobile Networks 7- 93
Recall our earlier description of traditional RAN base station (below)
▪ tightly coupled control and data planes
▪ let’s focus on control / management:  RRC implementation
Software-defined RAN
Wireless and Mobile Networks 7- 94
Software-defined RAN
▪ SD-RAN: implementing RAN using SDN approach
Control 
plane 
proxy
PDCP RLC MAC D/A conversion RF front endPHY
control 
plane
user 
plane
Real-Time Intelligent 
Controller (RIC)
3GPP-compliant 
interface between 
RAN and Mobile 
Core control plane
New programmatic 
API for exerting 
software-based 
control over pipeline 
that implements 
RAN user plane
Re-factored 
RRC
SDN-controlled switches
Wireless and Mobile Networks 7- 95
Software-defined RAN
▪ SD-RAN: implementing RAN using SDN approach
Control 
plane 
proxy
PDCP RLC MAC D/A conversion RF front endPHY
control 
plane
user 
plane
Real-Time Intelligent 
Controller (RIC)
Re-factored 
RRC
SDN-controlled switches
RAN Network Information Base (R-NIB) 
▪ common set of information 
consumed by numerous control apps, 
e.g., longer time-scale CQI (channel 
Quality Indicator) values, other per-
session state
R-NIB
load 
balancing handover QoS
Near-real time network 
control applications 
implemented as 
“xApps”
…
…
Wireless and Mobile Networks 7- 96
RAN: operator’s “secret sauce”
▪ combination of standardized specifications + implementation 
strategies:
▪ interfaces, high-level functions standardized 
▪ implementation of some functions, e.g., RB assignment to channels, 
frame scheduling, not standardized – up to the network operator. 
▪ implementation choices are the technical “secret sauces”
Wireless and Mobile Networks 7- 97
Chapter 7 outline
Wireless and Mobile Networks: 7-98
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• sharing a wireless access channel
• WiFi wireless LAN
• 5G radio access network
• common challenges: network discovery, 
frame scheduling, energy
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks

Joining the edge wireless network
▪ arriving device: must establish initial connection with node (WiFi AP , 
4G/5G base station) at wireless edge of network
• initial connection then used for authentication, DHCP , gain full network access
• “bootstrapping” connectivity: initial connection is just with edge node
institution’s
wired network Internet
gNode-B  
Mobile 
packet core Internet
WiFi AP
WiFi
5G
association
Wireless and Mobile Networks 7- 99
Association: two approaches
Beaconing: mobile listens to 
wireless channels for “beacons” 
advertising existence of wireless 
network node(s)
Probing: mobile actively 
transmits probe messages, 
waits for wireless network 
node(s) to reply
user device
Edge network 1
 Edge network 2
base
station
base
station
probe request
user device
Edge network 1
 Edge network 2
base
station
base
station
Either (or both)  approaches used in practice in an edge network 
Wireless and Mobile Networks 7- 100
802.11: beaconing and probing
arriving client device WiFi AP
1802.11 beacon frame (broadcast)
2 802.11 Association request
3802.11 Association response
Beaconing:
... device will next authenticate to network
AP 2
AP 1
H1
22
Probe Request frame broadcast from H1
Probe Response frames sent from APs
Association Request frame sent: H1 to 
selected AP 
Association Response frame sent from 
selected AP to H1
Probing:
1
1
2 2
3 4
2
3
4
No exchange of identity, credentials (yet)!  Just “Can we talk?”
Wireless and Mobile Networks 7- 101
Connecting to the 5G edge
5G network
(network 1)
5G network
(network 2)
H1
Base station 1
1 1
3
2
Wireless and Mobile Networks: 7-
102
Base station 2
RAN/WLAN scheduling: the “big picture”
All packets to/from all devices in edge network 
must pass through base station
▪ 4G/5G and WiFi 6/7: OFDMA RB scheduling
▪ downlink MAC scheduler: which frames to send 
from base station to which devices in which 
order in which RBs (if OFDMA)?
▪ uplink MAC scheduler: which devices send which 
frames in which order in which RBs to base 
station (if OFDMA)
gNodeB
devices
5G RAN
AP
devices
Wi-Fi
PHY
MAC
PHY
MAC
Wireless and Mobile Networks 7- 103
Channel aware or 
channel unaware?
▪ does scheduler 
consider quality of 
channel between 
base station and 
device?
Wireless MAC scheduling: considerations
good
poor
QoS aware or QoS 
unaware?
▪ does scheduler 
consider QoS (quality 
of service) needed by 
(or guaranteed to) 
device?
voice
WWW browsing
Priorities, Fair scheduling?
▪ Does scheduler provide priority 
among different types of traffic 
(user, control, real-time)?
▪ does scheduler consider 
fairness among UEs?
▪ fairness: no standard definition
“We are all equally important”
Wireless and Mobile Networks 7- 104
Channel aware or 
channel unaware?
▪ does scheduler 
consider quality of 
channel between 
base station and 
device?
MAC scheduling considerations
good
poor
QoS aware or QoS 
unaware?
▪ does scheduler 
consider QoS (quality 
of service) needed by 
(or guaranteed to) 
device?
voice
WWW browsing
Priorities, Fair scheduling?
▪ Does scheduler provide priority 
among different types of traffic 
(user, control, real-time)?
▪ does scheduler consider 
fairness among UEs?
▪ fairness: no standard definition
“We are all equally important”
▪ Standards do not dictate answers to these questions!
▪ Scheduling algorithms, parameters up to network 
implementers, operators: their “secret sauce”
Wireless and Mobile Networks 7- 105
... ... ... ... ... ........................
A 10 MHz channel with 
50  RBs, each RB spanning 180 kHz
180
kHz
RAN scheduling: Resource Blocks
Scheduling:
▪ Base station decides which 
frames/packets get 
assigned to which RBs for 
transmission to user
▪ scheduling interval: 1 msec
▪ scheduling complexity:
• 50 subchannels per 
10MHz channel
• 100’s (?) active user
Resource Block: 84 symbols
• one user gets to transmit 84 symbols 
on one subchannel in 0.5 sec time 
interval
• 50 subchannels per 10MHz channel
1 ms
time
Wireless and Mobile Networks: 7-
106
RAN scheduling: Channel Quality Indicator
PDCP
RLC
MAC
PHY
RAN packet-processing 
stack (3GPP)
IP datagrams
Channel Quality Indicator 
(CQI):
▪ user measures quality of 
received reference signals 
(embedded in RBs), reports 
quality back to base station
▪ 4-bit CQI value maps to 
modulation scheme to use 
(e.g., which QAM?) and 
expected throughput
scheduler
“We are all equally important”
control plane (RRC)
CQI
Wireless and Mobile Networks: 7-
107
RAN scheduling: QoS Class Indicator
PDCP
RLC
MAC
PHY
RAN packet-processing 
stack (3GPP)
IP datagrams
 QCI: QoS Class Indicator 
▪ QoS network wants to provide to a 
particular device (e.g., delay, 
guaranteed bit rate QoS guarantees)
▪ scheduler determines allocation of 
available radio spectrum to ensure all 
UEs meet their QoS requirementsscheduler
Priority QCI Max 
delay
Max loss Application
2 1 100ms .01 Voice
3 4 50 ms .001 Real-time gaming
6 7 300 ms .000001 Streaming video
8 8 600 .000001 Web browsing, TCP
CQI
QCI
(RRC)
Wireless and Mobile Networks: 7-
108
4G/5G scheduling: abstraction
Wireless and Mobile Networks 7- 109
Priority scheduling: 
▪ arriving traffic classified, 
queued by class
• any header fields can be used for 
classification, e.g., control versus 
user data
Scheduling policies: priority
high priority queue
low priority queue
arrivals
classify departureslink
 
1 3 2 4 5
arrivals
departures
packet 
in 
service
▪ send packet from highest 
priority queue that has 
buffered packets
• scheduling within priority class 
could be another scheduling 
discipline
1 3 4
2
5
1 3 2 4 5
Wireless and Mobile Networks 7- 110
Each device has its own queue▪ scheduler cyclically scans device queues, mapping packets/frame from 
each device (if available) to an RB in 
turn
▪ channel unaware, QoS unaware
▪ fair (by turns) but not necessarily 
throughput-fair since different devices 
may have different channel quality
Round Robin scheduling (per UE)
Wireless and Mobile Networks 7- 111
▪ find device (UE) i, with highest quality 
channel over all RBs, k:
• di k(t): expected data rate for UEi using 
kth RB at time t (e.g., based on CQI) 
• at t: select maxi,k {di k(t)}, assign UEi 
frame to RBk
▪ maximizes overall immediate throughput
▪ channel aware, QoS unaware, throughput 
unfair
Maximum Throughput (MT) scheduling
Wireless and Mobile Networks 7- 112
Blind Equal Throughput (BET) scheduling (per device)
▪ scheduler maintains exponentially-weighted-
moving-average of data rate received at each 
UEi at time t, Ri(t):
Ri(t) = (1-) . ri(t) +   Ri(t-1)
where ri(t) is data rate achieved in scheduling 
interval t
▪ at t: select mini {Ri(t-1)}: assign UEi frame blindly 
(not know channel conditions) to (any) RB
• assign RB to device with smallest data rate last round 
▪ channel somewhat-aware, QoS unaware, blind 
throughput fair
Wireless and Mobile Networks 7- 113
▪ combine Blind Equal Throughput (BET) and 
Maximum Throughput (MT) scheduling
di k(t): expected data rate for UEi 
using kth RB at time t 
Ri(t-1): data rate achieved by UEi at t
▪ at t: select maxi,k {di k(t) / Ri(t-1)}: assign UEi
Proportional Fairness (PF) scheduling
▪ balances high data rate with a measure of fairness
▪  channel aware, QoS unaware, fairness aware
Wireless and Mobile Networks 7- 114
▪ battery/energy: a critical resource in wireless devices (phones, IoT)
▪ energy use by LTE radios1:
• on: transmitting or receiving/waiting to receive: 1000 — 3500mW
• off: < 15mW (~1% – 2 % of on-state energy use)
Energy consumption in wireless devices
▪ significant amount of device energy 
expended on communication, across 
applications 
▪ 5G implementations currently 
expending more energy than 4G
Power use in mobile phones: 
app vs screen vs system vs network
Sources: 1: ATT, 2: “Understanding Operational 5G,” ACM SIGCOMM 2020 Wireless and Mobile Networks 7- 115
4G/5G, WiFi, Bluetooth radios turned off when not in use: conserve energy
Cycles of sleep/activity: sleep
Going to sleep is easier:
▪ device-driven: go to sleep if nothing to 
send, nothing being received
▪ sleep may (or may not) be coordinated 
with base station (4/5G), AP (WiFi) , 
controller (BT)
▪ may have deep-sleep (longer, more 
“turned off”) versus light sleep 
(shorter, less “turned off”) 
Wireless and Mobile Networks 7- 116
4G/5G, WiFi, Bluetooth radios turned off when not in use: conserve energy
Cycles of sleep/activity: awake
Waking up is harder:
▪ base station (4/5G), AP (WiFi) , controller (BT) 
needs to signal to “wake up” device when 
there are packets to be sent to it
• network context (4/5G) may need to be re-created
• data frames containing IP datagram (e.g., from 
remote hosts) need to be buffered at base station 
until device is awake
Wireless and Mobile Networks 7- 117
Cycles of sleep/activity: tradeoff/challenges
How long to sleep?
▪ longer: save more energy but greater latency
• effects on high-layer protocols: e.g., TCP 
▪ shorter: less energy savings, and more signaling 
overhead with short sleep cycles
How long to stay awake?
▪ time since last activity (before going to sleep)
• data transmission typically “bursty”
• burst should be over before going to sleep: how long to 
wait?
Wireless and Mobile Networks 7- 118
transmission 
received at device, 
start inactivity timer
incoming transmission to 
device buffered at base 
station until end of 
current DRX cycle
Device awakes from long DRX 
sleep, accepts channel 
scheduling assignment, ends 
sleep
device active
inactivity timer timeout, 
enter short DRX cycle
device active
periodic wakeup in short DRX 
cycles, nothing to send/receive, 
return to short DRX sleep
short DRX cycles
still nothing to send 
or receive, enter 
long DRX cycle
long DRX cycles
timet0 t1 t2 t4t3
transmission 
received at device
t5
Coordinated wake/sleep in 5G
Wireless and Mobile Networks 7- 119
Chapter 7 outline
Wireless and Mobile Networks: 7-120
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• principles, WiFi, 5G
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks

user plane
control plane
base station
AMF
Access, Mobility 
Management
AUSF
Authentication
Server
SMF
Session
Management
UPF
User
 Plane
NEF
Network 
Exposure
AF
Application 
Function
NRF
Network 
Repository
PCF
Policy 
control
UDM
Unified Data 
Management
UDSF
Unstructured 
Data Storage
UDR
Unified Data 
Repository
SEPP
Security 
Edge Proxy
data 
storage
control planes in other 
cellular providers
3rd  party apps
Internet
N1
N2
N3
5G Core Functional Components
5G Core is all 
(mostly) about 
control plane 
services
Wireless and Mobile Networks 7- 121
UPF (User Plane Function) 
▪ each device is assigned to a UPF, which acts as relay, forwarding traffic between 
UE, Internet 
▪ UPF responsible for policy enforcement, lawful intercept, traffic usage 
measurement, QoS policing
▪ responsible for tunneling (i.e., encapsulating, decapsulating) traffic to/from base 
station over N3 interface
5G Core Functional Components
Wireless and Mobile Networks 7- 122
5G Core Functional Components
AMF (Access, Mobility Management Function)
▪ connection, reachability management; 
mobility management; access 
authorization;  and location services
SMF (Session Management Function)
▪ manages each UE session, including IP 
address allocation, selection of 
associated UP function, QoS control, 
control aspects of UP routing
Wireless and Mobile Networks 7- 123
5G Core Functional Components
▪ AUSF (Authentication Server Function): Authenticates devices.
▪ UDM (Unified Data Management): Manages user identity, including the generation 
of authentication credentials.
▪ UDR (Unified Data Repository): Manages user static subscriber-related information.
▪ UDSF (Unstructured Data Storage Network Function): Used to store unstructured 
data, and so is similar to a Key/Value Store.
Wireless and Mobile Networks 7- 124
5G interfaces*, control/user -plane separation (CUPS)
control plane
▪ emphasis on functions and 
services
▪ well-defined interfaces 
defines between services
base station
N2
N7
N5
N13
N12 N10N8
N4N3
N1 N11
base station S-GW
data plane
▪ 5-layer Internet data plane
▪ extensive use of tunneling
IP tunnel
N3 N6 N6
AMF
Access, Mobility 
Management
SMF
Session
Management
PCF
Policy 
control
AUSF
Authentication
Server
UDM
Unified Data 
Management
AF
Application 
Function
UPF
User
 Plane
IP datagrams
* not all 3GPP defined interface shown
Wireless and Mobile Networks 7- 125
5G Core:  User plane tunnels
from Internet, 
sender has IP address w
IP
Packet Data
Convergence
Radio Link
Medium Access
Physical
GTP-U
UDP
IP
link
Physical
GTP-U
UDP
IP
link
Physical
IP
link
Physical
UPF for device z
UPF address: x
Source 
addr: w user payloadDest addr: z Source addr: w user payloadDest addr: z
Source
addr: x
Dest 
addr: y
Source 
addr: w UE payloadDest addr: z
base station
address  y         backhaul 
network
user device,
address z
Wireless and Mobile Networks 7- 126
Identity: who are you?
Internet approaches:
▪ You’re a name, password
• different names, password 
for different applications, 
services
▪ You’re a name, public key 
certificate
• servers often have public 
keys, users not so much 
(yet)
4G/5G:
▪ You’re a customer to a wireless 
service provider, with a home 
cellular network (who you pay)
▪ you have a SIM (Subscriber 
Identity Module) card or vSIM
• identifies you, your home 
network to all cellular networks 
globally
• has cryptographic key info also 
known to your home network
Wireless and Mobile Networks 7- 127
Joining a 5G network
▪ Two major phases:
• Registration: device identifies, authenticates itself to network, and vice 
versa
• PDU Session establishment:  Core network functions allocate  IP address to 
device, create data-plane path between device and device’s UPF 
• PDU: protocol data unit, aka, “packet”
▪ Access and Mobility Management Function (AMF) plays key role in 
joining arriving device into network
Wireless and Mobile Networks 7- 128
Joining a 5G network: steps
AMF
Access, Mobility 
Management
UDM
Unified Data 
Management
RRC connection setup 
request, response
Identity  request, response
Registration request
AUSF
Authentication
Server
remote/home 
5G Core
registration   accept
SMF
Session
Management
PDU session establishment request
registration 
session creation request, response device subscription retrieval, update
UPF
User Plane 
Function
session 
establishment 
req./resp. 
session info (e.g., device IPv4 address, tunnel)session req. (with SMF info)
session response
Device, base station, RAN 
data plane configuration
1st uplink datagram 
in data plane
session
establishment
authentication, security authentication, security
update device’s connection data 
AUSF
Authentication
Server
Wireless and Mobile Networks 7- 129
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• principles, WiFi, 5G
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-130
▪ spectrum of mobility, from the network perspective:
What is mobility?
no mobility high mobility
device moves
between 
networks, but
powers down
while moving
device moves 
within same 
WLAN/RAN in
one provider
network
device moves
among multiple
provider networks,
while maintaining
ongoing 
connections
device moves 
among WLANs/ 
RANs  in
one provider
network
We’re interested in these!
Wireless and Mobile Networks 7- 131
Mobility in a WiFi network
AP1
BSS1
AP2
AP3
BSS3
BSS2
 Extended Service Set (ESS)
router R1
switch S2
Internetswitch S1
▪ 802.11: a link-layer 
standard, takes a link-layer 
approach towards mobility
▪ Extended Service Set (ESS): 
multiple BSS’s, in same 
layer-3 subnet, each with 
same SSID
▪ mobility between BSSs in same ESS
• Fast re-authentication
• AP can suggest new APs to device
▪ proprietary (vendor) solutions for enhanced mobility 
Wireless and Mobile Networks 7- 132
Mobility in 5G networks: handover
Handover: 
▪ mobile device changes is 
point of attachment to the 
network
▪ data flow to device changes 
from source base station to 
target base station
AMF
Access, Mobility 
Management
SMF
Session
Management
UPF
User Plane 
Function
before 
handover
after 
handover
Why perform handover?
▪ stronger signal from target 
base station
▪ target base station has less 
devices, less traffic
Wireless and Mobile Networks: 7-133
source BS
1 3
2
data path before handover
data path after 
handover
1 current (source) BS selects 
target BS, sends Handover 
Request message to target BS
2 target BS pre-allocates radio 
time slots, responds with HR 
ACK with info for mobile
3 source BS informs mobile of new BS 
▪ mobile can now send via new BS - 
handover looks complete to mobile
4 source BS stops sending datagrams to mobile, instead forwards to new BS 
(who forwards to mobile over radio channel)
target BS
4
UPF
User Plane 
Function
Mobility in 5G networks: handover
Wireless and Mobile Networks: 7-134
UPF
User Plane 
Function
source BS
target BS5
5 target BS informs AMF, SMF 
that it is new BS for mobile
▪ SMF instructs UPF to 
change tunnel endpoint 
to be (new) target BS
AMF
Access, Mobility 
Management
SMF
Session
Management
6
UPF
User Plane 
Function
6 target BS ACKs back to 
source BS: handover 
complete, source BS can 
release resources
7 mobile’s datagrams now 
flow through new tunnel 
from target BS to UPF
5
Mobility in 5G networks: handover
Wireless and Mobile Networks: 7-135
Handover: timeline, signaling
AMF
Access, Mobility 
Management
SMF
Session
Management
UPF
User Plane 
Function
device
 source base 
station
target base 
station
detach from source 
base station, attach to 
target base station 
device data
buffer device data from 
source base stationRRC reconfig. 
complete handover 
success
handover
 in the 
RAN
transfer 
status path switch req. PDU session update session mod. req/response
data end marker
device data device data
path switch req. ACK 
PDU session 
update resp.device context
release
handover
 in the 
Core
measurement
handover 
request
handover 
request ACKRRC 
reconfig. transfer 
status
device data device data
accept?
making 
handover
decision
time
Wireless and Mobile Networks: 7-136
Chapter 7 outline
▪ introduction
▪ radio: the physical layer
▪ the wireless access network
• principles, WiFi, 5G
▪ the wireless core network
• principles, 5G
▪ mobility
▪ Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks: 7-137
example of wireless ad hoc network: devices have no “infrastructure” 
(e.g., access point, base station) to connect to
▪ BT devices must find other BT devices, organize themselves into a 
network from scratch!
• connect devices at link layer, providing channel allocation
• addressing assignment
• service discovery
• application-to-application communication over Bluetooth network
• security
Bluetooth (BT) overview
An entirely new architecture and protocol stack (different from Internet) is 
needed!
Wireless and Mobile Networks 7- 138
Bluetooth: overview
▪ Bluetooth network: piconet
▪ coverage: generally <10 m diameter
▪ no more than 8 devices per piconet
• device initially forming network: central role
• up to 7 more devices: peripheral role
▪ communication only between central and 
peripheral node 
• no direct peripheral-to-peripheral communication
▪ BT device has unique 48-bit address
▪ Operate in unlicensed ISM band: 2.4 GHz
C
P
device with central role
device with peripheral role
diameter of
coverage
C
P P
P
Wireless and Mobile Networks 7- 139
Bluetooth basics: wireless channel
▪ operates in 2.4-2.5 GHz ISM radio band
• Classic BT: 1 MHz bandwidth/channel, 79 
channels, 2.1 Mbit network max rate
• BLE: 2 MHz bandwidth/channel, 40 channels. 
3 advertising, 37 data channels
▪ BT channel: TDM, 625 sec slot length
▪ channel access via polling: central device 
advertises, grants channel access to 
peripherals in its BT network
▪ uses frequency hopping (form of “spread 
spectrum”) transmissions 
C
P
device with central role
device with peripheral role
diameter of
coverage
C
P P
P
Wireless and Mobile Networks 7- 140
Bluetooth channel: frequency hopping
▪ senders in BT network “hop” among 79 
frequencies/channels
• transmit on different frequency after each slot
• hopping pattern known by all BT devices in 
same piconet
▪ different BT piconets (with different hop 
patterns) can exist in same space
Q: Why hop?
A: minimize effects of interference:
▪ potentially many interfering transmitters in ISM
▪ If interfering device uses channel x, x occurs only occasionally in sequence
▪ BT frame sent on x (not received at receive due to interference), retransmitted on 
different frequency in next slot
... ... ........................
625 sec
slot
channel #
1
2
3
4
76
77
78
79
time
Hopping pattern used by BT network 1
Hopping pattern used by BT network 2
Wireless and Mobile Networks 7- 141
▪ Bluetooth stack completely 
different from Internet stack!
• differences reflect BT’s special purpose
▪ no “network,” “transport” layer!
• no routing in Classic BT (BLE adds 
managed flooding)
▪ layers not as conceptually well-
defined as in Internet, 5G
Bluetooth architecture, protocol stack (simplified)
Applications,
E2E services
Logical Link Control 
and Adaptation 
(L2CAP)
physical
link
Classic BLE
Host (OS)
Controller 
(firmware)
▪ separate controllers 
for classic, BLE
Host-Controller 
Interface (HCI)
▪ host, controller structure deeply 
embedded in architecture
Wireless and Mobile Networks 7- 142
▪ creation, management of end-end 
L2CAP channels between two devices
• channels for E2E application/user data, 
or higher-level services
• reliability, flow control, segmentation
▪L2CAP channels types:
• connection-oriented, asynchronous 
(ACL)
• connectionless, asynchronous (ACL)
• synchronous (eSCO), e.g., for periodic 
audio app)
Logical Link Control, Adaptation (L2CAP) layer
Wireless and Mobile Networks 7- 143
Bluetooth piconet and L2CAP connections
Bluetooth central role
physical
link
L2CAP 
MP3
music
MP3
music
Bluetooth peripheral
physical
link
L2CAP 
Bluetooth peripheral
Bluetooth piconet wireless 
channel (frequency hopping)
Service 
discovery
Service 
discovery
Remote
keyboard
Service 
discovery
Remote
keyboard
L2CAP 
link
physical
end-to-end L2CAP 
connections
Wireless and Mobile Networks 7- 144
Satellite applications
Sensing:
▪ environment: weather, 
land use,  various 
human activity
▪ resolution: ~m/pixel
Broadcast:
▪ consumer: Direct to Home 
TV/video, radio (Dish, SiriusXM)
▪ business: content to many 
cable head ends 
▪ GPS
▪ leverage broadcast: one 
send reaches many users
Internet:
▪ connectivity to unserved 
regions, alternative to 
wired Internet
▪ low latency over long 
distances
▪ access in airplanes
Wireless and Mobile Networks: 7-
145
GEO and LEO 
satellites
GEO:
▪ geosynchonous: stationary with 
respect to ground
▪ 35,768 km above earth
▪ ~800 msec RTT
▪ wide area coverage / satellite
LEO:
▪ Low Earth Orbit: satellite moves with 
respect to ground: 27,000 km/hour
• within line of sight (LOS) of ground 
station for 5-15 mins
▪ 550 - 1200 km above earth
▪ ~30 msec RTT in practice
▪ smaller area coverage / satellite
• constellation (network) of multiple 
LEO satellites to cover wide area
• inter-satellite links (ISL)
Wireless and Mobile Networks: 7-
146
Satellites: why all the fuss?
Sources: A. Raman, LEO Satellite Mega Constellations, networkingchannel.eu;
                 N.Pachler et al., An Updated Comparison of Four Low Earth Orbit Satellite Constellation Systems to Provide Global Broadband; company literature
 
Lots of (LEOS) satellites being launched
LEOS constellations
# deployed 
(2025)
# planned ISL planned?
Starlink 7,239 12,000 - 
42,000
Yes
EutelSat  
Oneweb
648 716 – 6,372 No
Kuipers 
(Amazon)
27 3,236 ?
Telesat 1 298 - 1671 Yes
Wireless and Mobile Networks: 7-
147
Components of a LEO satellite network
LEO satellites in motion
rural,
remote 
communications
airborne,
maritime
vehicles
intersatellite links (ISL)
satellite channel
▪ Broadcast (multicast) down
▪ unicast up
“footprint”
ground
stations
 Internet
mobile user terminals
Starlink satellite dish: 
“Dishy McFlatface”
Wireless and Mobile Networks: 7-
148
Satellite networking: a link or a network?
links in the sky
▪ single satellite hop between base 
stations
▪ AKA “bent pipe” architecture
network in the sky:
▪ multiple satellite hops between base 
stations
▪ routing among satellites
Wireless and Mobile Networks: 7-
149
Starlink
▪ April 2025: ~7,239 operational LEO satellites (planned: 
12K, requesetd:30K)
▪ first launches: 2019
▪ three low-Earth-orbit orbital shells, at 525, 530, 535 km 
▪ satellites: 500 – 2700 lbs
▪ services:
▪ Internet service: 4M subscribers in Sept 2024 (residential US: $120/mo)
▪ service in Ukraine (terrestrial networks damaged)
▪ 2024: testing direct-to-smartphone tests would use cellular spectrum from 
SpaceX’s U.S. mobile partner T-Mobile
Wireless and Mobile Networks: 7-
150
IoT: many, many use cases!
Monitoring: pressure, vibration, 
3D tilt, temperature, humidity, 
switches, openings, battery 
charge, voltage, leaks, cracks, 
strain gauges, fill levels ...
Asset geolocation, tracking 
warehouse security, monitoring 
transport conditions, e.g., for 
food safety  ... 
Monitoring: sound, air, water, 
weather, lighting, traffic, 
crowds, infrastrcuture; sharing 
(bikes) ...  
Smart metering, service 
(de)activation ,  efficiency 
monitoring, remote diagnosis, 
asset surveillance, quality 
monitoring ...
rainfall, temperature, wind, 
humidity, animal tracking and 
health, soil condition, 
infrastructure monitoring ...
Security, enviro conditions 
(temp., air, lights, power),  
predictive infrastructure 
monitoring,   ...
.... and 
there’s 
many 
more!
Wireless and Mobile Networks 7- 151
Lots of connected IoT devices, and more soon!
https://www.statista.com/statistics/512650/worldwide-connected-devices-amount/
IoT
PC, laptops, 
tablets, phones
number of devices (in billions)
60
50
40
30
20
10
2014 2028
Wireless and Mobile Networks 7- 152
▪ wireless
▪ distance: from meters to 
kilometers
▪ data rate: 100’s bps when active 
(metering) to ~1 Mbps (video 
surveillance)
▪ energy: always a consideration
• up ~10 years without external 
power
• local energy harvesting 
IoT communication requirements
wide area coverage
short
range: WiFi, 
BLE, Zigbee
traditional
Cellular:
4/5G
low power 
wide area: 
LoRaWAN, 
LTE-M 
IoT technical tradeoffs
Wireless and Mobile Networks 7- 153
Wireless and mobile networks: Summary
▪The physical layer: radio
▪The wireless access network
• principles, WiFi, 5G
▪The wireless core network
• principles, 5G
▪Mobility
▪Bluetooth, satellite, IoT wireless 
networks
Wireless and Mobile Networks 7- 154
For a more extensive treatment of wireless and mobile networks visit:  https://gaia.cs.umass.edu/wireless_and_mobile_networks 