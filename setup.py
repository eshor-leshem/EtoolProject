#! /usr/bin/python3

"""
Installing python packages on client environment to use Etool
"""
import pip


def install(package):
    pip.main(['install', package])


if __name__ == '__main__':
    print("Starting setup for Etool")
    packages = ['boto3', 'requests', 'paramiko', 'sshtunnel', 'flask']
    for package in packages:
        print("Installing {}".format(package))
        install('{}'.format(package))
