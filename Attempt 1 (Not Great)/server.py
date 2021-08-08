import socket
import threading

HEADER = 64
PORT = 6667
#SERVER = socket.gethostbyname(socket.gethostname())
#ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = ""

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server.bind(("::1", PORT))

class myObject:
	socket = ""
	username = ""
	nickname = ""
	realname = ""

	def __init__ (self, s, u, n, r):
		self.socket = s
		self.username = u
		self.nickname = n
		self.realname = r

users = []
channels = {}

def handle_client(conn, addr):
	print(f"[NEW CONNECTION] {addr} connected. ")

	connected = True
	while connected:
		#Blocking line of code, won't pass the line until we receive a message from the client
		message = conn.recv(2 ** 30).decode(FORMAT)
		print ("-------------------------------------------------------")
		print(f"Message from the client is: {message}---------------------------------------")


		#finding the user who sent the message
		#how many users we have atm
		listLength = len(users)
		for i in range(listLength):
				if users[i].socket == conn:
					this = i

		#--------------------------------------------------- PART -------------------------------------------------------

		if message.startswith("PART"):
			splitS = message.split(" ")
			cName = splitS[1][1:]
			messageNew = ":" + str(users[this].nickname)+"!"+str(users[this].username)+"@::1 PART " + str(splitS[1]) + " :Leaving\n"
			conn.send(messageNew.encode())
			channels[cName].remove(users[this].nickname)

			for i in channels[cName]:
				for j in range(listLength):
						if users[j].nickname == i: #and users[j].nickname != users[this].nickname:
							print("Sending PART message to ", users[j].nickname)
							users[j].socket.send(messageNew.encode())


		# ------------------------------------------------- PRIVMSG in a channel -----------------------------------------------------

		if message.startswith("PRIVMSG "):
			stringToSplit = message.split(" ",2)
			nicknameToSendTo = stringToSplit[1]
			messageReceived = stringToSplit[2]
			#print("Private message: ", messageReceived)
			#find user to send it to
			for j in range(listLength):
				if users[j].nickname == nicknameToSendTo:
					messageToSend =":" + str(users[this].nickname) + "!" + str(users[j].username) + "@::1 PRIVMSG " + str(users[j].nickname) + " " + str(messageReceived)
					users[j].socket.send(messageToSend.encode())


			if message.startswith("PRIVMSG #"):
				split_string = message.split(" ",2)
				channelName = split_string[1][1:]
				privateMes = split_string[2][1:]

				messageNew =":" + str(users[this].nickname) + "!" + str(users[this].username) + "@::1 PRIVMSG " + str(split_string[1]) + " " + str(split_string[2]) 

				for i in channels[channelName]:
					#we need to find the data of the user with that nickname
						for j in range(listLength):
							if users[j].nickname == i and users[j].nickname != users[this].nickname:
								users[j].socket.send(messageNew.encode())



		# -------------------------------------------------  REGISTERTING A USER ------------------------------------------
		if message.startswith("CAP"):
			split_string = message.strip().split("\r\n")
			#print("Split string is: ", split_string)

			NICK = split_string[1][5:]
			#print("Nickname:", NICK)

			getUsername = split_string[2].split(" ")
			USRNAME = getUsername[1]
			#print("Username:", USRNAME)

			RLNAME = getUsername[4][1:]
			#print("Realname:", RLNAME)

			users.append(myObject(conn,USRNAME,NICK,RLNAME))
			print("Object created successfully! \n")

			del split_string

		#------------------------------------------------------- NICK -------------------------------------------------------

		#getting the new nickname
		if message.startswith("NICK"):
			split_string = message.split(" ")
			NICK = split_string[1][:-2] #removing the \n in the end
			oldNickname = users[this].nickname
			#updating object
			users[this].nickname = NICK

			#:nickname!username@::1 NICK changedNickname
			messageNew = ":" + str(oldNickname) + "!" + str(users[this].username) + "@::1 NICK " + str(NICK) + "\n" 
			conn.send(messageNew.encode())

			#print("Username successfully changed to",NICK)

			#updating other channels with the new nickname
			for key in channels:
				if oldNickname in channels[key]:
					#print("Found old nickname in the list")
					for i in channels[key]:
						count = 0
						#updating nickname
						if i == oldNickname:
							#print("It updated the old nickname")
							#print("Old Nickname:", oldNickname)
							channels[key][count] = NICK
						#we need to find the data of the user with that nickname
						for j in range(listLength):
							if users[j].nickname == i and users[j].nickname != users[this].nickname:
								print("Sending the message to", users[j].nickname)
								users[j].socket.send(messageNew.encode())
						count = count + 1


		# ----------------------------------------- JOIN -----------------------------------------------------
		if message.startswith("JOIN"):
			splitString = message.split(" ")
			channelName = splitString[1][1:-2] #removing the hash in the beginning and the \n in the end

			
			#checking if that channel already exists
			if channelName in channels:
				print("Channel already exists!")

				#making other users in the channel aware someone joined them
				for i in channels[channelName]:
				#we need to find the data of the user with that nickname
					for j in range(listLength):
						if users[j].nickname == i:

							messageNew =":" + str(users[this].nickname) + "!" + str(users[this].username) + "@::1 JOIN " + str(splitString[1]) 
							users[j].socket.send(messageNew.encode())


				m1 = ":" + str(socket.gethostname()) + " 331 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " :No topic is sent\n"
				conn.send(m1.encode())

				listOfUsers=""
				for i in channels[channelName]:
					listOfUsers = listOfUsers + " " + i 
				#print("List of users:", listOfUsers)

				
				m2 = ":" + str(socket.gethostname()) + " 353 " + str(users[this].nickname) + " = " + str(splitString[1][:-2]) + " :" + str(listOfUsers) + "\n"
				conn.send(m2.encode())
				
				m3 = ":" + str(socket.gethostname()) + " 366 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " :End of NAMES list\n"
				conn.send(m3.encode())
				
				m4 = ":" + str(socket.gethostname()) + " 324 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " +\n"
				conn.send(m4.encode())

				for i in channels[channelName]:
					#we need to find the data of the user with that nickname
					for j in range(listLength):
						if users[j].nickname == i:
							m5 = ":" + str(socket.gethostname()) + " 352 " + str(users[j].nickname) + " " + str(splitString[1][:-2]) + " " + str(users[j].username) + " ::1 " + str(socket.gethostname()) + " " + str(users[j].nickname) + " H :0 " + str(users[j].realname) + "\n" 
							conn.send(m5.encode())

				m6 = f":{str(socket.gethostname())} 315 {str(users[this].nickname)} {str(splitString[1][:-2])} :End of WHO list\n"
				conn.send(m6.encode())	  

				channels[channelName].append(users[this].nickname)
				print(users[this].nickname, "successfully added to channel", channelName, " !")

			else:
				print("Chanel doesn't exist. Creating new channel and adding user to it.")
				channels[channelName]=[users[this].nickname]
				print(users[this].nickname, "successfully added to channel", channelName, " !")

			messageNew = f":{str(users[this].nickname)}!{str(users[this].username)}@::1 JOIN {str(splitString[1])}" #no need to add \n, its appended to the string

			conn.send(messageNew.encode())

			#del listOfUsers

		#------------------------------------------- MODE -----------------------------------------------------

		if message.startswith("MODE"):

			m1 = ":" + str(socket.gethostname()) + " 331 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " :No topic is sent\n"
			conn.send(m1.encode())

			listOfUsers=""
			for i in channels[channelName]:
				listOfUsers = listOfUsers + " " + i 
			#print("List of users:", listOfUsers)

			
			m2 = ":" + str(socket.gethostname()) + " 353 " + str(users[this].nickname) + " = " + str(splitString[1][:-2]) + " :" + str(listOfUsers) + "\n"
			conn.send(m2.encode())
			
			m3 = ":" + str(socket.gethostname()) + " 366 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " :End of NAMES list\n"
			conn.send(m3.encode())
			
			m4 = ":" + str(socket.gethostname()) + " 324 " + str(users[this].nickname) + " " + str(splitString[1][:-2]) + " +\n"
			conn.send(m4.encode())

			for i in channels[channelName]:
				#we need to find the data of the user with that nickname
				for j in range(listLength):
					if users[j].nickname == i:
						m5 = ":" + str(socket.gethostname()) + " 352 " + str(users[j].nickname) + " " + str(splitString[1][:-2]) + " " + str(users[j].username) + " ::1 " + str(socket.gethostname()) + " " + str(users[j].nickname) + " H :0 " + str(users[j].realname) + "\n" 
						conn.send(m5.encode())

			m6 = f":{str(socket.gethostname())} 315 {str(users[this].nickname)} {str(splitString[1][:-2])} :End of WHO list\n"
			conn.send(m6.encode())	

			#del listOfUsers  

		#---------------------------------------------WHO -----------------------------------------------------

		if message.startswith("WHO"):
			for i in channels[channelName]:
				#we need to find the data of the user with that nickname
				for j in range(listLength):
					if users[j].nickname == i:
						m5 = ":" + str(socket.gethostname()) + " 352 " + str(users[j].nickname) + " " + str(splitString[1][:-2]) + " " + str(users[j].username) + " ::1 " + str(socket.gethostname()) + " " + str(users[j].nickname) + " H :0 " + str(users[j].realname) + "\n" 
						conn.send(m5.encode())

			m6 = f":{str(socket.gethostname())} 315 {str(users[this].nickname)} {str(splitString[1][:-2])} :End of WHO list\n"
			conn.send(m6.encode())	  


	conn.close()


def start():
	server.listen()
	print(f"[LISTENING] Server is listening on {PORT}")
	while True:
		#The line blocks - will wait on new connection to the server
		#We store the address and port and an object allowing us to send information back to the client
		#Conn is a socket object
		conn, addr = server.accept()
		#When a new connection occurs, we are passing it to that function with the parameters
		thread = threading.Thread(target=handle_client, args=(conn, addr))
		thread.start()
		#Tells us how many threads are active. Since there is always one thread listening for connection we do - 1 
		print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1 }")

print("[START] server is starting ... ")
start()