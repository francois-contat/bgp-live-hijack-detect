#!/usr/bin/env python3
"""
    1.0
        This script intends to subscribe to ris live stream on all ris instances.
        You must give an AS number or a list of AS numbers you want to follow.
        When launched, it searches for prefixes the watched ASes announced and follow
        them. Therefore, if another AS announces the said prefix, an alert is raised on
        the standard output

"""
import sys
import threading
import json
import argparse
import radix
import websocket

def print_prefixes():
    '''
        Debugging function
    '''
    print("ok")
    t = threading.Timer(5.0, print_prefixes)
    t.start() 
    if TREE:
        print(TREE.prefixes())

def argument_parse():
    '''
    This function handles the option and arguments given to the program
    '''
    parser = argparse.ArgumentParser(description='Watch AS(es) prefix hijacks')
    parser.add_argument('--asn', type=int, help='AS number to follow')
    parser.add_argument('--asfile',
                        type=str, help='file containing ASes numbers to follow')
    args = parser.parse_args()
    if not args.asn and not args.asfile:
        print("You must give an as or an asfile to the program", file=sys.stdout)
        sys.exit(1)
    return args

def stream_setup():
    '''
    Function that sets up the websocket stream with the RIS live service
    '''
    web_socket = websocket.WebSocket()
    web_socket.connect("wss://ris-live.ripe.net/v1/ws/?client=fco-stream.py")
    params = {
        "moreSpecific": True,
        "host": None,
        "socketOptions": {
            "includeRaw": False #was True
        }
    }
    web_socket.send(json.dumps({
        "type": "ris_subscribe",
        "data": params
    }))
    return web_socket
if __name__ == "__main__":
    ARGS = argument_parse()
    TREE = radix.Radix()
    t = threading.Timer(10.0, print_prefixes)
    t.start()
    WEB_SOCKET = stream_setup()
    for data in WEB_SOCKET:
        parsed = json.loads(data)
        if "announcements" in parsed["data"]:
            if ARGS.asn == parsed["data"]["path"][-1]:
                for groups in parsed["data"]["announcements"]:
                    for prefix in groups['prefixes']:
                        TREE.add(prefix)
