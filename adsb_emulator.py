import socket

A2198_msg = [
    b'*8DA06646990C3831907C106D4F7F;', 
    b'*8DA06646EA2D0884013C08A2463B;', 
    b'*8DA0664623041332C79E20386508;', 
    b'*8DA066465853641200D015B4433A;', 
    b'*8DA06646585340689A44EB8806AC;', 
    b'*8DA0664658535068C244E87E5C14;', 
    b'*8DA06646F83300060049B8C94897;'
    ]


def build_srv(ip_addr, port):
    addr_info = socket.getaddrinfo(ip_addr, port, type=socket.SOCK_STREAM)
    (sock_fam, _, _, _, bind_args) = addr_info[0]

    sock = socket.socket(sock_fam, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(bind_args)
    sock.listen(1)

    return sock

class ADSBServer():
    def __init__(self):
        self.srv = None

    def sock_setup(self):
        ip = '0.0.0.0'
        port = '30002'

        self.srv = build_srv(ip, port)

    @property
    def is_closed(self):
        return self.srv.fileno() == -1
        
    def list_tx(self, list, conn):
        assert len(list) > 0; 'TX list must contain elements'        
        for msg in list:
            conn.sendall(msg)


def main():
    server = ADSBServer()
    server.sock_setup()
    msg_list = []

    with open('/vipr/adsb.txt', 'rb') as f:
        for line in f:
            msg_list.append(line)

    while True:
        connection, client_address = server.srv.accept()
        print('Connection to emulator!')
        try:
            server.list_tx(msg_list, connection)
            print('Sent ADS-B messages!')
            exit()
        except Exception as exc:
            print('Exception! ', exc)
            exit()

if __name__ == "__main__":
    main()


    
