#! /usr/bin/python3

"""
Utils collection to help test and configure "Innovi" system ("Etool")
"""

__author__ = "Elad Shor Leshem"

import paramiko
import os
from sshtunnel import SSHTunnelForwarder
import boto3
import requests
import json


class Ssh:
    """
    Opens regular ssh connection and sending commands
    """

    def __init__(self, dest_host, dest_username, dest_password=None):
        self.dest_host = dest_host
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(dest_host, username=dest_username, password=dest_password)

    @staticmethod
    def cleaner(string_to_delete):
        """Deleting all output txt files (output*.txt)"""
        exist_logs = [file for file in (os.listdir(os.getcwd())) if string_to_delete in file]
        for file in exist_logs:
            print("Deleting {}".format(file))
            os.remove(file)

    def execute(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        errors = stderr.readline()
        if errors:
            print("Errors while executing the command:\n{}".format(errors))
        with open('output_{}_{}.txt'.format(self.dest_host, command), 'w') as file:  # Writing the output to a txt file
            for line in stdout.readlines():
                file.write(line)
        return 'output_{}_{}.txt'.format(self.dest_host, command)

    def terminate_connection(self):
        print("Terminating connection to {}".format(self.dest_host))
        self.ssh_client.close()


class TunnelSsh(Ssh):  # NEED IMPROVEMENTS!!!
    """
    Opening ssh connection via "middle man" machine - (for e.g. ops machine for aws-stag environment),
    to be able to connect all the other service machines (Application server, Admin portal and so on...)
    and execute a command on them (for e.g. docker ps -a) and saving the output in a txt file for future use..
    """

    def __init__(self, tunnel_host, dest_host, local_host_port, username):
        """Setting parameter needed for ssh tunneling"""
        self.tunnel = tunnel_host
        self.dest = dest_host
        self.username = username
        self.port = local_host_port

    def execute(self, command):
        """opening a tunnel to "dest_host" via "tunnel_host" and sending the desired command"""
        with SSHTunnelForwarder(
                (self.tunnel, 22),
                ssh_username=self.username,
                remote_bind_address=(self.dest, 22),
                local_bind_address=('0.0.0.0', self.port)
        )as open_tunnel:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('127.0.0.1', self.port, self.username)
            ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(command)
            errors = ssh_stderr.readline()
            if errors:
                print("Errors while executing the command:\n{}".format(errors))
            # if errors:  # If command returned a error, raise it and exit
            #     raise Exception("Error executing the command: {} --> {}".format(command, errors))
            with open('output_{}_{}.txt'.format(self.dest, command), 'w') as file:  # Writing the output to a txt file
                for line in ssh_stdout.readlines():
                    file.write(line)
            return 'output_{}_{}.txt'.format(self.dest, command)
            client.close()


class Aws:
    """
    Set of modules for aws EC2 and ECS
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, tag_name):
        self.instances = []
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.tag_name = tag_name.split(',')
        self.region_name = region_name
        self.connection = boto3.resource('ec2', aws_access_key_id=self.aws_access_key_id,
                                         aws_secret_access_key=self.aws_secret_access_key, region_name=self.region_name)

    def running_instances(self):
        instance_query = self.connection.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']},
                     {'Name': 'tag:Name', 'Values': self.tag_name}])
        for instance in instance_query:
            self.instances.append([instance.key_name, instance.id, instance.private_ip_address])
        return self.instances

        # print("AS:")
        # for instance in self.as_instances:
        #     print(instance,sep=" ")
        # print("CS:")
        # for instance in self.cs_instances:
        #     print(instance, sep=" ")


class AdminPortal:
    """
    Set of modules for Admin portal API
    """

    def __init__(self, host, email, password):
        self.host = host
        self.email = email
        self.password = password
        self.assigned_videos = []
        self.un_assigned_videos = []

        body = {'email': email, 'password': str(password)}
        header = {'content-type': 'application/json'}
        try:
            token = requests.post(host + '/api/v1/signin', headers=header, data=json.dumps(body), verify=False)
        except Exception as e:
            raise Exception(
                "Couldn't retrieve token, Please check the host name, email and password you provided."
                " This is the Error -->", e)
        self.token = token.json()['token']
        print(self.token)

    def list_current_accounts(self):  # Current accounts under Innovi
        current_accounts = []
        header = {'x-access-token': self.token}
        accounts = requests.get(self.host + '/api/v1/accounts', headers=header, verify=False).json()['accounts']
        for acc in range(len(accounts)):
            current_accounts.append([accounts[acc]['name'], accounts[acc]['id'], accounts[acc]['key']])
        print(current_accounts)
        return current_accounts

    def list_current_videos(self, account=None, folder=None):  # Current unassigned videos under Innovi
        header = {'x-access-token': self.token}
        if folder:
            current_videos = requests.get(
                self.host + '/api/v1/folder/{}/sensors'.format(str(folder)), headers=header, verify=False).json()[
                'sensors']
        elif account:
            current_videos = requests.get(
                self.host + '/api/v1/account/{}/sensors'.format(str(account)), headers=header, verify=False).json()[
                'sensors']
        else:
            current_videos = requests.get(
                self.host + '/api/v1/sensors/ids', headers=header, verify=False).json()['sensors']
        for sensor in range(len(current_videos)):
            if current_videos[sensor]['folderName'] == "Unassigned Cameras":
                self.un_assigned_videos.append(current_videos[sensor]['id'])
            self.assigned_videos.append(current_videos[sensor]['id'])
        print(self.assigned_videos, self.un_assigned_videos)
        return self.assigned_videos, self.un_assigned_videos

    def add_rule_moving_in_area(self):
        print("Creating rules")
        header = {'x-access-token': self.token, 'content-type': 'application/json'}
        body = {
            'ruleTypeId': 1, 'useEventEngine': 'true', 'isActive': 'true', 'scheduleId': 1,
            'ObjectClass': ["ObjectClass-Person", "ObjectClass-Vehicle", "ObjectClass-Bicycle", "ObjectClass-Motorcycle"],
            'MinMaxFilters': [{'Type': 2, 'Min': 0.35, 'Max': 100}],
            'FloatParameters': [{'Type': 0, 'Value': 1}, {'Type': 1, 'Value': 1}],
            'Zones': [{'Polygon': {'Points': [{'X': 0.018544935805991, 'Y': 0.020922491678554},
                                              {'X': 0.97860199714693, 'Y': 0.026628625772706},
                                              {'X': 0.98716119828816, 'Y': 0.96814075130766},
                                              {'X': 0.029957203994294, 'Y': 0.97574893009986}]}, 'Type': 0}]
        }
        for sensor in self.assigned_videos:
            print("Adding moving in area rule to {} sensor ".format(sensor))
            requests.post(
                self.host + '/api/v1/rules/{}'.format(sensor), headers=header, data=json.dumps(body), verify=False)

    def add_rule_crossing_a_line(self):
        print("Creating rules")
        header = {'x-access-token': self.token, 'content-type': 'application/json'}
        body = {
            'ruleTypeId': 2, 'useEventEngine': 'true', 'isActive': 'true', 'scheduleId': 1,
            'ObjectClass': ["ObjectClass-Person", "ObjectClass-Vehicle", "ObjectClass-Bicycle", "ObjectClass-Motorcycle"],
            'MinMaxFilters': [{'Type': 2, 'Min': 0.35, 'Max': 100}],
            'FloatParameters': [{'Type': 3, 'Value': 0.5}],
            'Lines': [{'Polygon': {'Points': [{'X': 0.15, 'Y': 0.5}, {'X': 0.85, 'Y': 0.5}]}, 'CrossDirection': 1}]

        }
        for sensor in self.assigned_videos:
            print("Adding crossing a line rule to {} sensor ".format(sensor))
            requests.post(
                self.host + '/api/v1/rules/{}'.format(sensor), headers=header, data=json.dumps(body), verify=False)

    def create_account(self):
        header = {'content-type': 'application/json', 'x-access-token': self.token}
        body = {'name': 'elad_fgbjjjjddddhhgfool', 'description': " d", 'type': 2}
        print("Creating new account: {}".format(body['name']))
        try:
            create_account = requests.post(
                self.host + '/api/v1/accounts', headers=header, data=json.dumps(body), verify=False)
        except Exception as e:
            raise Exception(
                "Couldn't create account,"
                " This is the Error -->", e)
        return create_account.status_code


class Parser:
    """
    Set of modules for parsing data
    """

    def __init__(self, file_name):
        self.file_name = file_name

    def parse_output(self):
        with open(self.file_name) as file:
            for line in file:
                print(line)
