# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 09:41:09 2018

@author: Alzahraa Elsallakh
"""


'''
Advanced:
    Time ,
    online/offline
    
'''
import socket 
from _thread import *
import threading
import pickle
import sys

print_lock = threading.Lock()

# User: IP, user_name, password, c

##                    pass, c,   ip
## users = {"hatem" :[123, 12 , 5555]}

users = dict()
online = 1
offline = 0


def chat(c,sender_username):
    global users
    debug("before chat")
    while True:
        #debug(sender_username  + " start chat")
        message = recieveFromCleint(c)
        debug(users)
        message = ">" + sender_username + ': ' + message
        if "<LOGOUT>" in message:
            message = sender_username + " logout"
            users[sender_username][3] = offline
            for client in users:
                if users[client][3]:
                    reciever_client = users[client][1]
                    sendMessage(reciever_client, message)
            sendMessage(c , "logout")
            c.close()
            break

        elif "<Private>" in message:
            sendMessage(c, "To:")
            privateReceiver = recieveFromCleint(c)
            privateReceiverInstance = users[privateReceiver][1]
            privateMessage = "Private message from: " + sender_username
            sendMessage(privateReceiverInstance, privateMessage)
            sendMessage(privateReceiverInstance, recieveFromCleint(c))

        else:

            for client in users:
                if users[client][3] and client != sender_username:
                    reciever_client = users[client][1]
                    sendMessage(reciever_client, message)

def startLogin(c , msg): #msg = login / register
    #recieve username and password from user
    sendMessage(c ,msg)
    info = c.recv(1024)
    info_dec = pickle.loads(info)

    return info_dec[0]  ,info_dec[1]   
    
def debug(msg):
    print_lock.acquire()
    print (msg)
    print_lock.release()

def saveUser(username , password , c , ip): #save user in database
    global users
    users[username] = [password , c , ip, online]
    debug("register success")
    debug(users)

def recieveFromCleint(c):
    data = c.recv(1024)
    data = str(data.decode('ascii'))
    
    return data

def sendMessage(c , msg):     
    c.send(msg.encode('ascii'))


def hasJoinedMessage(username):
    # print has joined the chat
    joined_msg = "<JOINED>" + username + " has joined the Chat..."
    for key in users.keys():
        if users[key][3]:
            client = users[key][1]
            sendMessage(client , joined_msg)
    debug("before chat")
    chat(users[username][1], username)


def logReg(c, ip):
    username , password = startLogin(c , "login")
    debug(users)

    # check if user exist or not
    #login function
    debug("start LOGIN!!")
    if len(users) > 0 and username in  users.keys() :
        debug("LOGIN success")
        if users[username][0] == password:
            #welcome message    
            """
            if username in notSendTo:
                print_lock.acquire()
                notSendTo.remove(username)
                print_lock.release()
            """
            sendMessage(c , "welcome") 
            debug("WELCOME") 
            users[username][1] = c
            users[username][3] = online
            debug(users)
            # print has joined the chat
            hasJoinedMessage(username)
            debug("JOINED B2A")
        else:
            sendMessage(c, "wrongpass")
            logReg(c, ip)

    else:
        #register function
        debug("start REGISTER!!!")
        c.send("register".encode('ascii'))

        getReply = c.recv(1024)
        getReply = str(getReply.decode('ascii'))
        if getReply == "yes":
            userInfo = c.recv(1024)
            userInfo_dec = pickle.loads(userInfo)
            username, password = userInfo_dec[0], userInfo_dec[1]
            saveUser(username , password , c , ip)
            hasJoinedMessage(username)
        elif getReply == "no":
            logReg(c, ip)
        
        # print has joined the chat
        #hasJoinedMessage(username)


def threaded(c,ip):
    global users
    while True:  
        try:   
            
            logReg(c, ip)

            #break
        except:
            
            #debug("user " + username + " logged out!!")
            userName = ""
            for key in users.keys():
                if users[key][2] == ip:
                    userName = key
                    break

            users[userName][3] = offline
            logout_msg = "<LOGOUT>" + userName + " logged out!!"
            for user in users:
                if users[user][3]:
                    users[user][1].send(logout_msg.encode('ascii'))
            debug(users)
            break

    c.close()
    
def Main():
    """
    try:
        host = socket.gethostbyname("0.tcp.ngrok.io")
    except socket.gaierror:
        print("Host Error!!!")
        sys.exit()
    """
    host = ""
    port = 3000
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("Socket binded to post", port) 
    s.listen(5)
    print("Socket is listneing")
    
    while True:

        c, addr = s.accept()
        print_lock.acquire()
        print('Connected to: ', addr[0],':',addr[1])
        print_lock.release()        
        start_new_thread(threaded, (c,addr,))
    s.close()
    
if __name__ == '__main__':
    Main()