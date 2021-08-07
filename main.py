#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Permet de connaître le répertoire courant
print(os.getcwd())

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
   [0]--Exit
   \033[0m
 """)

menu()
