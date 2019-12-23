from time import sleep
import telnetlib
import json


def parce():
    file = open("conf", "r")

    str = file.read()
    str = str.split(':')
    str.pop(0)

    int=str[str.index("INT")+1]
    int=int.split(";")
    int.pop(int.__len__()-1)
    net=str[str.index("RIP")+1]
    net=net.split(";")
    vlan = str[str.index("VLAN") + 1]
    vlan = vlan.split(";")
    vlan.pop(vlan.__len__() - 1)
    ospf = str[str.index("OSPF") + 1]
    ospf = ospf.split(";")
    ospf.pop(ospf.__len__() - 1)
    dhcp = str[str.index("DHCP") + 1]
    dhcp = dhcp.split(";")
    dhcp[0]=dhcp[0][1:]
    file.close()
    return [int,net,vlan,ospf,dhcp]

def putadata(tn):
    data = tn.read_until(b'\n').decode('ascii')
    print(data,end='')
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
        print(data,end='')

def rip(tn,net):
    tn.write(b"conf t\n")
    tn.write(b"router rip\n")
    for i in net:

        tn.write(b"network " + bytes(i, 'utf-8') + b"\n")
    tn.write(b"exit\n")
    tn.write(b"exit\n")

def intconf(tn,inter):
    tn.write(b"conf t\n")
    putadata(tn)
    for i in inter:
        tn.write(b"int " + bytes(i['int'], 'utf-8') + b"\n")
        sleep(0.01)
        tn.write(b"ip address " + bytes(i["network"], 'utf-8') + b"\n")
        sleep(0.01)
        if i["no_sh"] == "1":
            tn.write(b"no sh\n")
            sleep(0.01)
        putadata(tn)
    tn.write(b"exit\n")
    tn.write(b"exit\n")

def vlanconf(tn,vlan):
    tn.write(b"conf t\n")
    putadata(tn)
    for i in vlan:
        tn.write(b"int " + bytes(i['int'], 'utf-8') + b"\n")
        tn.write(b"encapsulation dot1q " + bytes(i['int'][i['int'].index(".")+1:], 'utf-8') + b"\n")
        sleep(0.01)
        tn.write(b"ip address " + bytes(i["network"], 'utf-8') + b"\n")
        sleep(0.01)
        if i["no_sh"] == "1":
            tn.write(b"no sh\n")
            sleep(0.01)
        putadata(tn)
    tn.write(b"exit\n")
    tn.write(b"exit\n")

def bgpconf(tn,bgp):
    tn.write(b"conf t\n")
    putadata(tn)

    tn.write(b"router bgp " + bytes(bgp["id"], 'utf-8')+b"\n")
    for i in range(bgp["neighbor"].__len__()):
        tn.write(b"neighbor " + bytes(bgp["neighbor"][i], 'utf-8') + b" remote-as " + bytes(bgp["n_id"][i], 'utf-8') + b"\n")
        sleep(0.01)
        putadata(tn)

    for i in range(bgp["network"].__len__()):
        tn.write(b"network " + bytes(bgp["network"][i], 'utf-8') + b" mask " + bytes(bgp["mask"][i], 'utf-8') + b"\n")
        sleep(0.01)
        putadata(tn)

    tn.write(b"exit\n")
    tn.write(b"exit\n")

def ospfconf(tn,ospf):
    tn.write(b"conf t\n")
    putadata(tn)

    tn.write(b"router ospf " + bytes(ospf["id"], 'utf-8')+b"\n")
    for i in range(ospf["network"].__len__()):
        tn.write(b"network " + bytes(ospf["network"][i], 'utf-8') + b" area " + bytes(ospf["area"][i], 'utf-8') + b"\n")
        sleep(0.01)
        putadata(tn)
    tn.write(b"exit\n")
    tn.write(b"exit\n")

def get_ip_route(tn,name):
    arr=[]
    data="d"
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
    tn.write(b"show ip route\n\t")
    data = tn.read_until(b'\n').decode('ascii')
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
        arr.append(data)
        #print(data, end='')

    arr=arr[1:-3]
    #print(arr)

    buf=arr.index('\r\n')
    info=arr[:buf]
    buf2=arr.index('\r\n',buf+1)
    gateway=arr[buf+1:buf2]
    routes=arr[buf2+1:]
    #print(gateway)
    file=open(name+"_ip_route.txt","w")
    for i in routes:
        file.write(i[:-2]+"\n")
    file.close()

def get_int(tn,name):
    arr=[]
    data="d"
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
    tn.write(b"show ip int brief\n\t")
    data = tn.read_until(b'\n').decode('ascii')
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
        arr.append(data)
        #print(data, end='')

    arr=arr[:arr.index("Router#\r\n")]
    file=open(name+"_int.txt","w")
    for i in arr:
        file.write(i[:-2]+"\n")
    file.close()

def dhcpconf(tn,dhcp):
    tn.write(b"conf t\n")
    putadata(tn)
    for i in dhcp["exclude"]:
        tn.write(b"ip dhcp excluded-address " + bytes(i, 'utf-8') + b"\n")

    tn.write(b"ip dhcp pool " + bytes(dhcp["name"], 'utf-8') + b"\n")
    tn.write(b"network " + bytes(dhcp["network"], 'utf-8') + b"\n")
    tn.write(b"default-router " + bytes(dhcp["default"], 'utf-8') + b"\n")
    tn.write(b"dns-server " + bytes(dhcp["dns"], 'utf-8') + b"\n")
    tn.write(b"domain-name " + bytes(dhcp["domain"], 'utf-8') + b"\n")
    tn.write(b"end\n")



HOST = '192.168.56.101'
port = 32769
with open('example.json', 'r') as json_file:
    data = json.load(json_file)
HOST=data["host"]
routers=data["routers"]
for i in routers:
    print("configurating "+i['name'])

    tn = telnetlib.Telnet(HOST,port,5)
    tn.write(b"enable\n")
    if (i.get("int")!=None):
        intconf(tn,i["int"])
    if (i.get("rip") != None):
        rip(tn,i["rip"])
    if (i.get("vlan") != None):
        vlanconf(tn,i["vlan"])
    if (i.get("ospf") != None):
        ospfconf(tn,i["ospf"])
    if (i.get("dhcp") != None):
        dhcpconf(tn,i["dhcp"])
    if (i.get("bgp") != None):
        bgpconf(tn,i["bgp"])
    sleep(0.01)


    get_ip_route(tn,i['name'])
    get_int(tn,i["name"])
    if (i["save"]==True):
        tn.write(b"wr\n")
    #tn.write(b"exit\n")
    sleep(0.01)
    putadata(tn)
    #tn.write(b"\n")
    tn.close()
