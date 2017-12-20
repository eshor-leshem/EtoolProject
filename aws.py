import argparse
import utils


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help="The aws access id", type=str)
    parser.add_argument('--key', help="The aws access key", type=str)
    parser.add_argument('--tag', help = "The tag name for your system (e.g. staging-innovi)", type=str)
    parser.add_argument('--region', help="The aws region (default: eu-west-1)", type=str, default="eu-west-1")
    args = parser.parse_args()
    if not args.id or not args.key:
        raise Exception("Please specify aws id and key")
    return args


def main():
    args = arg_parser()
    new_inst = utils.Aws(args.id, args.key, args.region, args.tag)
    current_instances = new_inst.running_instances()
    print('\n'.join([str(inst) for inst in sorted(current_instances)]),sep='/n')


if __name__ == '__main__':
    main()

