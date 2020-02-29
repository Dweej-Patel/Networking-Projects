# Dweej Patel
# UNI: dp3039
# Part 2 PA1

from socket import *
from re import *
from select import *
import sys
import os
import time
import threading
from datetime import datetime

# buffer size
BUFF_SIZE = 1024
FAVICON = "favicon.ico"
# QUEUE for favicon domain
QUEUE = []


def sendToServer(serverSocket, request, domain):
    # Send GET request to server socket
    message = "GET " + request + " HTTP/1.0\r\n" + \
              "Host: " + domain + "\r\n\r\n"
    serverSocket.send(message.encode())


def receiveFromServer(serverSocket):
    # Receive message from socket
    hearder = ''.encode()
    response = ''.encode()
    input_serv = [serverSocket]
    
    while True:
        readable,_,_ = select(input_serv, [], [], 0)
        
        ts = time.time()

        # Try checking if readable until time limit or if readable just move on
        while not readable and (time.time() - ts) < 2:
            readable, _, _ = select(input_serv, [], [], 0)
        
        if readable:
            resp = serverSocket.recv(BUFF_SIZE)
            if resp:
                response += resp
            else:
                break
        else:
            break
    if response:
        response = response.split("\r\n\r\n".encode())
        header = response[0]
        responseLine = response[0].split("\r\n".encode())[0]
        body = response[1]
    
    else:
        return None, None, None

    return body, responseLine, header


def connectSocket(domain, serverPort):
    # Connect to server
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((domain, serverPort))
    except:
        serverSocket.close()
        return None

    return serverSocket


def checkCache(filename, path, domain, serverPort):

    body, responseLine, header = None, None , None
    lock = threading.Lock()
    # Check if the request exists in cache
    lock.acquire()
    if os.path.exists("."+filename) and not os.path.isdir("."+filename):
        lock.release()
        
        print("Thread: " + str(threading.current_thread().getName()) +\
              "\nReceiving from cache\n\n")

        responseLine = "HTTP/1.0 200 OK".encode()
        header = ''
        
        with open("."+filename, "rb") as f:
            timestr = f.readline()
            body = f.read()
    
    else:
        lock.release()
        
        serverSocket = connectSocket(domain, serverPort)
        if serverSocket:
            sendToServer(serverSocket, path, domain)
            body, responseLine, header = receiveFromServer(serverSocket)
            serverSocket.close()

            if responseLine.split(" ".encode())[1] == "200".encode():
                
                print("Thread: " + str(threading.current_thread().getName()) +\
                      "\nCaching file\n\n")
                lock.acquire()
                try:
                    os.makedirs("."+'/'.join(filename.split('/')[:-1]))
                except:
                    pass

                with open("."+filename, "wb") as f:
                    curr_time = time.localtime()
                    f.write(time.strftime('%m-%d-%Y %H:%M:%S GMT', curr_time).encode() + "\r\n".encode())
                    f.write(body)
                lock.release()
                

    return body, responseLine, header


def workmythread(clientSocket, clientAddr, proxy_port):

        readable, _, _ = select([clientSocket], [], [], 0)
        
        ts = time.time()
        
        # Try checking if readable until time limit or if readable just move on
        while not readable and (time.time() - ts) < 1:
            readable, _, _ = select([clientSocket], [], [], 0)

        if readable:
            # initializing variables to be used later
            body, responseLine, header = None, None, None

            # Receive 1024 bytes from client
            clientMessage = clientSocket.recv(BUFF_SIZE).decode(errors='ignore')
            print("Thread: " + str(threading.current_thread().getName()) +\
                 "\nClient: " + str(clientAddr) +\
                 "\nReceived from client\n\n")

            # Parse requests
            clientHeader = clientMessage.split("\r\n\r\n")[0]
            req = clientHeader.split(" ")[0:2]  # first line is "GET /path HTTP/1.0\r\n" so we want /path/

            if req[0] != "GET" or len(req) <=1:
                clientSocket.close()
                return
            
            request = req[1]

            if not request:
                clientSocket.close()
                return
            
            split_req = request.split('/')
            filename = "/" + "/".join(split_req[1:])
            domain = split_req[1]
            if request[-1] == "/":
                filename += "index.html"
                QUEUE.append(domain)
            elif split_req[-1] == "index.html":
                QUEUE.append(domain)
                
            path = "/" + "/".join(filename.split('/')[2:])
            
            if len(path) <= 1:
                
                if domain == FAVICON:
                    print("Thread: " + str(threading.current_thread().getName()) +\
                     "\nClient: " + str(clientAddr) +\
                     "\nSending favicon.ico \n\n")
                    if QUEUE:
                        domain = QUEUE.pop(0)
                        filename = "/" + domain + "/" + FAVICON
                        path = "/" + FAVICON
                        body, responseLine, header = checkCache(filename, path, domain, serverPort=80)
                else:
                    
                    clientSocket.close()
                    print("Ending thread: " + str(threading.current_thread().getName()) + "\n\n")
                    return
            else:
                
                body, responseLine, header = checkCache(filename, path, domain, serverPort=80)

            if responseLine:
                
                #Handle 301 errors
                if responseLine.split(" ".encode())[1] == "301".encode():
                    
                    print("Thread: " + str(threading.current_thread().getName()) +\
                     "\nClient: " + str(clientAddr) +\
                     "\nRedirecting 301\n\n")
                    
                    values = header.split("\r\n".encode())
                    for v in values:
                        if v[0:9] == "Location:".encode():
                            v = v.decode()
                            filename = "/" + v.split(" ")[1].split("//")[1]
                            if filename[-1] == "/":
                                filename += "index.html"
                                QUEUE.append(domain)
                            elif split_req[-1] == "index.html":
                                QUEUE.append(domain)
                            path = "/" + "/".join(filename.split('/')[2:])
                            domain = filename.split('/')[1]
                            body, responseLine, header = checkCache(filename, path, domain, serverPort=80)
                            break
                
                #Handle 404 on images
                if responseLine.split(" ".encode())[1] == "404".encode():
                    
                    print("Thread: " + str(threading.current_thread().getName()) +\
                     "\nClient: " + str(clientAddr) +\
                     "\nRedirecting 404\n\n")

                    values = clientHeader.split("\r\n")
                    for v in values:
                        if v[0:8] == "Referer:":
                            refer = v[9:]
                            spref = refer.split("/")
                            refstr = ''
                            if len(spref) > 4:
                                refstr = spref[4:]
                                sppath = path[1:].split("/")
                                newpath = []
                                fslook = True
                                for i, sp in enumerate(sppath):
                                    if i < len(refstr) and sp == refstr[i] and fslook:
                                        newpath.append(sp)
                                    elif fslook: 
                                        fslook = False
                                        for load in refstr[i:]:
                                            newpath.append(load)
                                    if not fslook:
                                        newpath.append(sp)
                                path = "/"+"/".join(newpath)
                                filename = "/" + domain + path
                                body, responseLine, header = checkCache(filename, path, domain, serverPort=80)
                            break
                    
                    body, responseLine, header = checkCache(filename, path, domain, serverPort=80)

            if body:

                # Send data back to client
                #referer = "Referer: "+"http://localhost:"+str(proxy_port)+'/'.join(filename.split('/')[:-1])+"/"
                #http = responseLine + "\r\n".encode() + referer.encode() + "\r\n\r\n".encode() + body
                print("Thread: " + str(threading.current_thread().getName()) +\
                     "\nSending to Client: " + str(clientAddr) +\
                     "\nResponse line: " + str(responseLine) + "\n\n")
                referer = "Content-Location: "+"http://localhost:"+str(proxy_port)
                http = responseLine + "\r\n".encode() + referer.encode() + "\r\n\r\n".encode() + body
                #http = responseLine + "\r\n\r\n".encode() + body
                clientSocket.send(http)
            
                clientSocket.close()  # close socket to wait for new request
        else:
            # Or other error handling 
            clientSocket.close()

        print("Ending thread: " + str(threading.current_thread().getName()) + "\n\n")
    
def main():

    # creating and binding the proxy
    proxy_name = 'localhost'
    proxy_port = 8080
    if len(sys.argv) == 2:
        proxy_port = int(sys.argv[1])

    proxySocket = socket(AF_INET, SOCK_STREAM)
    proxySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    proxySocket.bind((proxy_name, proxy_port))
    proxySocket.listen(5)

    while True:
        clientSocket, clientAddr = proxySocket.accept()  # Accept a connection
        clientSocket.setblocking(0)

        # Create a thread to handle the request and go back to the to accept more clients
        thread = threading.Thread(target=workmythread, args=(clientSocket,clientAddr,proxy_port,), daemon=True)
        print("Thread created: " + str(thread.getName()) + "\n\n")
        thread.start()
        #print("Before workthread")
        #workmythread(clientSocket,clientAddr, proxy_port)
    
    proxySocket.close()


if __name__ == "__main__":
    main()

