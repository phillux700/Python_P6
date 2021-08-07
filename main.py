#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import shutil

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

def local_backup():
    output_filename_1 = "%s.html_dir" % f_date
    output_filename_2 = "%s.html_dir.zip" % f_date
    dir_name = '/var/www/wordpress'
    dst = "%s" % date
    shutil.make_archive(output_filename_1, 'zip', dir_name)
    shutil.move(output_filename_2, dst)

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