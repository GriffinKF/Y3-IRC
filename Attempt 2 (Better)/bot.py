# Provides the modules required
import socket
import threading
import os
import random
import sys
import time
from datetime import datetime

# Allows for the creation of bot objects
class bot:

    # Seting the bots initial state upon object creation
    def __init__(self, name, realname, server, port, channel):
        # Define the socket to give access to networking
        self.ircBot = socket.socket()
        
        # Bot details declared to give access throughout the class
        self.name = name
        self.realname = realname
        self.server = server
        self.port = port
        self.channel = channel
        self.users = []
        self.on = True

        # Providing a list of facts for the bot to send
        try:
            f = open("facts.txt", "r")
            self.facts = []
            for x in f:
                self.facts.append(x)
            f.close()
        except:
            facts.append("Facts database experiencing downtime")

    # Allows the bot to update the data about the users
    def update(self):
        self.names(self.channel)

    # To allow the bot to send messages
    def send(self, command, args):
        # Transfer data
        try:
            self.ircBot.send(bytes("%s %s\r\n" % (command, args), "ascii"))
            print("%s %s\n" % (command, args))
        except:
            print("Error sending message - \"%s %s\"" % (command, args))

    # To allow the bot to recieve messages
    def receive(self):
        try:
            return self.ircBot.recv(2040).decode("ascii")
        except:
            return "ERROR"

    # Provides the structure needed to use the PRIVMSG command
    def privmsg(self, recipient, message):
        self.send("PRIVMSG", "%s :%s" % (recipient, message))
    
    # Provides the structure needed to use the PONG command
    def pong(self):
        self.send("PONG", self.server)

    # Provides the structure needed to use the USER command
    def user(self):
        self.send("USER", "%s %s %s :%s" % (self.name, self.name, self.name, self.realname))

    # Provides the structure needed to use the NICK command
    def nick(self):
        self.send("NICK", ":%s" % self.name)

    # Provides the structure needed to use the JOIN command
    def join(self):
        self.send("JOIN", ":%s" % self.channel)

    # Provides the structure needed to use the QUIT command
    def quit(self):
        self.send("QUIT", "")

    # Provides the structure needed to use the NAMES command and handle the response
    def names(self, channel):
        self.send("NAMES", ":%s" % self.channel)
        inMessage = self.receive()
        
        if "353" in inMessage:
            inMessageSplit = inMessage.split(self.channel)
            self.users = inMessageSplit[1].split("\r\n")
            self.users = self.users[0].split()
            
    # Setups the connection with the IRC server
    def connect(self):
        print("Connecting to: " + self.server)
        
        try:
            self.ircBot = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.ircBot.connect((self.server, self.port))
        except:
            print("Already connected to socket")
            
        self.user()
        self.nick()
        self.join()

    # Disconnects the bot from the IRC server
    def disconnect(self):
        self.quit()
        
        try:
            self.ircBot.shutdown(socket.SHUT_RDWR)
            self.ircBot.close()
            
        except:
            pass
        
    # Processes the messages relayed from the server
    def process(self):
        inMessage = self.receive()
        outMessage = ""

        # Allows the bot to accomodate for connection errors
        if inMessage != "ERROR":
            print (inMessage)
        
            # Allows the bot to distinguish between different IRC commands
            if "PING" in inMessage:
                self.pong()

            elif "PRIVMSG" in inMessage:
                inMessageSplit = inMessage.split()
                prefix = inMessageSplit[0].split("!")
                channel = self.channel
                origin = prefix[0].replace(":", "")

                # Allows the bot to distinguish between messages sent in channels vs private messages, and respond
                if channel in inMessage:

                    # Provides functionality for bot commands
                    if "!slap" in inMessage:
                        outMessage = "%s has been slapped with a trout!" % random.choice(self.users)
                        self.privmsg(channel, outMessage)
                
                    elif "!hello" in inMessage:
                        outMessage = "Hello! It is :%s" % str(datetime.now())
                        self.privmsg(channel, outMessage)

                    #Allows the bot to terminate safely
                    elif "!off" in inMessage:
                        self.on = False
                        return False

                elif self.name:
                    outMessage = random.choice(self.facts)
                    self.privmsg(origin, outMessage)

        else:
            print("\nError receiving messages from client, reconnecting...\n")
            return False
        
        # Allows the bot to loop and update   
        return True

# Config details of the bot
p_host = '::1'
p_port = 6667
name = "ludovic"
realname = "bot"
channel = "#test"

# Creating and connecting the bot
ludo = bot(name, realname, p_host, p_port, channel)
ludo.connect()

# Runs the bot loop whilst on
while ludo.on:
    while ludo.process():
        ludo.update()

    # Disconnects the bot
    ludo.disconnect()

    # Allows for reconnection if premature disconnection
    if ludo.on:
        time.sleep(5)
        ludo.connect()
