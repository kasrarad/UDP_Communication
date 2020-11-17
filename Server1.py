import schedule
import socket
import threading
import time
import pickle
from functions import list_register_file,check_register_file,append_register_file,delete_register_entry,get_users,get_addresses,get_subjects

# IP and PORT of the servers
PORT1 = 5050
PORT2 = 9999
SERVER1 = socket.gethostbyname(socket.gethostname())
SERVER2 = socket.gethostbyname(socket.gethostname())

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

change_ip_port = False
run_server = True

# Length of massage
HEADERSIZE = 10


def create_socket():
    try:
        global HOST
        global PORT
        global server
        global ADDR

        HOST = SERVER1
        PORT = PORT1
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
        #server.bind(('', PORT))

        if SERVER_NUM == 0:
            print(f"[LISTENING] Server B is listening on {HOST} and Port: {PORT}")
        else:
            print("Server A is waiting to start")

    except socket.error as e:
        print("Socket binding error: " + "\n" + "Retrying...")
        bind_socket()


def start_shell():
    while True:
        cmd = input("zyra> ")

        if cmd == "list":
            list_users()
        elif cmd == "listregister":
            list_register_file()
        elif "port" in cmd:
            change_port(cmd)
        elif "ip" in cmd:
            change_ip(cmd)
        else:
            print("Wrong Command")


def list_users():
    print("----Users----" + "\n")
    for i in range(len(users)):
        results = str(i) + "    " + str(addresses[i][0]) + "    " + str(addresses[i][1]) + "\n"
        print(results)


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

    users = get_users()
    addresses = get_addresses()
    subjects = get_subjects()

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
    #TODO not sure if its needed to save file because its updated whenever we add, update, or delete
    # it is possible to dump everything from the text file into a msg and send it when switching

    server_addr = (SERVER2, PORT2)
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
        data = {1: "CHANGE-SERVER", 2: SERVER2, 3: PORT2}
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
    global SERVER2
    global PORT2

    if run_server:
        #time.sleep(5)
        print("Message received from client: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
        # Get message length (from header) and Convert it to the integer
        msg_length = int(data[:HEADERSIZE])
        if msg_length <= 1028:
            data = pickle.loads(data[HEADERSIZE:])
            if data[1] == "UPDATE-SERVER":
                SERVER2 = data[2]
                PORT2 = data[3]
            elif data[1] == "REGISTER":
                handle_registration(data, addr)
            elif data[1] == "DE-REGISTER":
                handle_de_registration(data, addr)
            elif data[1] == "ADD_SUBJECT":
                handle_subject(data, addr)
            elif data[1] == "DEL_SUBJECT":
                handle_subject(data, addr)
        else:
            print("Message length is more than the buffer size")
    else:
        print("Message received from server: " + "IP: " + addr[0] + "Port: " + str(addr[1]))
        # Get message length (from header) and Convert it to the integer
        msg_length = int(data[:HEADERSIZE])
        if msg_length <= 1028:
            data = pickle.loads(data[HEADERSIZE:])
            if data[1] == "DE-REG":
                delete_user(data)


def handle_registration(cmd, addr):
    global SERVER
    global server
    global users
    global addresses

    if cmd[1] == "REGISTER":
        check = True
        for user_name in users:
            if user_name == cmd[3]:
                check = False
        if check:
            users.append(cmd[3])
            addresses.append(addr)
            subjects.append([])
            data = {1: "REGISTERED", 2: cmd[2]}
            sub = []  # initialize empty subject array for future use
            append_register_file({1: "REGISTERED", 2: cmd[2], 3: cmd[3], 4: cmd[4], 5: cmd[5], 6: sub})  # output to text file
        else:
            data = {1: "REGISTER-DENIED", 2: cmd[2], 3: "Name already exist. Use another name"}

    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        server.sendto(msg, addr)
    except:
        print("Error sending message")


def handle_de_registration(cmd, addr):
    global SERVER
    global server
    global users
    global addresses

    if cmd[1] == "DE-REGISTER":
        check = False
        index = -1
        for user_name in users:
            if user_name == cmd[3]:
                index = users.index(user_name)
                check = True
        if check:
            del users[index]
            del addresses[index]
            data = {1: "DE-REGISTER", 2: cmd[2]}
            delete_register_entry(cmd[3])  # remove from textfile
            msg = pickle.dumps(data)
            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
            try:
                server.sendto(msg, addr)
            except:
                print("Error sending message")

            server_addr = (SERVER2, PORT2)
            data1 = {1: "DE-REG", 2: cmd[3]}
            msg1 = pickle.dumps(data1)
            msg1 = bytes(f'{len(msg1):<{HEADERSIZE}}', FORMAT) + msg1
            try:
                server.sendto(msg1, server_addr)
            except:
                print("Error sending message")


def handle_subject(cmd, addr):
    global SERVER
    global server
    global users
    global addresses
    global subjects

    if cmd[1] == "ADD_SUBJECT":
        data = cmd[3].split()
        check = False
        subs = []
        for k in range(1, len(data)):
            subs.append(data[k])

        for subject in subjects:  # for each user/subject dict in the subjects object
            if subject[1] == data[0]:  # if the username matches then
                delete_register_entry(data[0])  # delete the entry in the file
                new = {1: "REGISTERED", 2: cmd[2], 3: data[0], 4: cmd[4], 5: cmd[5], 6: subs}  # make new dict
                append_register_file(new)  # add the info again
                subjects = get_subjects()  # refresh global subjects array

            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subs}
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


def delete_user(cmd):
    global users

    check = False
    index = -1
    for user_name in users:
        if user_name == cmd[2]:
            index = users.index(user_name)
            check = True
    if check:
        del users[index]
        del addresses[index]
        delete_register_entry(cmd[3])
        ######################## Update the file (Delete the user) ##############################


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

