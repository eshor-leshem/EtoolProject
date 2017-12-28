#! /usr/bin/python3

import argparse
import utils
import sys
import time


def arg_parser():
    parser = argparse.ArgumentParser(
        description='EC2 tool',
        usage='e.g. ec2.py access_keyID secret_accessKEY --tag staging-innovi'
    )
    parser.add_argument('id', help="The aws access id", type=str)
    parser.add_argument('key', help="The aws access key", type=str)
    parser.add_argument('--name', help="Your name to load customize env configuration (elad/efrat/anna) ",
                        choices=['elad', 'efrat', 'anna'], type=str, required=True)
    parser.add_argument('--builds', help="The desired build names (for e.g build-dev-3695, build-rc-1.2.1-3664)",
                        nargs='+', type=str, required=True)
    parser.add_argument('--amount', help="How many clips to create for each build", type=int, default=10)
    parser.add_argument('--keep', help="Do not delete current machine clip", action='store_true', default=False)
    parser.add_argument('--region', help="The aws region (default: us-west-2)", type=str, default="us-west-2")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit("\nPlease see Usage")
    return parser.parse_args()


def main():
    args = arg_parser()
    new_request = utils.EncoderClip(args.id, args.key, args.region, args.name, args.builds)
    if not args.keep:
        exists_machine = new_request.current_running_instances('Etool_Encoder_{}'.format(args.name))
        if exists_machine:
            new_request.terminate_instances(exists_machine)
    new_instance_id = new_request.create_clip_encoder()
    new_request.is_instance_status_ok(new_instance_id)
    new_instance_ip = new_request.instance_id_to_ip(new_instance_id)

    retries = 10
    while retries != 0:
        try:
            start_clips = utils.Ssh(new_instance_ip, 'ubuntu')
        except Exception as err:
            print("SSH to Encoder machine ({}) failed:{}\nRetrying...".format(new_instance_ip, err))
            retries -= 1
            time.sleep(10)
        else:
            break

    index = 0
    for build in args.builds:
        for clip in range(args.amount):
            start_clips.execute('./etool_testLoopDocker.sh {} {} {} {}'.format(args.name, index, index, build))
            index += 1


if __name__ == '__main__':
    main()
