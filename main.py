import getpass
import sys
from time import sleep
import telnetlib

def putadata(tn):
    data = tn.read_until(b'\n').decode('ascii')
    print(data)
    while (data != ''):
        data = tn.read_until(b'\n', 1).decode('ascii')
        print(data)

HOST = '192.168.56.101'
#user = raw_input("Enter your remote account: ")
password = b"eve"
user = b"root"
port = 32769

tn = telnetlib.Telnet(HOST,port,5)


#tn.write('sh ver ')
file=open("conf","r")
data = ''
#print(tn.read_until(b'\n').decode('ascii'))
#print (data)
#putadata(tn)
#tn.write(b"\n")
#tn.write(b"no\n")
#putadata(tn)
tn.write(b"enable\n")

tn.write(b"conf t\n")
putadata(tn)

str=file.readline()
while str!="":
    str=str.split(';')
    tn.write(b"int "+bytes(str[0], 'utf-8')+b"\n")
    sleep(0.01)
    tn.write(b"ip address "+bytes(str[1], 'utf-8')+b' '+bytes(str[2], 'utf-8')+b"\n")
    sleep(0.01)
    if str[3]=="1\n":
        tn.write(b"no sh\n")
        sleep(0.01)
    putadata(tn)
    str = file.readline()

tn.write(b"exit\n")
sleep(0.01)

tn.write(b"interface Loopback 0\n")
sleep(0.01)
tn.write(b"ip address 10.0.0.10 255.255.255.0\n")
sleep(0.01)
tn.write(b"exit\n")
sleep(0.01)
putadata(tn)
tn.write(b"exit\n")
sleep(0.01)
putadata(tn)

tn.write(b"show ip route\n\t")
putadata(tn)
tn.write(b"exit\n")
sleep(0.01)
putadata(tn)
tn.write(b"\n")
tn.close()