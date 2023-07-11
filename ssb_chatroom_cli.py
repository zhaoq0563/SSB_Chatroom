import sys, re
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor

class Client(QDialog):
    def __init__(self, parent=None):
        super(Client, self).__init__(parent)
        self.resize(500,500)
        self.setStyleSheet("font-size: 25px")
        
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.readyRead.connect(self.receiveMessage)
        
        self.name, ok = QInputDialog.getText(self, "Client Name", "Enter your name:")
        if ok:
            self.tcpSocket.connectToHost('192.168.0.108', 8888)
            self.tcpSocket.waitForConnected()
            self.tcpSocket.write(("Name: " + self.name).encode())
            self.tcpSocket.flush()

        self.client_label = QLabel("Client list")
        self.clientList = QListWidget()
        self.chat_label = QLabel("Chat history")
        self.chatHistory = QTextEdit()
        self.chatHistory.setReadOnly(True)
        self.messageInput = QLineEdit()
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMessage)

        layout = QVBoxLayout()
        layout.addWidget(self.client_label)
        layout.addWidget(self.clientList)
        layout.addWidget(self.chat_label)
        layout.addWidget(self.chatHistory)
        layout.addWidget(self.messageInput)
        layout.addWidget(self.sendButton)
        self.setLayout(layout)
        self.setWindowTitle("SSB Chat Room - User " + self.name)

    def sendMessage(self):
        message = self.messageInput.text()
        # if re.match(r'>>[a-zA-Z]{1,9} .*', message):
            # index = message.find(" ")
            # message = message[:index+1] + self.name + ": " + message[index+1:]
        # else:
        message = self.name + ": " + message
        self.tcpSocket.write(message.encode())
        self.tcpSocket.flush()
        self.messageInput.clear()

    def receiveMessage(self):
        message = self.tcpSocket.readAll().data().decode()
        if message.startswith("client_update!"):
            self.clientList.clear()
            client_list = message[14:].split("::")
            item = QListWidgetItem(self.name)
            text_color = QColor(255, 0, 0)  # Red color
            item.setForeground(text_color)
            self.clientList.addItem(item)
            for c in client_list:
                if c != self.name:
                    item = QListWidgetItem(c)
                    self.clientList.addItem(item)
        else:
            self.chatHistory.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())