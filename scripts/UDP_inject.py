from scapy.all import *
import sockets

def main(args):  
    srcip = sockets.gethostbyname(args.srchn)
    dstip = sockets.gethostbyname(args.dsthn)

    for line in args.contents:
        packet = IP(src=srcip, dst=dstip)/UDP(sport=args.sport, dport=args.dport)/Raw(line)
        send(packet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--srchn", help="Source hostname")
    parser.add_argument("--dsthn", help="Destination hostname")
    parser.add_argument("--sport", help="Source port", type="int")
    parser.add_argument("--dport", help="Destination port", type="int")
    parser.add_argument("--contents", help="List of packet payloads")
    try:
        args = parser.parse_args()
    except:
        sys.exit(2)
    main(args)