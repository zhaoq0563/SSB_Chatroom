import socket
import threading

SERVER_IP = '192.168.0.108'  # Replace with the IP address of the server
SERVER_PORT = 8888  # Replace with the port number of the server

def receive_messages(sock):
    """Thread target function to continuously receive messages from the server."""
    while True:
        try:
            message = sock.recv(1024).decode()
            print("[Message received] " + message)
        except (socket.error, KeyboardInterrupt):
            break

def main():
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        name = input('Enter your name (or type \'quit\' to exit): ')
        client_socket.connect((SERVER_IP, SERVER_PORT))
        client_socket.sendall(("Name: " + name).encode())
        print('Connected to the chat room.')

        # Create and start the receive thread
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        # Start sending messages
        while True:
            message = input('Enter your message (or type \'quit\' to exit): ')
            if message.lower() == 'quit':
                break

            # Send the message to the server
            client_socket.sendall((name + ': ' + message).encode())

        # Close the connection
        client_socket.close()
        print('Disconnected from the chat room.')

    except ConnectionRefusedError:
        print('Unable to connect to the server.')

if __name__ == '__main__':
    main()