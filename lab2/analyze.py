from scapy.all import *
from scapy.layers.inet import IP, TCP
from scapy.packet import Raw
import statistics

#the point is to use the delay between a server segment and the client's ACK,
#which is the round trip between the PC and the NAT.
#to check the rtt I can use the method .time

packets = rdpcap('capture-4.pcap')
# print(len(packets)) #2164


#to identify connections I need to use 4 parameters combined together: 
# IP src addr, IP dest addr, src port, dest port

connections_dict = {}
admin_key = None


for i, p in enumerate(packets):
    # if i > 5: break
    # print(p.show())   
    # print(type(p))

    if IP in p and TCP in p:
        srcIP = p[IP].src
        dstIP = p[IP].dst
        srcPort = p[TCP].sport
        dstPort = p[TCP].dport

        k_tuple = (f'{srcIP}:{srcPort}', f'{dstIP}:{dstPort}')
        key = tuple(sorted(k_tuple))

        if key not in connections_dict:
            #every value of a specific key is a list of packets
            connections_dict[key] = [p]
        else:
            connections_dict[key].append(p)

        #to identify the admin PC
        if p.haslayer(Raw) and b'POST /admin/login' in p[Raw].load:
            admin_key = key


rtt_per_conn = {}

for k, conn in connections_dict.items():
    ack_dict = {}

    #for every packet in the connection
    for pack in conn:
        #I need to distinguish between server and client, server has src port 80, client has destination port 80 
        if pack[TCP].sport == 80:
            #it's the server, I need to calculate the corresponding ack
            len_payload = len(pack[TCP].payload)
            if len_payload > 0:
                ack = pack[TCP].seq + len_payload

                ack_dict[ack] = pack.time


        else:
            #it's the client
            if pack[TCP].ack in ack_dict:
                rtt = pack.time - ack_dict[pack[TCP].ack]

                if k not in rtt_per_conn:
                    rtt_per_conn[k] = [rtt]
                else:
                    rtt_per_conn[k].append(rtt)

                del ack_dict[pack[TCP].ack]

# print('number of connections', len(connections_dict))
# print('\n rtt dictionary:   \n', rtt_per_conn)

#the method medians also sorts the list
reference_median = statistics.median(rtt_per_conn[admin_key])

xtrace_list = set()

for key, val_list in rtt_per_conn.items():
    if abs(statistics.median(rtt_per_conn[key]) - reference_median) < 0.005:

        # #first 3 packets of every connection are the three-way handshake
        # if len(connections_dict[key][0].payload) > 0:
        #     xtrace = connections_dict[key][3][Raw].load.decode('utf-8', errors='ignore').split('X-Trace: ')[1].split('\r\n')[0]

        for p in connections_dict[key]:
            if p.haslayer(Raw) and b'X-Trace:' in p[Raw].load:
                xtrace = p[Raw].load.decode('utf-8', errors='ignore').split('X-Trace: ')[1].split('\r\n')[0]
        xtrace_list.add(xtrace)

print('numero di pacchetti con flag', len(xtrace_list))
print('xtrace list', xtrace_list)

flag = 'netsec{'

for xtr in sorted(list(xtrace_list)):
    flag += xtr.split('-')[1]

flag += '}'
print(flag)
