import sys
import socket
from datetime import datetime

ECHO_ARGS = [('-u', '--upper'),
             ('-l', '--lower'),
             ('-e', '--eval')]

TIME_ARGS = [('-l', '--local'),
             ('-u', '--utc')]


class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = None
        self.client_id = None
        self.last_file = None

    def run(self):
        with socket.socket(type=socket.SOCK_STREAM) as server:
            server.bind((self.address, self.port))
            server.listen(0)
            server.settimeout(10)

            while True:
                self.socket, address = server.accept()
                print('{} connected to server'.format(address))
                self.handle_connection()
                print('{} disconnected from server'.format(address))

    def handle_connection(self):
        while True:
            data_bytes = self.recv()
            if not data_bytes:
                break

            data_bytes = data_bytes[:-1]
            data = data_bytes.decode('utf-8').split(' ', 1)
            command = data[0]
            load = data[1] if len(data) > 1 else None
            print(data)
            if command == 'echo':
                key, data = self.check_key(load, ECHO_ARGS)
                self.echo(key, data)
            elif command == 'time':
                key, _ = self.check_key(load, TIME_ARGS)
                self.time(key)
            elif command == 'upload':
                pass
            elif command == 'download':
                self.download(load)
            elif command == 'close':
                self.socket.close()
                break
            else:
                self.send(b'Error: unknown command.')

    def send(self, data):
        self.socket.sendall(data)
        self.socket.send(b'\n')

    def recv(self):
        data_bytes = self.socket.recv(1024)
        while data_bytes and chr(data_bytes[-1]) != '\n':
            data_bytes += self.socket.recv(1024)
        return data_bytes

    def echo(self, key, data):
        if not data:
            self.send(b'Error: no data were sent.')
            return

        if key == '--upper':
            result = data.upper()
        elif key == '--lower':
            result = data.lower()
        elif key == '--eval':
            result = str(eval(data))
        else:
            result = data

        self.send(result.encode('utf-8'))

    def time(self, key):
        if key == '--utc':
            clock = datetime.utcnow()
        else:
            clock = datetime.now()

        self.send(clock.strftime("%Y-%m-%d %H:%M:%S").encode('utf-8'))

    def download(self, data):
        if not data:
            self.send(b'Error: no file name was sent.')
        filename = data.split(' ')[0]

        try:
            with open(filename, 'rb') as file:
                self.socket.sendall(b'1')
                bytes_array = file.read(1024)
                while bytes_array:
                    self.socket.sendall(bytes_array)
                    bytes_array = file.read(1024)
                self.socket.send(b'\n')
        except FileNotFoundError:
            self.send(b'Error: file with this name does not exist.')

    @staticmethod
    def check_key(data, args_types):
        if not data:
            return None, None

        if '-' not in data[0]:
            return None, data

        arr = data.split(' ', 1)
        key = None

        for short, full in args_types:
            if arr[0] == short or arr[0] == full:
                key = full

        return key, arr[1] if len(arr) > 1 else None


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print('No arguments were detected. Pass -h or --help to get info about them.')
        return

    if args[0] == '-h' or args[0] == '--help':
        print('Pass as arguments server\'s IPv4 address and port.\n'
              'Example: server 127.0.0.1 8080')
        return

    try:
        address = args[0]
        port = int(args[1])
        server = Server(address, port)
        server.run()
    except socket.gaierror:
        print('Error: initialization failed. Check address.')
    except ValueError:
        print('Error: port value is incorrect.')
    except socket.timeout:
        print('Timeout: server was shut down because of no clients.')


if __name__ == '__main__':
    main()
