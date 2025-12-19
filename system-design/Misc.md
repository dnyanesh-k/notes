# What is DDoS(Distributed Denial of Service)?
- A DDoS attack uses multiple servers and Internet connections to flood the targeted resource. 
- DDoS attack where an attacker sends a large number of User Datagram Protocol (UDP) packets to a target port exploiting UDP’s connectionless nature.

## Attack Process
1. The attacker sends massive UDP packets with spoofed IP addresses to random ports on the target.
2. The target checks for active applications at those ports (usually none).
3. It responds with ICMP "Destination Unreachable" messages, overloading its own resources.