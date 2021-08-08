#!/usr/bin/python
import socket
import re
import subprocess
import os
import time
import threading
import sys

# Some basic variables used to configure the bot
server = "127.0.0.1" # Server
channel = "#test" # Channel
botnick = "bottest" # Your bots nick


botsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
botsock.connect((server, 6667)) # Here we connect to the server using the port 6667
botsock.send("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n") # user authentication
botsock.send("NICK "+ botnick +"\n") # assign the nick to the bot
def ping(): # responds to server Pings.
  botsock.send("PONG :pingis\n")

def sendmsg(msg): # sends messages to the channel.
 botsock.send(bytes("PRIVMSG "+ channel +" :"+ msg.strip('\n\r') +"\n","UTF-8"))

def joinchan(chan): # join channel(s).
  botsock.send("JOIN "+ chan +"\n")

def whisper(msg, user): # whisper a user
  botsock.send("PRIVMSG " + user + ' :' + msg.strip('\n\r') + '\n')




# log chat messages
def logger(name, msg):
  irclog = open("chatlog.log", 'r')
  content = irclog.readlines()
  irclog.close()
  irclog = open("chatlog.log", "w")
  while len(content) > 100:
    content.remove(content[0])
  if len(content) > 0:
    for i in content:
      irclog.write(i.strip('\n\r') + '\n')
#send newest message to log
  irclog.write(name + ':' + msg.strip('\n\r'))
  irclog.close()




def main():
  joinchan(channel)
  with open("chatlog.log", "w") as temp:
    temp.write("")
#loop to look for new infos on the server
  while 1:
    # clear botmsg value every time
    botmsg = ""
    # set botmsg to new data received from server
    botmsg = botsock.recv(2048)
    # remove any line breaks
    botmsg = botmsg.strip('\n\r')

    print(botmsg)
    # repsonds to pings
    if botmsg.find("PING :") != -1:
      ping()

    if botmsg.find("PRIVMSG") != -1:
      # save user name into name variable
      name = botmsg.split('!',1)[0][1:]
      print('name: ' + name)
      # split message and look for commands
      message = botmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      print(message)
#commands to look for (breaks the code so commented in for now)
#     if len(name) < 17:
#  if message.find('!hello') != -1:
#        sendmsg("Hello " + name + "!")
#
#   if message.find('!slap') != -1:
#      sendmsg("*slaps" + name + 'with a trout*')

     # look for commands and send to appropriate function.
      if message[:2] == 's|':
        regex(message)
      elif message[:2] == 's/':
        sed(message)
      elif message[:5] == '.help':
        help(name,message[5:])
      else:
      # if no command found, get
        if len(name) < 17:
          logger(name, message)


#start main functioin
main()
