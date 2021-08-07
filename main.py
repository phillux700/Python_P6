#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import shutil
import tarfile

date = datetime.datetime.now().strftime('%Y%m%d-%s')
f_date = datetime.datetime.now().strftime('%Y%m%d')

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

# --- Variables --- #
backup_path = '/home/philippe/P6/backup/'
source_directory = '/var/www/wordpress'
todays_date = (time.strftime("%d-%m-%Y"))
free_space_needed = 1000000
backup_site_name = 'wordpress'
database_name = 'wordpress_db'
target_dir = '/home/philippe/P6/backup/'
username = 'philippe'
password = 'password'

def local_backup():
    os.system("tar -zcvf " + target_dir + todays_date + backup_site_name + ".tar.gz " + source_directory)
    os.system("mysqldump -u " + username + " -p" + password + " " + database_name + "  > " + target_dir + todays_date + database_name + ".sql")


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