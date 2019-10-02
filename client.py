import socket
import sys


# def send(sock, data):
#     sock.sendall(data)
#     sock.send(b'\n')
#
#
# def recv(sock):
#     data_bytes = sock.recv(1024)
#     while data_bytes and chr(data_bytes[-1]) != '\n':
#         data_bytes += sock.recv(1024)
#     return data_bytes[:-1]


# def download_file(sock):
#     try:
#         sock.settimeout(5)
#         data_bytes = None
#         downloading = True
#
#         while downloading:
#             try:
#                 data_bytes = sock.recv(1024) if not data_bytes else data_bytes
#                 while data_bytes and chr(data_bytes[-1]) != '\n':
#                     data_bytes += sock.recv(1024)
#                 data_bytes = data_bytes[:-1]
#                 downloading = False
#             except Exception:
#                 print('Warning: connection issues. Trying to reconnect...')
#                 sock.settimeout(20)
#                 sock.connect((ADDRESS, PORT))
#
#         sock.settimeout(None)
#         return data_bytes
#     except Exception:
#         print('Error: connection lost')


# def download(sock, params):
#     params = params.split(' ', 2)
#     if len(params) == 1:
#         return
#
#     data_bytes = recv(sock)
#     if data_bytes[0] != b'1'[0]:
#         print(data_bytes.decode('utf-8'))
#         return
#
#     filename = params[1]
#     with open(filename, 'wb') as file:
#         file.write(data_bytes[1:])


# def connect(address, port):
#     with socket.socket(type=socket.SOCK_STREAM) as client:
#         client.connect((address, port))
#         print('Connection is established. Write help to get info about available commands.')
#         while True:
#             print('> ', end='')
#
#             command = input()
#             if command == '':
#                 continue
#             send(client, command.encode('utf-8'))
#
#             if command[:8] == 'download':
#                 download(client, command)
#                 continue
#
#             data = recv(client)
#             if not data:
#                 print('Session has been finished.')
#                 break
#             print(data.decode('utf-8'))


class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = None

    def connect(self):
        with socket.socket(type=socket.SOCK_STREAM) as sock:
            self.socket = sock
            self.socket.connect((self.address, self.port))
            print('Connection is established. Write help to get info about available commands.')
            while True:
                print('> ', end='')

                command = input()
                if command == '':
                    continue
                elif command[:8] == 'download':
                    self.download(command)
                    continue
                else:
                    self.send(command.encode('utf-8'))
                    data = self.recv()
                    if not data:
                        print('Session has been finished.')
                        break
                    print(data.decode('utf-8'))


    def send(self, data):
        self.socket.sendall(data)
        self.socket.send(b'\n')

    def recv(self):
        data_bytes = self.socket.recv(1024)
        while data_bytes and chr(data_bytes[-1]) != '\n':
            data_bytes += self.socket.recv(1024)
        return data_bytes[:-1]

    def download_file(self):
        try:
            self.socket.settimeout(5)
            data_bytes = None
            downloading = True

            while downloading:
                try:
                    data_bytes = self.socket.recv(1024) if not data_bytes else data_bytes
                    while data_bytes and chr(data_bytes[-1]) != '\n':
                        data_bytes += self.socket.recv(1024)
                    data_bytes = data_bytes[:-1]
                    downloading = False
                except Exception:
                    print('Warning: connection issues. Trying to reconnect...')
                    self.socket.settimeout(20)
                    self.socket.connect((self.address, self.port))

            self.socket.settimeout(None)
            return data_bytes
        except Exception:
            print('Error: connection lost')
            return None

    def download(self, params):
        params = params.split(' ', 2)
        if len(params) == 1:
            return

        filename = params[1]
        with open(filename, 'wb') as file:

            data_bytes = recv(sock)
            if data_bytes[0] != b'1'[0]:
                print(data_bytes.decode('utf-8'))
                return

            file.write(data_bytes[1:])


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print('No arguments were detected. Pass -h or --help to get info about them.')
        # args.append('192.168.1.21')
        # args.append(9090)
        return

    if args[0] == '-h' or args[0] == '--help':
        print('Pass as arguments server\'s IPv4 address and port.\n'
              'Example: client 127.0.0.1 8080')
        return

    try:
        address = args[0]
        port = int(args[1])
        client = Client(address, port)
        client.connect()
    except socket.gaierror:
        print('Error: connection failed. Check server address.')
    except ValueError:
        print('Error: port value is incorrect.')
    except TimeoutError:
        print('Error: connection timed out.')
    except ConnectionError:
        print('Error: connection lost.')
    except KeyboardInterrupt:
        print('\nSession has been finished.')


if __name__ == '__main__':
    main()