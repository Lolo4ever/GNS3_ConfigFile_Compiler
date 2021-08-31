#GNS3_Autoscript
import json
import string
import random
import os
import ipaddress

#PB : enlevé l'adresse donnée au script du PC de la list d'adresses possible (ou changer le script)
#Que le back bonne ont besion de partager le OSPF
#PC et Routeru wire peut avoir ospf et pas de mpls

#dans le back-Bone les routerus de part et d'autre du nuage qui doivent faire VPN se connaiisent


#A FAIRE:
#BACKBONE : definir le nombre de flux. Sur l'interface avec le routeur client metter en place la VRF --> detecet la bonne interface
#pour chaque flux : liste des PE concernée
#si un PE à un cite quin'est pas VPN, il doit être partagé

#liste de nodes associés à un flux

#Reconnaitre chaque routuer:
    #si backbone et connecté que à des routerus backbone : P
    #si backbone et connecté à non backbone : PE
    #si pas backbone : CE

#poir les routeur P : facile, déjà fait
#pour les routeur CE : facile, pareil mais avec Fast ethernet 0/0 pour ordi
#Pour PE :
    #pour chaque vrf : 
        """
        ip vrf <nom>
            rd <bgp>:<num>
            route-target export 25253:200
            route-target import 25253:200
        """ 
    #pour chaque liaison CE un ospf : 
        #si vfr
        """
        router ospf 2 vrf IT
            redistribute bgp 25253 subnets
            network 194.20.12.0 0.0.0.3 area 0
        """
        #sinon normal
    #en lisaison bgp avec chaque PE:
        """
        router bgp 25253 (même num partout)
            bgp log-neighbor-changes
            neighbor 192.168.10.11 remote-as 25253
            neighbor 192.168.10.11 update-source Loopback0
        address-family vpnv4 (si utile au flux vpn)
            neighbor 192.168.10.11 activate
            neighbor 192.168.10.11 send-community extended
            neighbor 192.168.10.11 next-hop-self
        exit-address-family
        """
        #et pour chaque flux concrnées:
            """
            address-family ipv4 vrf IT
                redistribute ospf 2
                exit-address-family
            """
        #activer le bgp pour les routeur indépendant de flux (faire aussi une vrf mais avec des export et import)
    #pour chaque interface :
        #si avec P : mpls, reconnaitre bon ospf
        #si PE : reconaitre le bon vfr


routers = []
PCs = []
wires = []
project_name=""
data = dict([])
backbone_nodes = []
with open('script2.txt') as json_file:
    data = json.load(json_file)
    routers = list(data["routers"].keys())
    PCs = list(data["PC"].keys())
    wires = list(data["links"].keys())
    project_name = data["project_name"]
    backbone_nodes = data["Protocols"]["Backbone"]

part1 = string.ascii_uppercase[0:6]
part2 = string.ascii_lowercase[0:6]
part3 = string.digits
project_id = "".join(random.choice(part1+part2+part3) for i in range(8)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(12))

P = []
PE = []
CE = []
flux_vpn = []

interfaces = {}

slots = [
    "f0/0",
    "g1/0",
    "g2/0",
    "g3/0",
    "g4/0"
]

mac_adresses = [
    "ca08.526a.0000",
    "ca07.376d.0000",
    "ca07.5251.0000",
    "ca06.375e.0000",
    "ca06.523f.0000",
    "ca05.374f.0000",
    "ca05.522a.0000",
    "ca04.3740.0000",
    "ca04.7a5f.0000",
    "ca03.36c4.0000",
    "ca03.7a4f.0000",
    "ca02.36b5.0000",
    "ca02.7a3f.0000",
    "ca01.366c.0000",
    "ca01.7a2f.0000"
]
"""
#option of configuration:
    -Avec mpls et ospf
    -avec VPN
    -All the nodes will be under the same ospf and area, eeveryone is backbone except PCs

#order
    -project name
    -instanciate each node like:
        R1 : 1.1.1.1(loopback and router id)
        PC1 : 192.168.1.1/8 (pc ip @)
    -write down each connection like
        R1/R2 : 192.168.10.0/24
   
"""


config_file = {}
config_file = {
    "auto_close": True,
    "auto_open": False,
    "auto_start": False,
    "drawing_grid_size": 25,
    "grid_size": 75,
    "name": project_name,
    "project_id": project_id,
    "revision": 9,
    "scene_height": 1000,
    "scene_width": 2000,
    "show_grid": False,
    "show_interface_labels": False,
    "show_layers": False,
    "snap_to_grid": False,
    "supplier": None,
    "topology": {
        "computes" : []
    }
}


drawings = []
drawing_id = "".join(random.choice(part1+part2+part3) for i in range(8)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(12))

drawings = [
    {
        "drawing_id": drawing_id,
        "locked": False,
        "rotation": 0,
        "svg": "<svg height=\"32\" width=\"211\"><text fill=\"#000000\" fill-opacity=\"1.0\" font-family=\"TypeWriter\" font-size=\"10.0\" font-weight=\"bold\">XXXXXXX /32</text></svg>",
        "x": 0,
        "y": 0,
        "z": 2
    },{}
]
config_file["topology"]["drawings"] = drawings



base = -600
console = 4999
dynamips_id = 0
nodes_id = {}
nodes = []
for router in routers:
    #varialbes
    base = base + 100
    console = console + 1
    dynamips_id = dynamips_id + 1
    router_id = "".join(random.choice(part1+part2+part3) for i in range(8)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(12))
    nodes_id.update(dict([(router,router_id)]))

    #interfaces
    interfaces[router] = [i for i in slots]

    #JSON
    temp = {
        "compute_id": "local",
        "console": console,
        "console_auto_start": False,
        "console_type": "telnet",
        "custom_adapters": [],
        "first_port_name": None,
        "height": 45,
        "label": {
            "rotation": 0,
            "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
            "text": router,
            "x": 14,
            "y": 14
        },
        "locked": False,
        "name": router,
        "node_id": router_id,
        "node_type": "dynamips",
        "port_name_format": "Ethernet{0}",
        "port_segment_size": 0,
        "properties": {
            "auto_delete_disks": True,
            "aux": None,
            "clock_divisor": 4,
            "disk0": 0,
            "disk1": 0,
            "dynamips_id": dynamips_id,
            "exec_area": 64,
            "idlemax": 500,
            "idlepc": "0x62cc930c",
            "idlesleep": 30,
            "image": "c7200-advipservicesk9-mz.152-4.S5.image",
            "image_md5sum": "cbbbea66a253f1dac0fcf81274dc778d",
            "mac_addr": mac_adresses.pop(), 
            "midplane": "vxr",
            "mmap": True,
            "npe": "npe-400",
            "nvram": 512,
            "platform": "c7200",
            "power_supplies": [
                1,
                1
            ],
            "ram": 512,
            "sensors": [
                22,
                22,
                22,
                22
            ],
            "slot0": "C7200-IO-FE",
            "slot1": "PA-GE",
            "slot2": "PA-GE",
            "slot3": "PA-GE",
            "slot4": "PA-GE",
            "slot5": None,
            "slot6": None,
            "sparsemem": True,
            "system_id": "FTX0945W0MY",
            "usage": ""
        },
        "symbol": ":/symbols/router.svg",
        "template_id": "0ecbc8b2-7491-47f1-9e02-b331eafea650",
        "width": 66,
        "x": base,
        "y": base,
        "z": 1
    }
    nodes.append(temp)

x1 = 650
y1 = -550
for pc in PCs:
    x1 = x1 - 100
    y1 = y1 + 100
    #varialbes
    console = console + 1
    pc_id = "".join(random.choice(part1+part2+part3) for i in range(8)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(12))
    nodes_id.update(dict([(pc,pc_id)]))
    #interfaces
    interfaces[pc] = ["e0"]

    temp = {
        "compute_id": "local",
        "console": console,
        "console_auto_start": False,
        "console_type": "telnet",
        "custom_adapters": [],
        "first_port_name": None,
        "height": 59,
        "label": {
            "rotation": 0,
            "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
            "text": pc,
            "x": 0,
            "y": 0
        },
        "locked": False,
        "name": pc,
        "node_id": pc_id,
        "node_type": "vpcs",
        "port_name_format": "Ethernet{0}",
        "port_segment_size": 0,
        "properties": {},
        "symbol": ":/symbols/vpcs_guest.svg",
        "template_id": "19021f99-e36f-394d-b4a1-8aaa902ab9cc",
        "width": 65,
        "x": x1,
        "y": y1,
        "z": 1
    }
    nodes.append(temp)
    


config_file["topology"]["nodes"] = nodes


#Pour chaque liaison, un nouveau 
bd_links = {}
for router in routers:
    bd_links[router] = {}
    for slot in slots:
        bd_links[router][slot]=[]
for pc in PCs:
    bd_links[pc] = {}
    bd_links[pc]["e0"]=[]

#WHAT IF COMPUTER? VNPC is e0 and router is f0/0 (with number 0) --> ECRIRE PC EN PERMIER : PC1/R1
links = []
partners = {}
for wire in wires:
    #variables
    link_id = "".join(random.choice(part1+part2+part3) for i in range(8)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(4)) + "-" + "".join(random.choice(part1+part2+part3) for i in range(12))
    extremities = wire.split("/")
    interface1 = interfaces[extremities[0]].pop()
    interface2 = ""
    if interface1=="e0":
        interface2 = "f0/0"
        partners[extremities[0]] = extremities[1]
    else:
        interface2 = interfaces[extremities[1]].pop()

    #pour la config du router après
    IPv4_adress = ipaddress.IPv4Network(data["links"][wire])
    net_address = str(IPv4_adress.network_address)
    net_mask = str(IPv4_adress.netmask)
    net_host_list = list(IPv4_adress.hosts())
    inversed_masked = str(IPv4_adress.hostmask)
    bd_links[extremities[0]][interface1].append(net_address)
    bd_links[extremities[0]][interface1].append(net_mask)
    bd_links[extremities[0]][interface1].append(str(net_host_list.pop(0)))
    bd_links[extremities[0]][interface1].append(inversed_masked)
    bd_links[extremities[1]][interface2].append(net_address)
    bd_links[extremities[1]][interface2].append(net_mask)
    bd_links[extremities[1]][interface2].append(str(net_host_list.pop(0)))
    bd_links[extremities[1]][interface2].append(inversed_masked)
    if(extremities[1] in backbone_nodes) & (extremities[0] in backbone_nodes):
        bd_links[extremities[0]][interface1].append(True)
        bd_links[extremities[1]][interface2].append(True)



    temp = {
        "filters": {},
        "link_id": link_id,
        "nodes": [
            {
                "adapter_number": int(interface1[1]),
                "label": {
                    "rotation": 0,
                    "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
                    "text": interface1,
                    "x": int(interface1[1]),
                    "y": int(interface1[1])
                },
                "node_id": nodes_id[extremities[0]],
                "port_number": 0
            },
            {
                "adapter_number": int(interface2[1]),
                "label": {
                    "rotation": 0,
                    "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
                    "text": interface2,
                    "x": int(interface2[1]),
                    "y": int(interface2[1])
                },
                "node_id": nodes_id[extremities[1]],
                "port_number": 0
            }
        ],
        "suspend": False
    }
    links.append(temp)

config_file["topology"]["links"] = links






rest = {}
rest = {
    "type": "topology",
    "variables": None,
    "version": "2.2.16",
    "zoom": 50
}

config_file.update(rest)

#print(json.dumps(config_file, indent=4))

with open(project_name+'.gns3','w') as f:
    f.write(json.dumps(config_file, indent=4))


#---------------------------------------------------------------------------------------------------------------
#                                               Each router configuration
#---------------------------------------------------------------------------------------------------------------   

for router in routers:   

    router_config = """!
!
!
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname """+router+"""
!
boot-start-marker
boot-end-marker
!
!
!
no aaa new-model
no ip icmp rate-limit unreachable
ip cef
!
!
!
!
!         
!
no ip domain lookup
no ipv6 cef
!
!
mpls label range """+str((routers.index(router)+1)*100)+' '+str(((routers.index(router)+1)*100)+99)+"""
multilink bundle-name authenticated
!
!
!
!
!
!
!
!
!
ip tcp synwait-time 5
! 
!
!
!
!
!         
!
!
!
!
!
!
interface Loopback0
 ip address """+data["routers"][router]+""" 255.255.255.255
!
"""
    router_config += "interface FastEthernet0/0\n"
    if len(bd_links[router]["f0/0"]) == 0:
        router_config +=" no ip address\n"
        router_config +=" shutdown\n"
        router_config +=" duplex full\n"
        router_config +="!\n"
    else:
        router_config +=" ip address "+bd_links[router]["f0/0"][2]+" "+bd_links[router]["f0/0"][1]+"\n"
        router_config +=" duplex full\n"
        router_config +=" no keepalive\n"
        router_config +="!\n"

    for slot in slots :
        if slot != "f0/0":
            router_config +="interface GigabitEthernet"+slot[1:]+"\n"
            if len(bd_links[router][slot]) == 0:
                router_config +=" no ip address\n"
                router_config +=" shutdown\n"
                router_config +=" negotiation auto\n"
                router_config +="!\n"
            else:
                router_config +=" ip address "+bd_links[router][slot][2]+" "+bd_links[router][slot][1]+"\n"
                router_config +=" ip ospf 1 area 0\n"
                router_config +=" negotiation auto\n"
                router_config +=" no keepalive\n"
                router_config +="!\n"



    router_config +="router ospf 1\n"
    router_config +=" router-id "+data["routers"][router]+"\n"
    router_config +=" redistribute connected\n"
 
    for slot in slots:
        if (len(bd_links[router][slot])==5) & ( router in backbone_nodes ):
            router_config +=" network "+bd_links[router][slot][0]+" "+bd_links[router][slot][3]+" area 0\n"
    router_config +="""!
ip forward-protocol nd
!
!
no ip http server
no ip http secure-server
!
!
!
!
control-plane
!
!
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line vty 0 4
 login    
!
!
end"""





    # define the name of the directory to be created
    current_path = os.getcwd()
 
    path = current_path+"/project-files/dynamips/"+nodes_id[router]+"/configs"
    try:
        os.makedirs(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)
    with open('project-files/dynamips/'+nodes_id[router]+'/configs/i'+str(routers.index(router) + 1)+'_startup-config.cfg','w') as f:
        f.write(router_config)

for pc in PCs:
    pc_config ="""# This the configuration for """+pc+"""
#
# Uncomment the following line to enable DHCP
# dhcp
# or the line below to manually setup an IP address and subnet mask
ip """+bd_links[pc]["e0"][2]+' '+bd_links[pc]["e0"][1]+""" gateway """+bd_links[partners[pc]]["f0/0"][2]+"""
#

set pcname """+pc

 # define the name of the directory to be created
    current_path = os.getcwd()
 
    path = current_path+"/project-files/vpcs/"+nodes_id[pc]
    try:
        os.makedirs(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)
    with open('project-files/vpcs/'+nodes_id[pc]+'/startup.vpc','w') as f:
        f.write(pc_config)