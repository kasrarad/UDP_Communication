import schedule
import socket
import threading
import time
import pickle
from queue import Queue


SERVER_NUM = 1
server = socket.socket()
HOST = ""
PORT = 0
ADDR = (HOST, PORT)
# The maximum  size of message that the server can receive
MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'

# We need at least two threads (one for listening and one for sending message)
# NUMBER_OF_THREADS = The number of threads for listening
NUMBER_OF_THREADS = 2
THREAD_NUMBER = [1, 2]
queue = Queue()
users = []
addresses = []

# Length of massage
HEADERSIZE = 10
# We close the connection when the server received this message
DISCONNECT_MESSAGE = "DISCONNECT"


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
        #server.bind(('', PORT))

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
        elif "select" in cmd:
            address = get_user(cmd)
            if address is not None:
                send_user_commands(address)
        else:
            print("Wrong Command")


def list_users():
    print("----Users----" + "\n")
    for i in range(len(users)):
        results = str(i) + "    " + str(addresses[i][0]) + "    " + str(addresses[i][1]) + "\n"
        print(results)


def get_user(cmd):
    try:
        user_id = cmd.replace("select ", "")
        user_id = int(user_id)
        address = users[user_id]
        return address
    except:
        print("Not Valid User")


def send_user_commands(addr):
    global server
    while True:
        try:
            cmd = input()
            if cmd == "quit":
                break
            #if len(cmd) > 0:
            #    server.sendto("", addr)
        except:
            print("Error sending message")
            break


def handle_client():
    global server
    connected = True
    while connected:
        try:
            data, addr = server.recvfrom(MAX_MSG_SIZE)
        except socket.timeout:
            server.close()
            connected = False
            print("Stop")
            break
        # Check that the message length to be not zero
        if data:
            #time.sleep(10)
            print("Message received from client: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
            # Get message length (from header) and Convert it to the integer
            msg_length = int(data[:HEADERSIZE])
            if msg_length <= 1028:
                data = pickle.loads(data[HEADERSIZE:])
                if data[1] == DISCONNECT_MESSAGE:
                    connected = False
                    print("Connection End")
                elif data[1] == "REGISTER":
                    handle_registration(data, addr)
                elif data[1] == "DE-REGISTER":
                    handle_registration(data, addr)
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


def start_threads():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=job)
        t.daemon = True
        t.start()


def job():
    global server
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            handle_client()
        if x == 2:
            create_socket()
            #bind_socket()
            handle_client()

        queue.task_done()


def create_threads():
    for x in THREAD_NUMBER:
        queue.put(x)

    queue.join()


# Start the thread for shell
t = threading.Thread(target=start_shell)
t.daemon = True
t.start()


def start():
    global server
    global SERVER_NUM
    SERVER_NUM = (SERVER_NUM + 1) % 2
    start_threads()
    create_threads()


schedule.every(3).seconds.do(start)

while True:
    schedule.run_pending()
