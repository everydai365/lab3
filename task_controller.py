#!/usr/bin/python3

import pox.openflow.libopenflow_01 as of

# KAIST CS341 SDN Lab Task 2, 3, 4
#
# All functions in this file runs on the controller:
#   - init(net):
#       - runs only once for network, when initialized
#       - the controller should process the given network structure for future behavior
#   - addrule(switchname, connection):
#       - runs when a switch connects to the controller
#       - the controller should insert routing rules to the switch
#   - handlePacket(packet, connection):
#       - runs when a switch sends unhandled packet to the controller
#       - the controller should decide whether to handle the packet:
#           - let the switch route the packet
#           - drop the packet
#
# Task 2: Getting familiarized with POX 
#   - Let switches "flood" packets
#   - This is not graded
# 
# Task 3: Implementing a Simple Routing Protocol
#   - Let switches route via Dijkstra
#   - Match ARP and ICMP over IPv4 packets
#
# Task 4: Redirecting all DNS request packets to controller 
#   - Let switches send all DNS packets to Controller
#       - Create proper forwarding rules, send all DNS queries and responses to the controller
#       - HTTP traffic should not be forwarded to the controller
#       
# Task 5: Implementing a Simple DNS-based Censorship
#   - Check DNS request
#       - If request contains task5-block.com, return empty DNS response instead of routing it
#       
# Task 6: Implementing more efficient DNS-based censorship 
#   - Let switches send only DNS query packets to Controller
#       - Create proper forwarding rules, send only DNS queries to the controller
#   - Check if DNS query contains cs341dangerous.com
#       - If such query is found, insert a new rule to switch to track the DNS response
#           - let the swtich route DNS response to the controller
#       - When the corresponding DNS response arrived, do followings:
#           - parse DNS response, insert a new rule to block all traffic from/to the server
#           - reply the DNS request with empty DNS response
#       - For all other packets, route them normally
#
# Task 7: Extending Censorship to Normal Network
#   - At any time, HTTP and DNS server can be changed by following:
#     - Create new server, hosting either task7-block-<one or more digits>.com or task7-open-<one or more digits>.com
#       - DNS server adds new record, HTTP server adds new domain
#     - For certain domain, hosting server changes
#       - DNS server changes record, HTTP server is replaced to another one
#     - For certain domain, hosting stops
#       - DNS server removes record, HTTP server removes the domain
#  - For 3 changes above, HTTP servers and DNS servers are changed instantly
#  - Assume that
#    - single IP might host multiple domains
#    - the IP should be blocked if it hosts at least one task7-block-<one or more digits>.com
#    - Only one IP is assigned to one domain
#    - If you detect different DNS response for same DNS request, assume that previous IP does not host the domain anymore


###
# If you want, you can define global variables, import Python built-in libraries, or do others
###

def init(self, net) -> None:
    #
    # net argument has following structure:
    # 
    # net = {
    #    'hosts': {
    #         'h1': {
    #             'name': 'h1',
    #             'IP': '10.0.0.1',
    #             'links': [
    #                 # (node1, port1, node2, port2, link cost)
    #                 ('h1', 1, 's1', 2, 3)
    #             ],
    #         },
    #         ...
    #     },
    #     'switches': {
    #         's1': {
    #             'name': 's1',
    #             'links': [
    #                 # (node1, port1, node2, port2, link cost)
    #                 ('s1', 2, 'h1', 1, 3)
    #             ]
    #         },
    #         ...
    #     }
    # }
    #
    pass
    ###
    # YOUR CODE HERE
    ###

def addrule(self, switchname: str, connection) -> None:
    #
    # This function is invoked when a new switch is connected to controller
    # Install table entry to the switch's routing table
    #
    # For more information about POX openflow API,
    # Refer to [POX official document](https://noxrepo.github.io/pox-doc/html/),
    # Especially [ofp_flow_mod - Flow table modification](https://noxrepo.github.io/pox-doc/html/#ofp-flow-mod-flow-table-modification)
    # and [Match Structure](https://noxrepo.github.io/pox-doc/html/#match-structure)
    #
    # your code will be look like:
    # msg = ....
    # connection.send(msg)
    pass
    ###
    # YOUR CODE HERE
    ###

from scapy.all import * # you can use scapy in this task

def handlePacket(self, switchname, event, connection):
    packet = event.parsed
    if not packet.parsed:
        print('Ignoring incomplete packet')
        return
    # Retrieve how packet is parsed
    # Packet consists of:
    #  - various protocol headers
    #  - one content
    # For example, a DNS over UDP packet consists of following:
    # [Ethernet Header][           Ethernet Body            ]
    #                  [IPv4 Header][       IPv4 Body       ]
    #                               [UDP Header][ UDP Body  ]
    #                                           [DNS Content]
    # POX will parse the packet as following:
    #   ethernet --> ipv4 --> udp --> dns
    # If POX does not know how to parse content, the content will remain as `bytes`
    #     Currently, HTTP messages are not parsed, remaining `bytes`. you should parse it manually.
    # You can find all available packet header and content types from pox/pox/lib/packet/
    packetfrags = {}
    p = packet
    while p is not None:
        packetfrags[p.__class__.__name__] = p
        if isinstance(p, bytes):
            break
        p = p.next
    print(packet.dump()) # print out received packet
    # How to know protocol header types? see name of class

    # If you want to send packet back to switch, you can use of.ofp_packet_out() message.
    # Refer to [ofp_packet_out - Sending packets from the switch](https://noxrepo.github.io/pox-doc/html/#ofp-packet-out-sending-packets-from-the-switch)
    # You may learn from [l2_learning.py](pox/pox/forwarding/l2_learning.py), which implements learning switches
    
    # You can access other switches via self.controller.switches
    # For example, self.controller.switches[0].connection.send(msg)

    ###
    # YOUR CODE HERE
    msg = of.ofp_packet_out()
    msg.data = event.ofp  # Include the original packet

    # Set the flood action: send to all ports except the one it came in on
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    msg.in_port = event.port  # Specify the incoming port

    # Send the flood action back to the switch
    connection.send(msg)
    print(f"Flooded packet from {switchname}")
    ###
