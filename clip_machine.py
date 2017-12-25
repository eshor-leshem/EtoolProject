#! /usr/bin/python3

import argparse
import utils
import sys


def arg_parser():
    parser = argparse.ArgumentParser(
        description='EC2 tool',
        usage='e.g. ec2.py access_keyID secret_accessKEY --tag staging-innovi'
    )
    parser.add_argument('id', help="The aws access id", type=str)
    parser.add_argument('key', help="The aws access key", type=str)
    parser.add_argument('--name', help = "Your name to load customize env configuration (elad/efrat/anna) ", type=str,
                        required=True)
    parser.add_argument('--builds', help="The desired build names (for e.g build-dev-3695, build-rc-1.2.1-3664)",
                        nargs='+', type=str, required=True)
    parser.add_argument('--region', help="The aws region (default: us-west-2)", type=str, default="us-west-2")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit("\nPlease see Usage")
    return parser.parse_args()


def main():
    args = arg_parser()
    new_inst = utils.Clip(args.id, args.key, args.region, args.name, args.builds)
    new_inst.create_clip_encoder()
    # current_instances = new_inst.running_instances()
    # print('\n'.join([str(inst) for inst in sorted(current_instances)]),sep='/n')


if __name__ == '__main__':
    main()