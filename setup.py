#! /usr/bin/python3

"""
Installing python packages on client environment to use Etool
"""
import pip


def install(package):
    pip.main(['install', package])


if __name__ == '__main__':
    print("Stating setup for Etool")
    install('boto3')
    install('requests')