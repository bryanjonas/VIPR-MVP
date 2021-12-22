import select
import sys
import socket
import time
import os

class Client():
    def __init__(self, sock, out_folder):
        self.sock = sock
        self.out_buff = b""
        self.out_folder = out_folder

    @property
    def is_closed(self):
        return self.sock.fileno() == -1

    @property
    def has_data(self):
        return len(self.out_buff) > 0

    def feed(self, data):
        ts = str(time.time())
        file_path = os.path.join(self.out_folder, ts + '.xml')
        print('Write CoT file!')
        with open(file_path, 'w') as f:
            f.write(data.decode('utf-8'))

    def socket_rx(self):
        try:
            data = self.sock.recv(4096)

            if len(data) == 0:
                self.disconnect("Client disconnected")
                return

            self.feed(data)

        except Exception as exc:
            self.disconnect(str(exc))

    def disconnect(self, reason=None):
        if not self.is_closed:
            print("Socket disconnect: ", reason)

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:  
            pass
        finally:
            self.sock.close()

def build_srv(ip_addr, port):
    addr_info = socket.getaddrinfo(ip_addr, port, type=socket.SOCK_STREAM)
    (sock_fam, _, _, _, bind_args) = addr_info[0]

    sock = socket.socket(sock_fam, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(bind_args)
    sock.listen()

    return sock

class COTServer:
    def __init__(self):
        self.clients = {}
        self.srv = None

    def sock_setup(self):
        ip_addr = "0.0.0.0"
        port = "8087"

        self.srv = build_srv(ip_addr, port)

    def srv_accept(self, sock):
        ip_addr = None
        port = None

        try:
            (sock, addr) = sock.accept()
            (ip_addr, port) = addr[0:2]
            stype = "tcp"
        except (socket.error, OSError) as exc:
            print("Client connect failed: ", ip_addr, port, exc)
            return

        print("New client from: ", stype, ip_addr, port)
        self.clients[sock] = Client(
            sock=sock,
            out_folder = '/vipr/CoT-out'
        )

    def client_disconnect(self, client, reason=None):
        client.disconnect(reason)
        client = self.clients.pop(client.sock)

    def loop(self):
        rd_clients = list(self.clients)
        rd_clients.append(self.srv)
        wr_clients = []
        (s_rd, s_wr, s_ex) = select.select(rd_clients, wr_clients, rd_clients, 1)
        
        # Process exception sockets
        for sock in s_ex:
            if sock in [self.srv, self.mgmt]:
                raise RuntimeError("Server socket exceptional condition")

            client = self.clients.get(sock)
            self.client_disconnect(client, "Exceptional condition")

        # Process sockets with incoming data
        for sock in s_rd:
            if sock is self.srv:
                self.srv_accept(sock)
            else:
                client = self.clients.get(sock)
                if not client.is_closed:
                    client.socket_rx()
        
        prune_sox = list(self.clients.items())
        for (sock, client) in prune_sox:
            if client.is_closed:
                self.client_disconnect(client, "Is closed")

    def shutdown(self):
        for client in list(self.clients.values()):
            self.client_disconnect(client, "Server shutting down")

        if self.srv:
            try:
                self.srv.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.srv.close()
            self.srv = None

def main():
    got_sigterm = False
    cot_srv = COTServer()
    try:
        cot_srv.sock_setup()
        print('CoT server started!')
    except Exception as exc: 
        print("Unable to start COTServer: ", exc)
        cot_srv.shutdown()
        sys.exit(1)

    try:
        print('Listening for CoT server connection!')
        while not got_sigterm:
            cot_srv.loop()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print("Unhandled exception: ", exc)
        ret = 1

    try:
        cot_srv.shutdown()
    except Exception as exc:
        print("Exception during shutdown: ", exc)
        ret = 1

    sys.exit(ret)

if __name__ == "__main__":
    main()