#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

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

# Affichage du menu
def menu():
    print (banner() + """\033[96m
 [*] Manage your backup [*]
   [1]--Local (first rule)
   [2]--Distant (second rule)
   [3]--AWS S3 Bucket (third rule)
   [4]--Restore from Local
   [5]--Restore from Distant
   [6]--Restore from AWS
   [7]--Return current directory
   [0]--Exit
   \033[0m
 """)

def show_info(info):
    print('\033[31m' + info + '\033[31m')

def show_input():
    return "{0}cisco~# {1}".format('\033[31m', '\033[0m')

menu()
choice = input(show_input())

if choice == "7":
    currentDir()
elif choice == "0":
    os.system('clear'), sys.exit()
elif choice == "":
    menu()
elif not int(choice) in range(0, 8):
    menu()
    show_info("Choix indisponible !")
    sys.exit()
