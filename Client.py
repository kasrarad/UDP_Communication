import socket
import pickle
import threading
from queue import Queue

MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'

# We need two treads (one for listening and one for sending message)
NUMBER_OF_THREADS = 2
THREAD_NUMBER = [1, 2]
queue = Queue()
users = []
addresses = []

PORT = 8888
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
# For servers
PORT1 = 5050
PORT2 = 9999
ADDR1 = (SERVER, PORT1)
ADDR2 = (SERVER, PORT2)

HEADERSIZE = 10
# We close the connection when the server received this message
DISCONNECT_MESSAGE = "DISCONNECT"
func = ""
RQ = 0
name = ""
IP_address = ""
socket_num = ""
reason = ""

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def start_shell():
    while True:
        cmd = input("zyra> ")

        if cmd == "quit":
            break
        elif "register" in cmd:
            register_user(cmd)
        elif "de-register" in cmd:
            de_register_user(cmd)
        else:
            print("Wrong Command")


def register_user(cmd):
    global RQ
    RQ = RQ + 1

    user_name = cmd.replace("register ", "")
    data = {1: "REGISTER", 2: RQ, 3: user_name, 4: SERVER, 5: PORT}
    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        client.sendto(msg, ADDR1)
        client.sendto(msg, ADDR2)
    except:
        print("Server not responding")


def de_register_user(cmd):
    global RQ
    RQ = RQ + 1

    user_name = cmd.replace("de-register ", "")
    data = {1: "DE-REGISTER", 2: RQ, 3: user_name}
    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        client.sendto(msg, ADDR2)
    except:
        print("Error sending message")


def add_subject_user(cmd):
    global RQ
    RQ = RQ + 1

    info = cmd.replace("add_subject ", "")
    data = {1: "ADD_SUBJECT", 2: RQ, 3: info, 4: SERVER, 5: PORT}
    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        client.sendto(msg, ADDR1)
        client.sendto(msg, ADDR2)
    except:
        print("Server not responding")


def del_subject_user(cmd):
    global RQ
    RQ = RQ + 1

    info = cmd.replace("del_subject ", "")
    data = {1: "DEL_SUBJECT", 2: RQ, 3: info, 4: SERVER, 5: PORT}
    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        client.sendto(msg, ADDR1)
        client.sendto(msg, ADDR2)
    except:
        print("Server not responding")


def handle_server_msg():
    connected = True
    while connected:
        data, addr = client.recvfrom(MAX_MSG_SIZE)
        # Check that the message length to be not zero
        if data:
            print("Message received from server: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
            # Get message length (from header) and Convert it to the integer
            msg_length = int(data[:HEADERSIZE])
            if msg_length <= 1028:
                d = pickle.loads(data[HEADERSIZE:])
                if d[1] == DISCONNECT_MESSAGE:
                    connected = False
                    print("Connection End")
                print(d)
            else:
                print("Message length is more than the buffer size")


def start_threads():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=job)
        t.daemon = True
        t.start()


def job():
    while True:
        x = queue.get()
        if x == 1:
            client.bind(ADDR)
            handle_server_msg()
        if x == 2:
            start_shell()

        queue.task_done()


def create_threads():
    for x in THREAD_NUMBER:
        queue.put(x)

    queue.join()


start_threads()
create_threads()