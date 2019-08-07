# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 09:48:25 2018

@author: Alzahraa Elsallakh
"""
import socket
import pickle
import sys
from _thread import *
import threading

print_lock = threading.Lock()

def recieve(s):
    
    while True:
        recieved_msg = s.recv(1024)  
        recieved_msg = str(recieved_msg.decode('ascii'))
        if "<JOINED>" in recieved_msg:
            recieved_msg = recieved_msg.replace("<JOINED>", "")
        elif "<LOGOUT>" in recieved_msg:
            recieved_msg = recieved_msg.replace("<LOGOUT>", "")
        elif recieved_msg == "logout":
            print("press enter to logout")
            s.close()
            break
            #s.close()
        
        #print_lock.acquire()
        print(recieved_msg)
        #print_lock.release()

def send(s):    
    try:

        while True:

            msg_to_send = input()
            #print("after input")
            s.send(msg_to_send.encode('ascii'))
    except:
            #print("after except")
            s.close()
            
        


def logReg(s):

    print("Enter your username and pass: ")
    username = input('username: ')  
    password = input('paswword: ') 
    info = [username, password]
    info_pic=pickle.dumps(info)
    s.send(info_pic)

    m = s.recv(1024)
    m = str(m.decode('ascii'))

    if m == "wrongpass":
        print("Wrong password, please try again !!")
    
    if m == "welcome":
            print ("welcome to konami chat")
    
    if "<LOGOUT>" in m:
            m = m.replace("<LOGOUT>", "")
            print(m)

    if m == "register":
        #print (msg)
        print("Not exist, do you want to register it? y/n")
        q = input()
        if q == "y":
            info_pic=pickle.dumps(info)
            s.send("yes".encode('ascii'))
            s.send(info_pic)
            
        elif q == "n":
            s.send("no".encode('ascii'))
            #logReg(s)


def Main():
    
    host = '127.0.0.1'
    """
    try:
        host = socket.gethostbyname("0.tcp.ngrok.io")
        print("HOST OK")
    except:
        print("Host Error!!!")
        sys.exit()
    """
    port = 3000
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host, port))
    print("Done...")
    
    
    #while True:
    data=s.recv(1024)
    msg = str(data.decode('ascii'))
    if msg == "login":
        logReg(s)
    
    # success enter to the chat
    data=s.recv(1024)
    msg = str(data.decode('ascii'))  
    if "<JOINED>" in msg:
        msg = msg.replace("<JOINED>", "")
        print(msg)
        ## Going Chat...
        R = threading.Thread(target = recieve, args=(s,))
        #S = threading.Thread(target = send, args=(s,))
        
        R.start()
        #S.start()
        send(s)
        R.join()
        #S.join()
        

        
          
    s.close()
    
if __name__ =='__main__':
    Main()