import schedule
import socket
import threading
import time
import pickle

from functions import *  #list_register_file,check_register_file,append_register_file,delete_register_entry,get_users,get_addresses,get_subjects

# IP and PORT of the servers
PORT1 = 7777
PORT2 = 7778
SERVER1 = socket.gethostbyname(socket.gethostname())
SERVER2 = socket.gethostbyname(socket.gethostname())

SERVER_NUM = 0
server = socket.socket()
HOST = ""
PORT = 0
ADDR = (HOST, PORT)
# The maximum  size of message that the server can receive
MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'

filename = "register2.pickle"
users = []
addresses = []
subjects = []
publish_log = "log2.pickle"

change_ip_port = False
run_server = False

# Length of massage
HEADERSIZE = 10


def create_socket():
    try:
        global HOST
        global PORT
        global server
        global ADDR

        HOST = SERVER2
        PORT = PORT2
        ADDR = (HOST, PORT)

        # MAKE new socket
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if SERVER_NUM == 0:
            server.settimeout(300.0)
        else:
            server.settimeout(400.0)

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
            print(f"[LISTENING] Server B is listening on {HOST} and Port: {PORT}")
        else:
            print("Server B is waiting to start")

    except socket.error as e:
        print("Socket binding error: " + "\n" + "Retrying...")
        bind_socket()


def start_shell():
    while True:
        cmd = input("zyra> ")

        if cmd == "list":
            list_users(filename)
        elif cmd == "listregister":
            list_register_file(filename)
        elif "port" in cmd:
            change_port(cmd)
        elif "ip" in cmd:
            change_ip(cmd)
        elif "log" in cmd:
            display_log(publish_log)
        else:
            print("Wrong Command")



def change_port(cmd):
    global PORT1
    global change_ip_port

    try:
        server_port = cmd.replace("port ", "")
        server_port = int(server_port)
        PORT1 = server_port
        change_ip_port = True
    except:
        print("Not Valid port")


def change_ip(cmd):
    global SERVER1
    global change_ip_port

    try:
        server_ip = cmd.replace("port ", "")
        SERVER1 = server_ip
        change_ip_port = True
    except:
        print("Not Valid ip")


def handle_client():
    global server
    global run_server
    global users
    global addresses
    global subjects
    global filename

    users = get_users(filename)
    addresses = get_addresses(filename)
    subjects = get_subjects(filename)

    while True:
        try:
            data, addr = server.recvfrom(MAX_MSG_SIZE)
            data1 = pickle.loads(data[HEADERSIZE:])
            if data1[1] == "START":
                run_server = True
                server.close()
                break
            # Check that the message length to be not zero
            if data:
                thread = threading.Thread(target=handle_data, args=(data, addr))
                thread.start()
                print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")

        except socket.timeout:
            run_server = False
            handle_server()
            break

    #server.close()
    #print("Done")


def handle_server():
    global server
    global users
    global addresses
    global subjects
    global change_ip_port

    ################# SAVE users, addresses, subjects IN FILE (only add the NEW ONES to the previous files) ####################
    # TODO not sure if its needed to save file because its updated whenever we add, update, or delete
    # it is possible to dump everything from the text file into a msg and send it when switching

    server_addr = (SERVER1, PORT1)
    if change_ip_port:
        data = {1: "UPDATE-SERVER", 2: SERVER1, 3: PORT1}
        msg = pickle.dumps(data)
        msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
        change_ip_port = False
        try:
            server.sendto(msg, server_addr)
        except:
            print("Error sending message")

    for i in range(len(users)):
        data = {1: "CHANGE-SERVER", 2: SERVER1, 3: PORT1}
        msg = pickle.dumps(data)
        msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
        user_addr = (addresses[i][0], addresses[i][1])
        try:
            server.sendto(msg, user_addr)
        except:
            print("Error sending message")

    data1 = {1: "START", 2: SERVER1, 3: PORT1}
    msg1 = pickle.dumps(data1)
    msg1 = bytes(f'{len(msg1):<{HEADERSIZE}}', FORMAT) + msg1
    try:
        server.sendto(msg1, server_addr)
    except:
        print("Error sending message")

    print("Server stopped")
    server.close()


def handle_data(data, addr):
    global run_server
    global server
    global SERVER1
    global PORT1
    global subjects
    global filename

    if run_server:
        #time.sleep(5)
        print("Message received from client: " + "IP: " + addr[0] + " Port: " + str(addr[1]))
        # Get message length (from header) and Convert it to the integer
        msg_length = int(data[:HEADERSIZE])
        if msg_length <= 1028:
            data = pickle.loads(data[HEADERSIZE:])
            subjects = get_subjects(filename)
            if data[1] == "UPDATE-SERVER":
                SERVER1 = data[2]
                PORT1 = data[3]
            elif data[1] == "REGISTER":
                handle_registration(filename,data, addr,server,users,addresses,subjects)
            elif data[1] == "UPDATE":
                handle_registration(filename,data, addr,server,users,addresses,subjects)
            elif data[1] == "DE-REGISTER":
                handle_de_registration(filename,data, addr,server,users,addresses,SERVER1,PORT1)
            elif data[1] == "ADD_SUBJECT":
                handle_subject(filename,data, addr,server,users,addresses,subjects)
            elif data[1] == "DEL_SUBJECT":
                handle_subject(filename,data, addr,server,users,addresses,subjects)
            elif data[1] == "PUBLISH":
                handle_publishing(filename,data, addr,server,users,addresses,subjects,publish_log)
        else:
            print("Message length is more than the buffer size")
    else:
        print("Message received from server: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
        # Get message length (from header) and Convert it to the integer
        msg_length = int(data[:HEADERSIZE])
        if msg_length <= 1028:
            data = pickle.loads(data[HEADERSIZE:])
            #if data[1] == "DE-REG":
               # delete_user(data,users)


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