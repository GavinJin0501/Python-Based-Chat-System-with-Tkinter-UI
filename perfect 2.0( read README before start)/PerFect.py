#!/usr/bin/env python3
# -*- coding: utf-8 -*-import sys
import os
import sys

from chat_client_class import *
import chat_server
os.chdir(sys.path[0])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()

    client = Client(args)
    client.run_chat()

try:
    chat_server.main()
finally:
    main()
