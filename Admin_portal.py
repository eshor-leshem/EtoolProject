import argparse
import utils
import sys


def status_code_cheacker(response):
    if response == 200:
        print("Done")
    else:
        print("Last operation failed... --> {}".format(response))


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Adding rules to camera',
        usage='e.g. Admin_portal.py https://aws-stag-admin-portal-111462923.eu-west-1.elb.amazonaws.com -a 2 -f 3'
    )
    parser.add_argument('host', help='The env admin-portal address')
    parser.add_argument('-u', help='The Admin portal Username. Default is adminrd@agentvi.com',
                        default='adminrd@agentvi.com')
    parser.add_argument('-p', help='The Admin portal Password. Default is 12345678', default=12345678)
    parser.add_argument('-a', help='Account id. if not exist, will create one')
    parser.add_argument('-f', help='Folder id. if not exist, will create one')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit("\nPlease see Usage")
    return parser.parse_args()


def main():
    args = arg_parser()
    new_session = utils.AP(args.host, args.u, args.p)
    print(new_session.list_current_accounts())
    print(new_session.list_current_videos())
    # utils.AP.status_code_cheacker(new_session.create_account())


if __name__ == '__main__':
    main()
