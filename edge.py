#! /usr/bin/python

"""
This module let you send remote requests to an Edge device.
"""

__author__ = "Elad Shor Leshem"

import argparse
import utils


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help="The Edge ip address", type=str)
    parser.add_argument('-c', help="The command to execute on the Edge device", type=str)
    args = parser.parse_args()
    if not args.i:
        raise Exception("Please specify edge ip(--ip x.x.x.x)")
    elif not args.c:
        raise Exception("Please specify command")
    return args.i, args.c


def main():
    print("Welcome to edge tool!")
    edge_ip_address, edge_command = arg_parser()
    try:
        edge_instance = utils.Ssh(edge_ip_address, 'agent', 'EdgeDevice200%')
        edge_instance.cleaner(edge_ip_address)
        edge_command_output = edge_instance.execute(edge_command)
    finally:
        edge_instance.terminate_connection()
    parsing = utils.Parser(edge_command_output)
    parsing.parse_output()


if __name__ == '__main__':
    main()



