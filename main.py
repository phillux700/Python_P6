##########################################################
# TITLE       : 3-2-1 Backup Rule
# DESCRIPTION :
    # - Sauvegarde wordpress/sql en local
    # - Sauvegarde wordpress/sql sur site distant
    # - Sauvegarde wordpress/sql sur AWS
    # - Restauration wordpress/sql depuis local
    # - Restauration wordpress/sql depuis site distant
    # - Restauration wordpress/sql AWS
# AUTHORS     : PHILIPPE TRAON
# DATE        : 31/08/2021
# REPO        : https://github.com/sergisergio/P6
##########################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import pysftp
import paramiko
import boto3
import botocore
import tqdm
import re
import shutil
import tarfile

"""############### DOCUMENTATION ####################
https://docs.python.org/fr/3/library/os.html
https://docs.python.org/fr/3/library/sys.html
https://docs.python.org/fr/3/library/datetime.html
https://docs.python.org/fr/3/library/time.html
https://docs.python.org/fr/3/library/shutil.html
https://docs.python.org/fr/3/library/tarfile.html
https://pypi.org/project/pysftp/
http://docs.paramiko.org/en/stable/api/client.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
https://botocore.amazonaws.com/v1/documentation/api/latest/index.html
https://github.com/tqdm/tqdm
https://www.python.org/dev/peps/pep-0020/
https://www.python.org/dev/peps/pep-0008/
https://www.python.org/dev/peps/pep-0257/
"""

# --- Variables --- #
# date = datetime.datetime.now().strftime('%Y%m%d-%s')
# f_date = datetime.datetime.now().strftime('%Y%m%d')
backup_path = '/home/philippe/P6/backup/'
source_directory = '/var/www/wordpress'
todays_date = (time.strftime("%Y%m%d_%HH%M"))
free_space_needed = 1000000
backup_site_name = 'wordpress'
database_name = 'wordpress_db'
target_dir = '/home/philippe/P6/backup/'
username = 'philippe'
password = 'password'

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

archive = todays_date + "_" + backup_site_name + ".tar "
zip_archive = todays_date + "_" + backup_site_name + ".tar.gz"
archive_db = todays_date + database_name + ".sql"
archive_db_path = target_dir + todays_date + database_name + ".sql"
rotation_time = '1'        # 1 week = 10080, 1 day = 1440

def banner():
    """
        Fonction permettant de définir une bannière pour le menu
    """
    banner = """\033[92m
 |__ /__|_  )__/ | | _ ) __ _ __| |___  _ _ __  | _ \_  _| |___ 
  |_ \___/ /___| | | _ \/ _` / _| / / || | '_ \ |   / || | / -_)
 |___/  /___|  |_| |___/\__,_\__|_\_\\_,_| .__/ |_|_\\_,_|_\___|
                                         |_|                    
 \033[0m"""
    return 

def rotate():
    """
        Fonction permettant la rotation des fichiers sur le serveur local
    """
    os.system("find /home/philippe/P6/backup/. -type f -mmin +" + rotation_time + " -delete")
    print('Backup rotation successful ...')

def local_backup():
    """
        Fonction permettant de faire une sauvegarde sur le serveur local
    """
    try:
        size = os.statvfs(target_dir)
        free_space = (size.f_bavail * size.f_frsize) / 1024
        if free_space > free_space_needed:
            os.system("tar -cvf " + archive + "/var/www/wordpress/*" + " --transform " + 's,^var/www/wordpress,' + todays_date + backup_site_name + ',' + " /var/www/wordpress")
            os.system("mysqldump -u " + username + " -p" + password + " " + database_name + "  > " + archive_db)
            os.system("tar -rf " + archive + archive_db + " && " + "rm " + archive_db + " && " + "gzip -9 " + archive)
            os.system("mv " + zip_archive + " " + target_dir)
            print('Local backup successful ...')
        else:
            print('Not enough space !')
    except:
        print('An error occured !')

def del_backup(zip_archive):
    os.system("rm /home/philippe/P6/backup/" + zip_archive)

def remote_backup_only():
    """
        Fonction permettant de faire une sauvegarde sur le serveur distant

        Documentation:
        https://blog.ruanbekker.com/blog/2018/04/23/using-paramiko-module-in-python-to-execute-remote-bash-commands/
    """
    try:
        local_backup()
        transport = paramiko.Transport(("192.168.2.2", 22))
        transport.connect(username = username, password =password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Connection succesfully established ... ")
        path = "/home/philippe/P6/backup/"
        sftp.put("/home/philippe/P6/backup/" + zip_archive, path + zip_archive)
        sftp.close()
        transport.close()
        print('Remote backup successful ...')

    except paramiko.AuthenticationException:
        print('Failed')
        print(': Sftp Authentication Failure.')

    except PermissionError:
        print('Failed')
        print(': Permission Denied Error From Server.')
    except:
        print('An error occured !')

def rotate_remote():
    """
        Fonction permettant de faire une sauvegarde sur le serveur distant
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='192.168.2.2', username=username, password=password)
    ssh.exec_command("find /home/philippe/P6/backup/. -type f -mmin +5 -delete")
    print('Remote backup rotation successful ...')
    ssh.close()

def aws_backup():
    """
        Fonction permettant de faire une sauvegarde dans un bucket S3 AWS

        Documentation:
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        https://adamtheautomator.com/boto3-s3/

        NB: Une configuration de cycle de vie a directement été créée dans le bucket pour supprimer les objets après 7 jours.
    """
    local_backup()
    # Create an S3 Client
    s3_client = boto3.client(
        's3',
        aws_access_key_id="AKIA45Z5NIQTRLHR3RBA",
        aws_secret_access_key="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"
    )
    # Upload object
    try:
        # Creating a bucket
        s3_client.create_bucket(Bucket='p6-eu-west-1-bucket')
        print("Bucket created succesfully")
        print('Uploading object ...')
        """
            Upload a file to S3 with a progress bar.

            From https://alexwlchan.net/2021/04/s3-progress-bars/
        """
        file_size = os.stat("/home/philippe/P6/backup/" + zip_archive).st_size
        with tqdm.tqdm(total=file_size, unit="B", unit_scale=True, desc=zip_archive) as pbar:
            s3_client.upload_file(
                "/home/philippe/P6/backup/" + zip_archive,
                'p6-eu-west-1-bucket',
                zip_archive,
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
            )
        print('Uploaded')

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "NoSuchBucket":
            print("Error: Bucket does not exist!!")
        elif e.response['Error']['Code'] == "InvalidBucketName":
            print("Error: Invalid Bucket name!!")
        elif e.response['Error']['Code'] == "AllAccessDisabled":
            print("Error: You do not have access to the Bucket!!")
        else:
            raise

    return

def restore_from_local():
    """
        Fonction permettant de faire une restauration depuis le serveur local
    """
    restore_local = print("restore local")
    return restore_local
    #### TODO Afficher liste des fichiers avec une boucle et saisir le choix (exemple: choix = input('Saisissez le choix')

def restore_from_remote():
    """
        Fonction permettant de faire une restauration depuis le serveur distant
    """
    restore_remote = print("restore remote")
    return restore_remote
    #### TODO Afficher liste des fichiers avec une boucle et saisir le choix (exemple: choix = input('Saisissez le choix')

def restore_from_aws():
    """
        Fonction permettant de faire une restauration depuis le bucket S3 AWS
    """
    restore_aws = print("restore aws")
    return restore_aws
    #### TODO Afficher liste des fichiers avec une boucle et saisir le choix (exemple: choix = input('Saisissez le choix')


# Affichage du menu
def menu():
    print (banner() + """\033[96m
 [*] Manage your backup [*]
   [1]--Local ONLY (first rule)
   [2]--Remote ONLY (second rule)
   [3]--AWS S3 Bucket ONLY (third rule)
   [4]--3 RULES
   [5]--Restore from Local
   [6]--Restore from Distant
   [7]--Restore from AWS
   [0]--Exit
   \033[0m
 """)

def show_info(info):
    print('\033[31m' + info + '\033[31m')

def show_input():
    return "{0}P6~# {1}".format('\033[31m', '\033[0m')

def menu():
    choice = input(show_input())

    if choice == "1":
        local_backup()
        rotate()
    elif choice == "2":
        remote_backup_only()
        rotate_remote()
        del_backup(zip_archive)
    elif choice == "3":
        aws_backup()
        del_backup(zip_archive)
    elif choice == "4":
        restore_from_local()
    elif choice == "5":
        restore_from_remote()
    elif choice == "6":
        restore_from_aws()
    elif choice == "0":
        os.system('clear'), sys.exit()
    elif choice == "":
        menu()
    elif not int(choice) in range(0, 9):
        menu()
        show_info("Choix indisponible !")
        sys.exit()