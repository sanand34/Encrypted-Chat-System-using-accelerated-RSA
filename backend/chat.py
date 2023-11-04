import sys
import socket
import threading
import rsa as RSA
import datetime
import os


def Server(host, port):
    """
    Creates the server instance, sets up the server
    """
    port = int(port)
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        print("* Waiting for partner to join conversation... *\n")
        conn, client_addr = server.accept()
        # print "Client connected: ", client_addr[0]
        print("* Client attempting to connect... *\n")
    except Exception:
        pass

    # Wait to receive client's public key
    recvIsComplete = False
    key = ""
    while not recvIsComplete:
        key += conn.recv(1024)
        if key.strip("~") and key[0] == "~" and key[-1] == "~":
            recvIsComplete = True
            key = key.strip("~").split(',')
    publicTuple = (key[0], key[1])
    print("* Client\'s Public Key received *")

    # Send public key to the client
    e, d, c = RSA.keygen()
    sendPublic = str(d) + ',' + str(c)
    conn.send("~" + sendPublic + "~")
    print("* Public Key sent *")
    privateTuple = (e, c)

    # Receiving a test string to make sure encryption is working properly
    recvIsComplete = False
    data = ""
    while not recvIsComplete:
        data += conn.recv(1024)
        if data.strip("~") and data[0] == "~" and data[-1] == "~":
            recvIsComplete = True
            data = decrypt(data.strip("~"), publicTuple)

    if data != "~Client:abcdefghijklmnopqrstuvwxyz~":
        print("\n* Encryption could not be verified! Please try to reconnect... *\n")
        conn.send("~ABORT~")
        connClose(conn)
        return

    # Sending a test string to make sure encryption is working properly
    data = "~Server:abcdefghijklmnopqrstuvwxyz~"
    data = encrypt(data.strip(), privateTuple)
    conn.send("~" + data + "~")

    print("\n* Connected to chat *\n*")
    print("1. Type your messages below and hit Enter to send")
    print("2. Type 'file()' and hit Enter to send a file in the current directory")
    print("3. Type 'quit()' and hit Enter to leave the conversation\n")

    ReadThread = Thread_Manager('read', conn, publicTuple, None)
    WriteThread = Thread_Manager('write', conn, None, privateTuple)
    ReadThread.start()
    WriteThread.start()

    # Wait until the client disconnects
    ReadThread.join()
    print("\n* Your partner has left the conversation. Press any key to quit...*\n")

    # Stop the write thread
    WriteThread.stopWrite()
    WriteThread.join()

    # Shut down the client connection
    try:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    except:
        # Connection already closed
        pass

    # Shut down the server
    connClose(server)


def Client(host, port):
    """
    Creates the client instance, sets up the client
    """
    port = int(port)
    print("\n* Connecting to server... *\n")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Send public key to the server
    e, d, c = RSA.keygen()
    sendPublic = str(d) + "," + str(c)
    client.send(("~" + sendPublic + "~").encode('utf-8'))
    print("* Public Key sent *")

    # Wait to receive the server's public key
    recvIsComplete = False
    key = ""
    while not recvIsComplete:
        key += client.recv(1024).decode('utf-8')
        if key.strip("~") and key[0] == "~" and key[-1] == "~":
            recvIsComplete = True
            key = key.strip("~").split(',')
    publicTuple = (int(key[0]), int(key[1]))
    print("* Server\'s Public Key received *")

    privateTuple = (e, c)

    # Sending a test string to make sure encryption is working properly
    data = "~Client:abcdefghijklmnopqrstuvwxyz~"
    data = encrypt(data.strip(), privateTuple)
    client.send(("~" + data + "~").encode('utf-8'))

    # Receiving a test string to make sure encryption is working properly
    recvIsComplete = False
    data = ""
    while not recvIsComplete:
        data += client.recv(1024).decode('utf-8')
        if data.strip("~") and data[0] == "~" and data[-1] == "~":
            recvIsComplete = True

    if data != "~ABORT~":
        data = decrypt(data.strip("~"), publicTuple)
        if data != "~Server:abcdefghijklmnopqrstuvwxyz~":
            print("\n* Encryption could not be verified! Please try to reconnect... *\n")
            client.send("~ABORT~".encode('utf-8'))
            connClose(client)
            return
        else:
            print("\n* Encryption Verified! *")

        print("\n* Connected to chat *\n*")
        print("1. Type your messages below and hit Enter to send")
        print("2. Type 'file()' and hit Enter to send a file in the current directory")
        print("3. Type 'quit()' and hit Enter to leave the conversation\n")

        ReadThread = Thread_Manager('read', client, publicTuple, None)
        WriteThread = Thread_Manager('write', client, None, privateTuple)
        ReadThread.start()
        WriteThread.start()

        ReadThread.join()
        print("\n* Your partner has left the conversation. Press any key to quit... *\n")

        # Stop the write thread
        WriteThread.stopWrite()
        WriteThread.join()

        # Shut down client connection
        connClose(client)


if __name__ == "__main__":
    TESTING = False
    print("\n------------------------------------------------------")
    print(" ENCRYPTED CHAT v1.0 ")
    print("------------------------------------------------------")
    if TESTING:
        host = 'localhost'
        port = 1337
    else:
        if len(sys.argv) < 3:
            print("\nUsage: python encryptedChat.py <hostname/IP> <port>\n")
            input("Press any key to quit")
            exit(0)
        host = sys.argv[1]
        port = sys.argv[2]
    doRead = True
    try:
        Client(host, port)
    except Exception as e:
        if TESTING:
            print(e)
        print("* Server was not found. Creating server... *\n")
        try:
            Server(host, port)
        except Exception as e:
            if TESTING:
                print(e)
            print("* ERROR creating server *\n")
    print("\n* Exiting... Goodbye! *")
