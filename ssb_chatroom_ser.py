import sys, re
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *

class Server(QDialog):
    def __init__(self, parent=None):
        super(Server, self).__init__(parent)
        self.resize(700,700)
        self.setStyleSheet("font-size: 25px")
        
        self.tcpServer = QTcpServer(self)
        self.clients = {}

        self.tcpServer.listen(QHostAddress.Any, 8888)
        self.tcpServer.newConnection.connect(self.newConnection)

        self.client_label = QLabel("Client list")
        self.clientList = QListWidget()
        self.history_label = QLabel("Chat history")
        self.chatHistory = QTextEdit()
        self.chatHistory.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.client_label)
        layout.addWidget(self.clientList)
        layout.addWidget(self.history_label)
        layout.addWidget(self.chatHistory)
        self.setLayout(layout)
        self.setWindowTitle("SSB Chat Room - Server")

    def newConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        clientConnection.readyRead.connect(lambda: self.receiveMessage(clientConnection))
        clientConnection.disconnected.connect(lambda: self.clientDisconnected(clientConnection))

    def receiveMessage(self, clientConnection):
        message = str(clientConnection.readLine().data().decode().strip())
        if message.startswith("Name: "):
            name = message[6:]
            if re.match(r'[a-zA-Z]{1,9}', name):
                item = QListWidgetItem(str(name))
                self.clientList.addItem(item)
                self.clients[name] = clientConnection
                self.broadcastMessage(name + " joined.", clientConnection)
                self.updateClientList()
            else:
                self.chatHistory.append("[System] Invalid name. Refused to join.")
        # elif re.match(r'>>[a-zA-Z]{1,9} .*', message):
        elif re.match(r'[a-zA-Z]{1,9}: >>[a-zA-Z]{1,9} .*', message):
            self.privateMessage(message, clientConnection)
        else:
            matchObj = re.match(r'[a-zA-Z]{1,9}: .*', message)
            fromname = message[:(message.find(":"))]
            if matchObj and fromname in self.clients.keys():
                self.broadcastMessage(message)
            else:
                self.chatHistory.append("[System] Invalid message received. Dumped.")

    def clientDisconnected(self, clientConnection):
        for client in self.clients:
            if self.clients[client] == clientConnection:
                item = self.clientList.findItems(client, Qt.MatchExactly)
                self.clientList.takeItem(self.clientList.row(item[0]))
                self.clients.pop(client)
                self.broadcastMessage(f"{client} left.", clientConnection)
                self.updateClientList()
                break

    def privateMessage(self, message:str, sender):
        # Send the message to private receiver
        message = message[message.find(": ")+2:]
        index = message.find(" ")
        fromname = [name for name in self.clients if self.clients[name] == sender][0]
        toname = message[2:index]
        message = message[index+1:]
        info = ""
        for c in self.clients:
            if c == toname:
                self.clients[c].write(("From " + fromname + ": " + message).encode())
                self.clients[c].flush()
                break
        else:
            info = "[Failed] "

        # Show the message in chat history
        local_history = info + fromname + " -> " + toname + ": " + message
        self.chatHistory.append(local_history)

        # Send the message back to sender as chat history
        if info == "[Failed] ":
            message = "[Failed] No " + toname + " found!"
        else:
            message = "To " + toname + ": " + message
        sender.write(message.encode())
        sender.flush()

    def broadcastMessage(self, message, client="everyone"):
        for c in self.clients:
            if self.clients[c] != client:
                self.clients[c].write(message.encode())
                self.clients[c].flush()
            
        # Show the message in chat history
        if client != "everyone":
            self.chatHistory.append("[System] " + message)
        else:
            self.chatHistory.append(message)

    def updateClientList(self):
        # Update the client list to every client
        for c in self.clients:
            client_list = "client_update!" + "::".join(self.clients.keys())
            self.clients[c].write(client_list.encode())
            self.clients[c].flush()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = Server()
    server.show()
    sys.exit(app.exec_())