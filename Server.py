import schedule
import socket
import threading
import time
import pickle

SERVER_NUM = 1
server = socket.socket()
HOST = ""
PORT = 0
ADDR = (HOST, PORT)
# The maximum  size of message that the server can receive
MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'

users = []
addresses = []
subjects = []

# Length of massage
HEADERSIZE = 10


def create_socket():
    try:
        global HOST
        global PORT
        global server
        global ADDR
        global SERVER_NUM

        if SERVER_NUM == 0:
            HOST = socket.gethostbyname(socket.gethostname())
            PORT = 5050
            ADDR = (HOST, PORT)
        else:
            HOST = socket.gethostbyname(socket.gethostname())
            PORT = 9999
            ADDR = (HOST, PORT)

        # MAKE new socket
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.settimeout(300.0)

    except socket.error as e:
        print("There is an error in socket creation: " + str(e))


def bind_socket():
    try:
        global HOST
        global PORT
        global server
        global ADDR

        # Bind socket to the (host, port)
        server.bind(ADDR)

        if SERVER_NUM == 0:
            print(f"[LISTENING] Server A is listening on {HOST}")
        else:
            print(f"[LISTENING] Server B is listening on {HOST}")

    except socket.error as e:
        print("Socket binding error: " + "\n" + "Retrying...")
        bind_socket()


def start_shell():
    while True:
        cmd = input("zyra> ")

        if cmd == "list":
            list_users()
        else:
            print("Wrong Command")


def list_users():
    print("----Users----" + "\n")
    for i in range(len(users)):
        results = str(i) + "    " + str(addresses[i][0]) + "    " + str(addresses[i][1]) + "\n"
        print(results)


def handle_client():
    global server
    while True:
        try:
            data, addr = server.recvfrom(MAX_MSG_SIZE)
            # Check that the message length to be not zero
            if data:
                thread = threading.Thread(target=handle_data, args=(data, addr))
                thread.start()
                print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
        except socket.timeout:
            server.close()
            print("Server stopped")
            break

    print("Done")


def handle_data(data, addr):
    time.sleep(5)
    print("Message received from client: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
    # Get message length (from header) and Convert it to the integer
    msg_length = int(data[:HEADERSIZE])
    if msg_length <= 1028:
        data = pickle.loads(data[HEADERSIZE:])
        if data[1] == "REGISTER":
            handle_registration(data, addr)
        elif data[1] == "DE-REGISTER":
            handle_registration(data, addr)
        elif data[1] == "ADD_SUBJECT":
            handle_subject(data, addr)
        elif data[1] == "DEL_SUBJECT":
            handle_subject(data, addr)
    else:
        print("Message length is more than the buffer size")


def handle_registration(cmd, addr):
    global SERVER
    global server

    if cmd[1] == "REGISTER":
        check = True
        for user_name in range(len(users)):
            if user_name == cmd[3]:
                check = False
        if check:
            users.append(cmd)
            addresses.append(addr)
            subjects.append([])
            data = {1: "REGISTERED", 2: cmd[2]}
        else:
            data = {1: "REGISTER-DENIED", 2: cmd[2], 3: "Name already exist. Use another name"}

    if cmd[1] == "DE-REGISTER":
        check = False
        for user_name in range(len(users)):
            if user_name == cmd[3]:
                check = True
        if check:
            users.append(cmd)
            addresses.append(addr)
            data = {1: "DE-REGISTER", 2: cmd[2]}

    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        server.sendto(msg, addr)
    except:
        print("Error sending message")


def handle_subject(cmd, addr):
    if cmd[1] == "ADD_SUBJECT":
        data = cmd[3].split()
        check = False
        for i in range(len(users)):
            if users[i][3] == data[0]:
                check = True
                user_id = i
        if check:
            for k in range(1, len(data)):
                if data[k] not in subjects[user_id]:
                    subjects[user_id].append(data[k])
            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subjects[user_id]}
        else:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Name does not exist."}

    if cmd[1] == "DEL_SUBJECT":
        data = cmd[3].split()
        check = False
        for i in range(len(users)):
            if users[i][3] == data[0]:
                check = True
                user_id = i
        if check:
            for k in range(1, len(data)):
                if data[k] in subjects[user_id]:
                    subjects[user_id].remove(data[k])
            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subjects[user_id]}
        else:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Name does not exist."}

    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        server.sendto(msg, addr)
    except:
        print("Error sending message")


def start_thread():
    global server
    create_socket()
    bind_socket()
    handle_client()


# Start the thread for shell
t = threading.Thread(target=start_shell)
t.daemon = True
t.start()


def start():
    global server
    global SERVER_NUM
    print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
    SERVER_NUM = (SERVER_NUM + 1) % 2
    t1 = threading.Thread(target=start_thread)
    t1.start()
    t1.join()


schedule.every(1).seconds.do(start)

while True:
    schedule.run_pending()