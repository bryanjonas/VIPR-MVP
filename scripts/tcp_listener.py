import socket 
import sys
import argparse
import select
import time
import os

def build_srv(ip_addr, port):
    addr_info = socket.getaddrinfo(ip_addr, port, type=socket.SOCK_STREAM)
    (sock_fam, _, _, _, bind_args) = addr_info[0]

    sock = socket.socket(sock_fam, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(bind_args)
    sock.listen(1)

    return sock

def main(args):  
    project_path = args.project_path
    ip_addr = socket.gethostbyname(args.host)

    sock = build_srv(ip_addr, args.port)
    
    inputs = [ sock ]
    outputs = []
    
    while True:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is sock:
                connection, client_address = s.accept()
                while True:
                    data = connection.recv(1049)
                    #if len(data) == 0: 
                    #    break
                    file_path = os.path.join(project_path, 'vipr/outputs/', 'vipr-' + str(time.time()))
                    open(file_path, 'wb').write(data)
                    print('Wrote CoT file at: ', file_path)
                #connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--host", help="host to bind socket to", default='0.0.0.0')
    parser.add_argument("-p", "--port", help="port to bind socket to", type=int)
    parser.add_argument("-f", "--project_path", help="path for system project")
    try:
        args = parser.parse_args()
    except:
        sys.exit(2)
    main(args)