import pickle

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