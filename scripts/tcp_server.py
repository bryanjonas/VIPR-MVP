import socket 
import sys
import argparse
import select
import time

def build_srv(ip_addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip_addr, port))
    sock.listen(1)

    return sock

def main(args): 

    ip_addr = socket.gethostbyname(args.host)
    sock = build_srv(ip_addr, args.port)
    payload_list = []
    with open(args.file, 'rb') as f:
        for line in f.readlines():
            payload_list.append(line)

    print('Payload: ', payload_list)

    inputs = [ sock ]
    outputs = []
    
    while True:
        readable, writeable, exceptional = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is sock:
                connection, client_address = s.accept()
                print('Connection from ', client_address)
                time.sleep(10)
                for line in payload_list:
                    connection.sendall(line)
                    print('Sent: ', line)
                connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--host", help="host to bind socket to", default='0.0.0.0')
    parser.add_argument("-p", "--port", help="port to bind socket to", type=int)
    parser.add_argument("-f", "--file", help="File containing newline-deliminated payloads", required=True)
    try:
        args = parser.parse_args()
    except:
        sys.exit(2)
    main(args)