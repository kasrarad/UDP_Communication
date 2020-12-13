import pickle5 as pickle

MAX_MSG_SIZE = 1500
FORMAT = 'utf_8'
HEADERSIZE = 10

available_subj = ["COEN445", "ENGR301", "SOEN342", "ELEC490"]


def list_register_file(filename):
    print("----Register File Contents----" + "\n")
    reg = []
    with open(filename, 'rb') as handle:
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break
    for user in reg:
        print(user)


def check_register_file(filename,username):
    reg = []   # container for register file
    check = True
    with open(filename, 'rb') as handle:   # open register file, each line is loaded until end of file error
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
def append_register_file(filename,data):
    with open(filename, 'ab') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


# takes username as argument, load file into object, remove username entry from object, overwrite entire register file.
def delete_register_entry(filename,username):
    reg = []  # container for register file
    deleted = False

    with open(filename, 'rb') as handle:  # open register file, each line is loaded until end of file error
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

    with open(filename, 'wb') as handle:
        for line in reg:
            pickle.dump(line, handle)

    return deleted


def display_log(filename):
    print("----Publish Message Log----" + "\n")
    log = []
    with open(filename, 'rb') as handle:
        while 1:
            try:
                log.append(pickle.load(handle))
            except EOFError:
                break
    for user in log:
        print(user)


def get_users(filename):
    reg = []  # container for register file
    users = [] #container for users
    with open(filename, 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        users.append(entry[3])  # append each user entry[3] should correspond to name

    return users


def get_addresses(filename):
    reg = []  # container for register file
    adds = [] #container for adds
    with open(filename, 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        adds.append((entry[4], entry[5]))  # append each user entry[4],entry[5] should correspond to ip,port

    return adds


def get_subjects(filename):
    reg = []  # container for register file
    subs = []  # container for subjects
    with open(filename, 'rb') as handle:  # open register file, each line is loaded until end of file error
        while 1:
            try:
                reg.append(pickle.load(handle))
            except EOFError:
                break

    for entry in reg:  # for each line in the register file
        temp = {1: entry[3], 2: entry[6], 3: (entry[4], entry[5])}
        subs.append(temp)

    return subs

def get_a_users_subjects(username,subjects):
    subs = []
    for subject in subjects:  # for each user/subject dict in the subjects object
        if subject[1] == username:  # if the username matches then
            for item in subject[2]:  # for each subject in the users subject list
               subs.append(item)    #append subject
    return subs


def list_users(filename):
    users = get_users(filename)
    addresses = get_addresses(filename)
    print("----Users----" + "\n")
    for i in range(len(users)):
        results = str(i) + "    " + str(addresses[i][0]) + "    " + str(addresses[i][1]) + "\n"
        print(results)


def handle_registration(filename,cmd, addr,server,users,addresses,subjects):

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
            append_register_file(filename,{1: "REGISTERED", 2: cmd[2], 3: cmd[3], 4: cmd[4], 5: cmd[5], 6: sub})  # output to text file
        else:
            data = {1: "REGISTER-DENIED", 2: cmd[2], 3: "Name already exist. Use another name"}
    elif cmd[1] == "UPDATE":
        check = False
        for user_name in users:
            if user_name == cmd[3]:
                check = True
        if check:

            data = {1: "UPDATE-CONFIRMED", 2: cmd[2], 3: cmd[3], 4: cmd[4], 5: cmd[5]}
            sub = get_a_users_subjects(cmd[3],subjects)
            delete_register_entry(filename,cmd[3])
            append_register_file(filename, {1: "REGISTERED", 2: cmd[2], 3: cmd[3], 4: cmd[4], 5: cmd[5],
                                            6: sub})  # output to text file
        else:
            data = {1: "UPDATE-DENIED", 2: cmd[2], 3: "Name does not exist."}

    msg = pickle.dumps(data)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg
    try:
        server.sendto(msg, addr)
    except:
        print("Error sending message")


def handle_de_registration(filename,cmd, addr,server,users,addresses,ip_addr,port_num):

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
            data = {1: "DE-REGISTER", 2: cmd[3]}
            delete_register_entry(filename,cmd[3])  # remove from textfile
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


def handle_subject(filename,cmd, addr,server,users,addresses,subjects):
    check = 0
    if cmd[1] == "ADD_SUBJECT":
        data = cmd[3].split()
        name = data[0]
        data = [x.upper() for x in data]
        subs = []

        for k in range(1, len(data)):
            if data[k] not in available_subj:
                print(data[k])
                check = 1
                break
            if data[k] not in subs:
                subs.append(data[k])
        if check == 0:
            for subject in subjects:  # for each user/subject dict in the subjects object
                if subject[1] == name:  # if the username matches then
                    check = 2
                    for item in subject[2]:  # for each subject in the users subject list
                        if item not in subs:  # if the subject is not part of the updated list then add it
                            subs.append(item)  # subs now contains old list plus new list
                    delete_register_entry(filename,name)  # delete the entry in the file
                    new = {1: "REGISTERED", 2: cmd[2], 3: name, 4: cmd[4], 5: cmd[5], 6: subs}  # make new dict
                    append_register_file(filename,new)  # add the info again
                    subjects = get_subjects(filename)  # refresh global subjects array
        if check == 0:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Name does not exist."}
        elif check == 1:
            data = {1: "SUBJECTS-REJECTED", 2: cmd[2], 3: "Subject is not in the list of available subjects."}
        elif check == 2:
            data = {1: "SUBJECTS-UPDATED", 2: cmd[2], 3: subs}

    if cmd[1] == "DEL_SUBJECT":
        data = cmd[3].split()
        name = data[0]
        data = [x.upper() for x in data]
        subs = []
        for subject in subjects:  # for each user/subject dict in the subjects object
            if subject[1] == name:  # if the username matches then
                check = True
                for item in subject[2]:  # for each subject in the users subject list
                    subs.append(item)  # add the subject to the list

        for k in range(1, len(data)):  # for each subject in the message
            if data[k] in subs:         # if the subject is present in the users sub list
                subs.remove(data[k])    # remove that value from the list

        delete_register_entry(filename,name)  # delete the entry in the file
        new = {1: "REGISTERED", 2: cmd[2], 3: name, 4: cmd[4], 5: cmd[5], 6: subs}  # make new dict
        append_register_file(filename,new)  # add the info again
        subjects = get_subjects(filename)  # refresh global subjects array

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


def handle_publishing(filename,cmd, addr, server, users, addresses, subjects, publish_log):
    check = 0
    data = cmd[3].split()
    name = data[0]
    subj = data[1].upper()
    words = ""

    for i in range(2, len(data)): # paste the message into a string
        words += data[i] + " "

    for subject in subjects:  # for each user/subject dict in the subjects object
        if subject[1] == name:  # check if the user does exist
            check = 1
            if subj in available_subj:  # check if the subject is in the available list of subject
                check = 2
                if subj in subject[2]:    # check if the subject is on the user's list
                    check = 3

    if check == 0:
        data = {1: "PUBLISHED-DENIED", 2: cmd[2], 3: "Name does not exist."}
    elif check == 1:
        data = {1: "PUBLISHED-DENIED", 2: cmd[2], 3: "Subject is not in the list of available subjects."}
    elif check == 2:
        data = {1: "PUBLISHED-DENIED", 2: cmd[2], 3: "Subject is not in user's list."}
    elif check == 3:
        data = {1: "MESSAGE", 2: name, 3: subj, 4: words}

    msg = pickle.dumps(data)
    append_register_file(publish_log, data)    # writing message into the log file
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

    if check == 3:
        for subject in subjects:  # for each user/subject dict in the subjects object
            if subj in subject[2]:  # check if the subject is on the user's list
                try:
                    server.sendto(msg, subject[3])
                except:
                    print("Error sending message")
    else:
        try:
            server.sendto(msg, addr)
        except:
            print("Error sending message")


def delete_user(filename,cmd,users):

    check = False
    index = -1
    for user_name in users:
        if user_name == cmd[2]:
            index = users.index(user_name)
            check = True
    if check:
        del users[index]
        #del addresses[index]
        delete_register_entry(filename,cmd[3])



