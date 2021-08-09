import threading
import socket
import time
import string
import re

#list of commands from client to process

chatFunctions = [
    'NICK',
    'JOIN',
    'USER',
    'PART',
    'PRIVMSG',
    'MODE',
    'WHO',
    'PING'
]

#ipv6 address and port and version for welcome
p_host = '::1'
p_port = 6667
version = "1.0"

#list of users array to store all users on the server at any given time
listOfUsers = []
#dictionary of channels to hold channels and the channels hold a list of users connected to them
channels = {}

#Join a channel function - if channel does not exist, create
#make sure the channel is less than 200 char
def joinChannel(channel, user):

    if(channel.startswith('#') and len(channel) < 200):

        if(channel in channels):
            if(user.nickname not in channels[channel]):
                channels[channel].append(user)

                msg = f":{user.nickname}!tested@{user.address[0]} JOIN {channel}\r\n"
                user.getMessage(msg)

                phrase = 'You have successfully joined ' + channel + '! :)\r\n'
                user.getMessage(phrase)

            elif(user in channels[channel]):
                phrase = 'You are already in ' + channel +'! \r\n'
                user.getMessage(phrase)

        elif(channel not in channels):
            channels[channel] = []
            channels[channel].append(user)
            msg = f":{user.nickname}!tested@{user.address[0]} JOIN {channel}\r\n"
            user.getMessage(msg)
            phrase = 'You have successfully joined ' + channel + '! :)\r\n'
            user.getMessage(phrase)

    elif(not channel.startswith('#') or len(channel) > 200):
        phrase = 'This is an invalid channel name. Please start it with # and use less than 200 characters.\r\n'
        user.getMessage(phrase)

def leaveChannel(channel, user):

    if(channel not in channels):
        phrase = channel + ' does not exist! :(\r\n'
        user.client.send(bytes(phrase.encode('utf-8')))

    if(channel in channels):
        if(user in channels[channel]):
            channels[channel].remove(user)
            msg = f":{user.nickname}!tested@{user.address[0]} PART {channel} :Leaving\r\n"
            user.getMessage(msg)
            phrase = 'You have been successfully removed from ' + channel + '! :(\r\n'
            user.getMessage(phrase)

        elif(user not in channels[channel]):
            phrase = 'You are not in ' + channel + '! :(\r\n'
            user.getMessage(phrase)

    if(channel in channels):
        if(len(channels[channel]) == 0):
            print(channel + ' has no more users. Now removing.')
            del channels[channel]

#user class to act as a "mini-server" and route messages to itself
class User:
 # Constructor
    def __init__(self, client, address):
        self.client = client
        self.address = address
        self.nickname = None
        self.realname = None
        self.userName = None

    def setNickname(self, nickname):
        self.nickname = nickname

    def setRealname(self, realname):
        self.realname = realname

    #receive messages
    def getMessage(self, message):
        self.client.send(bytes(message.encode('utf-8')))

    #"listen" for data on repeat
    def receive(self):
        while True:
            data = self.client.recv(1024).decode('utf-8')
            if data.startswith("QUIT"):
                remove_con(self)
                break
            if (data):
                manageMessage(data, self)


#remove connection; remove user when they quit
def remove_con(user):
    if user in listOfUsers:
        listOfUsers.remove(user)

    try:
        for y in channels:
            leaveChannel(y, user)
        user.nickname = None
        user.realname = None
        user.userName = None
        return
    except RuntimeError:
        user.nickname = None
        user.realname = None
        user.userName = None
        return

#parse and send commands to an index of commands
def manageMessage(message, user):

    minceMessage = message.split("\r\n")

    for x in minceMessage:
        for y in chatFunctions:
            if x.startswith(y):
                break_down = x.split(" ")
                if (len(break_down) < 2):
                    user.getMessage('Unacceptable input. Command is unclear.\r\n')
                    return
                runCommand(break_down,x,y,user)

#"index" of commands from IRC
def runCommand(clientInput,fullMsg,key, user):

    if key == 'NICK':
        if nicknameFunction(clientInput, user) == True:
            user.getMessage(f": 002 {user.nickname} :Host - {socket.gethostname()}, Version: {version}\r\n")
            user.getMessage(f": 003 {user.nickname} :Server was createred recently +\r\n")
            user.getMessage(f": 004 {user.nickname} {socket.gethostname()}, {version}\r\n")
            user.getMessage(f": 251 {user.nickname} :Number of users on: {len(listOfUsers)}\r\n")
            user.getMessage(f": 422 {user.nickname} :We were lazy to add a MOTD, but its cool here is this reason instead.\r\n")

    if key == 'USER':
        user.userName = clientInput[1]
        user.realname = clientInput[4].strip(":")

    if key == 'JOIN':
        channel = clientInput[1]
        joinChannel(channel, user)

    if key == 'PART':
        channel = clientInput[1]
        leaveChannel(channel, user)

    if key == 'MODE':
        user.getMessage(f": 324 {user.nickname} {clientInput[1]} +\r\n")
        user.getMessage(f": 331 {user.nickname} {clientInput[1]} :No channel topic for this channel.\r\n")
        for x in channels[clientInput[1]]:
            user.getMessage(f": 353 {user.nickname} = {clientInput[1]} :{x.nickname}\r\n")
        user.getMessage(f": 366 {user.nickname} {clientInput[1]} :End of NAMES list\r\n")

    if key == 'WHO':
        for  y in channels[clientInput[1]]:
            user.getMessage(f": 352 {user.nickname} {clientInput[1]} tested {user.address} {y.nickname} H:0 Preslav\r\n")
        user.getMessage(f": 315 {user.nickname} {clientInput[1]} :End of WHO List\r\n")

    if key == 'PING':
        user.getMessage(f": PONG {clientInput[1]}\r\n")

    if key == 'PRIVMSG':
        messageContentsSplit = fullMsg.split(' :')
        messageContents = messageContentsSplit[0].split('PRIVMSG ')

        if clientInput[1] in channels:
            for x in channels[clientInput[1]]:
                if(x == user):
                    continue
                message = ':'+user.nickname+'!'+user.nickname+'@'+socket.gethostname()+' PRIVMSG '+clientInput[1]+' '+messageContentsSplit[1] +'\r\n'
                x.getMessage(message)

        for x in listOfUsers:
            if(messageContents[1] == x.nickname):
                message = ':'+user.nickname+'!'+user.nickname+'@'+socket.gethostname()+' PRIVMSG '+clientInput[1]+' '+messageContentsSplit[1] +'\r\n'
                x.getMessage(message)
                return
    return

#sets nickname; handles other data initially taken in on registration
def nicknameFunction(minceMessage, user):
    if len(minceMessage[1]) > 10 or minceMessage[1] == "-" or minceMessage[1] == "#":
        print("Incorrect")
        msg = f": 432 {minceMessage[1]} :{minceMessage[1]} is invalid\r\n"
        user.getMessage(msg)
        return False

    try:
        if int(minceMessage[1]):
            print("Incorrect")
            msg = f": 432 {minceMessage[1]} :{minceMessage[1]} is invalid\r\n"
            user.getMessage(msg)
            return False
    except ValueError:
        pass

    for x in listOfUsers:
        if x.nickname == minceMessage[1]:
            print("Taken name")
            msg = f": 433 {minceMessage[1]} :{minceMessage[1]} is taken\r\n"
            user.getMessage(msg)
            return False

    user.nickname = minceMessage[1]
    return True

def privateMessage(message, user):
    return 0


# Receiving / Listening Function
def receive():
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((p_host,p_port))

        listenToYourHeart(server)

#function constantly listening for new connections
def listenToYourHeart(server):
        server.listen()
        while True:
            # Accept Connection
            client, address = server.accept()
            time.sleep(0.02)                    ## Reduce Overloading the buffer with too many inputs

            print("Connected with {}".format(str(address)))

            createUser(client, address)

#create a new user upon connection
def createUser(client, address):
    newUser = User(client, address)
    listOfUsers.append(newUser)

    thread = threading.Thread(target=newUser.receive)
    thread.start()


print("Server is listening...")
receive()
