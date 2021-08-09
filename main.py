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

def local_backup():
    os.system("tar -cvf " + archive + "/var/www/wordpress/*")
    os.system("mv " + archive + target_dir)
    os.system("mysqldump -u " + username + " -p" + password + " " + database_name + "  > " + archive_db)
    os.system("tar -rf " + archive + archive_db)
    os.system("rm " + archive_db)
    os.system("cd /var/www/wordpress")
    os.system("gzip -9  " + archive)
    os.system("mv  " + archive + ".gz" + target_dir)
    os.system("rm " + target_dir + "/" + archive)

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
    sftp.put("/home/philippe/P6/backup/" + todays_date + database_name + ".sql", path + todays_date + database_name + ".sql")

    sftp.close()
    transport.close()

def aws_backup():
    print("aws")



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
    aws_backup()
elif choice == "5":
    aws_backup()
elif choice == "6":
    aws_backup()
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