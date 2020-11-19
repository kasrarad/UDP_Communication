import pickle

MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'
HEADERSIZE = 10


def list_register_file():
    print("----Register File Contents----" + "\n")
    reg = []
    with open('register.pickle', 'rb') as handle:
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break
    for user in reg:
        print(user)


def check_register_file(username):
    reg = []   # container for register file
    check = True
    with open('register.pickle', 'rb') as handle:   # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:               # for each line in the register file check if the usernames match
        if username == entry[3]:    # if they match then set check to false,then break
            check = False
            break

    return check


# TODO add locks when appending,updating, or deleting from file.
# takes the full register message as an input, TODO add subject array
def append_register_file(data):
    with open('register.pickle', 'ab') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


# takes username as argument, load file into object, remove username entry from object, overwrite entire register file.
def delete_register_entry(username):
    reg = []  # container for register file
    deleted = False

    with open('register.pickle', 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file check if the usernames match
        if username == entry[3]:  # if they match then set check to false,then break
            reg.remove(entry)
            deleted = True
            break

    with open('register.pickle', 'wb') as handle:
        for line in reg:
            pickle.dump(line, handle)

    return deleted


def get_users():
    reg = []  # container for register file
    users = [] #container for users
    with open('register.pickle', 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        users.append(entry[3])  # append each user entry[3] should correspond to name

    return users


def get_addresses():
    reg = []  # container for register file
    adds = [] #container for adds
    with open('register.pickle', 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        adds.append((entry[4], entry[5]))  # append each user entry[4],entry[5] should correspond to ip,port

    return adds


def get_subjects():
    reg = []  # container for register file
    subs = []  # container for subjects
    with open('register.pickle', 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        temp = {1: entry[3], 2: entry[6]}
        subs.append(temp)

    return subs


def list_users():
    users = get_users()
    addresses = get_addresses()
    print("----Users----" + "\n")
    for i in range(len(users)):
        results = str(i) + "    " + str(addresses[i][0]) + "    " + str(addresses[i][1]) + "\n"
        print(results)


def handle_registration(cmd, addr,server,users,addresses):

    if cmd[1] == "REGISTER":
        check = True
        for user_name in users:
            if user_name == cmd[3]:
                check = False
        if check:
            users.append(cmd[3])
            addresses.append(addr)
            #subjects.append([])
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


def handle_de_registration(cmd, addr,server,users,addresses,ip_addr,port_num):

    if cmd[1] == "DE-REGISTER":
        check = False
        index = -1
        for user_name in users:
            if user_name == cmd[3]:
                print("found user")
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

            #server_addr = (SERVER2, PORT2)
            server_addr = (ip_addr, port_num)
            data1 = {1: "DE-REG", 2: cmd[3]}
            msg1 = pickle.dumps(data1)
            msg1 = bytes(f'{len(msg1):<{HEADERSIZE}}', FORMAT) + msg1
            try:
                server.sendto(msg1, server_addr)
            except:
                print("Error sending message")


def handle_subject(cmd, addr,server,users,addresses,subjects):
    check = False
    if cmd[1] == "ADD_SUBJECT":
        data = cmd[3].split()
        name = data[0]

        subs = []
        for k in range(1, len(data)):
            if data[k] not in subs:
                subs.append(data[k])

        for subject in subjects:  # for each user/subject dict in the subjects object
            if subject[1] == name:  # if the username matches then
                check = True
                for item in subject[2]:  # for each subject in the users subject list
                    if item not in subs:    # if the subject is not part of the updated list then add it
                        subs.append(item)   # subs now contains old list plus new list
                delete_register_entry(name)  # delete the entry in the file
                new = {1: "REGISTERED", 2: cmd[2], 3: name, 4: cmd[4], 5: cmd[5], 6: subs}  # make new dict
                append_register_file(new)  # add the info again
                subjects = get_subjects()  # refresh global subjects array
        if check:
            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subs}
        else:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Name does not exist."}

    if cmd[1] == "DEL_SUBJECT":
        data = cmd[3].split()
        name = data[0]
        subs = []
        for subject in subjects:  # for each user/subject dict in the subjects object
            if subject[1] == name:  # if the username matches then
                check = True
                for item in subject[2]:  # for each subject in the users subject list
                        subs.append(item)  # add the subject to the list

        for k in range(1, len(data)):  # for each subject in the message
            if data[k] in subs:         # if the subject is present in the users sub list
                subs.remove(data[k])    # remove that value from the list

        delete_register_entry(name)  # delete the entry in the file
        new = {1: "REGISTERED", 2: cmd[2], 3: name, 4: cmd[4], 5: cmd[5], 6: subs}  # make new dict
        append_register_file(new)  # add the info again
        subjects = get_subjects()  # refresh global subjects array

        if check:
            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subs}
        else:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Name does not exist."}

    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        server.sendto(msg, addr)
    except:
        print("Error sending message")


def delete_user(cmd,users):


    check = False
    index = -1
    for user_name in users:
        if user_name == cmd[2]:
            index = users.index(user_name)
            check = True
    if check:
        del users[index]
        #del addresses[index]
        delete_register_entry(cmd[3])



