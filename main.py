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
import shutil
import tarfile

############### DOCUMENTATION ####################
# https://docs.python.org/fr/3/library/os.html
# https://docs.python.org/fr/3/library/sys.html
# https://docs.python.org/fr/3/library/datetime.html
# https://docs.python.org/fr/3/library/time.html
# https://docs.python.org/fr/3/library/shutil.html
# https://docs.python.org/fr/3/library/tarfile.html
# https://pypi.org/project/pysftp/
##################################################

# --- Variables --- #
date = datetime.datetime.now().strftime('%Y%m%d-%s')
f_date = datetime.datetime.now().strftime('%Y%m%d')
backup_path = '/home/philippe/P6/backup/'
source_directory = '/var/www/wordpress'
todays_date = (time.strftime("%d-%m-%Y"))
free_space_needed = 1000000
backup_site_name = 'wordpress'
database_name = 'wordpress_db'
target_dir = '/home/philippe/P6/backup/'
username = 'philippe'
password = 'password'

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

archive = todays_date + backup_site_name + ".tar "
zip_archive = todays_date + backup_site_name + ".tar.gz"
archive_db = todays_date + database_name + ".sql"
archive_db_path = target_dir + todays_date + database_name + ".sql"

# Permet de connaître le répertoire courant
def currentDir():
    currentDir = print(os.getcwd())
    return currentDir

def banner():
    banner = """\033[92m
 |__ /__|_  )__/ | | _ ) __ _ __| |___  _ _ __  | _ \_  _| |___ 
  |_ \___/ /___| | | _ \/ _` / _| / / || | '_ \ |   / || | / -_)
 |___/  /___|  |_| |___/\__,_\__|_\_\\_,_| .__/ |_|_\\_,_|_\___|
                                         |_|                    
 \033[0m"""
    return banner

    #os.system("rm " + archive_db)
    #os.system("gzip -9 " + archive)
    #os.system("rm " + target_dir + archive)

def local_backup():
    os.system("tar -cvf " + archive + "/var/www/wordpress/*")
    os.system("mysqldump -u " + username + " -p" + password + " " + database_name + "  > " + archive_db)
    os.system("tar -rf " + archive + archive_db + " && " + "rm " + archive_db + " && " + "gzip -9 " + archive)
    os.system("mv " + zip_archive + " " + target_dir + " && " + "rm " + target_dir + archive)

def remote_backup():
    #with pysftp.Connection('192.168.2.2', username='philippe', password='password', cnopts=cnopts) as sftp:
        #with sftp.cd('/home/philippe/backup'):  # temporarily chdir to public
        #    sftp.put('/home/philippe/backup','/var/www/wordpress')  # upload file to /home/philippe/backup/ on remote
            # sftp.get('remote_file')  # get a remote file
    transport = paramiko.Transport(("192.168.2.2", 22))
    transport.connect(username = username, password =password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connection succesfully established ... ")
    path = "/home/philippe/backup/"
    localpath = "/var/www/wordpress/"
    sftp.put("/home/philippe/P6/backup/" + zip_archive, path + zip_archive)

    # sftp.put("/home/philippe/P6/backup/" + todays_date + database_name + ".sql", path + todays_date + database_name + ".sql")

    sftp.close()
    transport.close()

# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
def aws_backup():
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
        s3_client.upload_file("/home/philippe/P6/backup/" + zip_archive, 'p6-eu-west-1-bucket', zip_archive)
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
    restore_local = print("restore local")
    return restore_local

def restore_from_remote():
    restore_local = print("restore remote")
    return restore_local

def restore_from_aws():
    restore_local = print("restore aws")
    return restore_local


# Affichage du menu
def menu():
    print (banner() + """\033[96m
 [*] Manage your backup [*]
   [1]--Local (first rule)
   [2]--Remote (second rule)
   [3]--AWS S3 Bucket (third rule)
   [4]--3 rules
   [5]--Restore from Local
   [6]--Restore from Distant
   [7]--Restore from AWS
   [8]--Return current directory
   [0]--Exit
   \033[0m
 """)

def show_info(info):
    print('\033[31m' + info + '\033[31m')

def show_input():
    return "{0}P6~# {1}".format('\033[31m', '\033[0m')

menu()
choice = input(show_input())

if choice == "1":
    local_backup()
elif choice == "2":
    remote_backup()
elif choice == "3":
    aws_backup()
elif choice == "4":
    restore_from_local()
elif choice == "5":
    restore_from_remote()
elif choice == "6":
    restore_from_aws()
elif choice == "7":
    currentDir()
elif choice == "0":
    os.system('clear'), sys.exit()
elif choice == "":
    menu()
elif not int(choice) in range(0, 9):
    menu()
    show_info("Choix indisponible !")
    sys.exit()