import frida
import socket
import sys
import time
import os

if len(sys.argv) < 3:
    print("Usage: python3 dumper.py mode game")
    print("")
    print("Modes:")
    print("0: Connect to local node proxy server")
    print("1: Dump session")
    print("")
    print("Games:")
    print("0: Boom Beach")
    print("1: Clash of Clans")
    exit(0)

game = sys.argv[1]
mode = sys.argv[2]

package_name = ""
path = ""

if game == "0":
    package_name = "com.supercell.boombeach"
elif game == "1":
    package_name = "com.supercell.clashofclans"

def parse_message(message, data):
    payload = message["payload"]
    arr = payload.split("::::")
    sess_file = None

    if mode == "1":
        if arr[0] == "0":
            print("PK:"+arr[1])
            sess_file = open(path + "/pk" + ".bin", "w")
            sess_file.write(arr[1])
        elif arr[0] == "1":
            print("SK:"+arr[1])
            sess_file = open(path + "/sk" + ".bin", "w")
            sess_file.write(arr[1])
        elif arr[0] == "2":
            print("PKS:"+arr[1])
            sess_file = open(path + "/pks" + ".bin", "w")
            sess_file.write(arr[1])
        elif arr[0] == "3":
            msgId = int(arr[1][:4], 16)
            sess_file = open(path + "/client_" + str(msgId) + str(time.time()) + ".bin", "w")
            sess_file.write(arr[1])
            print("[CLIENT] " + str(msgId))
        elif arr[0] == "4":
            msgId = int(arr[1][:4], 16)
            sess_file = open(path + "/server_" + str(msgId) + str(time.time()) + ".bin", "w")
            sess_file.write(arr[1])
            print("[SERVER] " + str(msgId))
        if (sess_file is not None):
            sess_file.close()
    elif mode == "0":
        msglen = len(payload)
        totalsent = 0
        while totalsent < msglen:
            sent = clientsocket.send(payload[totalsent:].encode())
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        if arr[0] == "0":
            print("PK:"+arr[1])
        elif arr[0] == "1":
            print("SK:"+arr[1])
        elif arr[0] == "2":
            print("PKS:"+arr[1])
        elif arr[0] == "3":
            msgId = int(arr[1][:4], 16)
            print("[CLIENT] " + str(msgId))
        elif arr[0] == "4":
            msgId = int(arr[1][:4], 16)
            print("[SERVER] " + str(msgId) + " " + str(totalsent))
        time.sleep(50.0 / 1000.0)


def instrument_debugger_checks():
    injector = ""
    if game == "0":
        injector = "bb_dumper.js"
    elif game == "1":
        injector = "coc_dumper.js"

    return open(injector, "r").read()

def runCmd(cmd):
    os.system(cmd)

if not os.path.exists("dumps"):
    os.makedirs("dumps")

if mode == "0":
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 10101))
elif mode == "1":
    t = str(time.time())
    path = "dumps/" + package_name + "_" + t
    os.makedirs(path)

runCmd("adb shell am force-stop " + package_name)
runCmd("adb shell am start -n " + package_name + "/" + package_name + ".GameApp")

process = frida.get_usb_device().attach(package_name)
script = process.create_script(instrument_debugger_checks())
script.on('message', parse_message)
script.load()
sys.stdin.read()