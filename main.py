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
import time
import paramiko
import boto3
import botocore
import tqdm

"""############### DOCUMENTATION ####################
https://docs.python.org/fr/3/library/os.html
https://docs.python.org/fr/3/library/sys.html
https://docs.python.org/fr/3/library/datetime.html
https://docs.python.org/fr/3/library/time.html
https://docs.python.org/fr/3/library/shutil.html
https://docs.python.org/fr/3/library/tarfile.html
http://docs.paramiko.org/en/stable/api/client.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
https://botocore.amazonaws.com/v1/documentation/api/latest/index.html
https://github.com/tqdm/tqdm
https://www.python.org/dev/peps/pep-0020/
https://www.python.org/dev/peps/pep-0008/
https://www.python.org/dev/peps/pep-0257/
"""

# --- Variables --- #
backup_path = '/home/philippe/P6/backup/'
source_directory = '/var/www/wordpress'
todays_date = (time.strftime("%Y%m%d_%HH%M"))
free_space_needed = 1000000
backup_site_name = 'wordpress'
database_name = 'wordpress_db'
target_dir = '/home/philippe/P6/backup/'
username = 'philippe'
password = 'password'
archive = todays_date + "_" + backup_site_name + ".tar "
zip_archive = todays_date + "_" + backup_site_name + ".tar.gz"
# archive_db = todays_date + database_name + ".sql"
archive_db = "dump.sql"
archive_db_path = target_dir + todays_date + database_name + ".sql"
rotation_time = '60'        # 1 week = 10080, 1 day = 1440

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
    return banner

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
    """
        Fonction permettant de supprimer une sauvegarde sur le serveur local
    """
    os.system("rm /home/philippe/P6/backup/" + zip_archive)

def remote_backup():
    """
        Fonction permettant de faire une sauvegarde sur le serveur distant

        Documentation:
        https://blog.ruanbekker.com/blog/2018/04/23/using-paramiko-module-in-python-to-execute-remote-bash-commands/
    """
    try:
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
    ssh.exec_command("find /home/philippe/P6/backup/. -type f +" + rotation_time + " -delete")
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

def three_rules():
    """
        Fonction permettant de faire une sauvegarde sur le serveur distant, sur le serveur local et sur AWS !
    """

    local_backup()
    remote_backup()
    aws_backup()
    rotate()
    rotate_remote()

def restore_from_local():
    """
        Fonction permettant de faire une restauration depuis le serveur local
    """

    backups = os.listdir("/home/philippe/P6/backup")
    print("""\033[96m
        Quelle sauvegarde choisissez-vous ?
        \033[0m
    """)
    number = 0
    while number < len(backups):
        number = number + 1
        print(str(number) + ". " + backups[number - 1])

    backup_choice = input(show_input())
    file_to_restore = backups[int(backup_choice) - 1]
    print("Vous avez choisi la sauvegarde " + file_to_restore)

    transport = paramiko.Transport(("192.168.1.4", 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connection succesfully established ... ")
    sftp.put("/home/philippe/P6/backup/" + file_to_restore, "/var/www/html/" + file_to_restore)
    sftp.close()
    transport.close()
    print('File has been sent ...')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='192.168.1.4', username=username, password=password)
    ssh.exec_command("tar -xzvf /var/www/html/" + file_to_restore + " -C /var/www/html/")
    os.system("sleep 5")
    print('File extraction successful')
    ssh.exec_command("rm /var/www/html/" + file_to_restore)
    ssh.exec_command("sudo mysql --user=philippe --password=password wordpress_db < dump.sql")
    os.system("sleep 3")
    ssh.exec_command("cd /var/www/html/20* && mv * /var/www/html")
    ssh.close()


    #### TODO Le fichier est envoyé: il reste la restauration à faire

def restore_from_remote():
    """
        Fonction permettant de faire une restauration depuis le serveur distant
    """

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='192.168.2.2', username=username, password=password)
    output = ""
    stdin, stdout, stderr = ssh.exec_command("ls /home/philippe/P6/backup")
    stdout = stdout.readlines()
    print(stdout)

    print("""\033[96m
            Quelle sauvegarde choisissez-vous ?
            \033[0m
        """)
    number = 0
    while number < len(stdout):
        number = number + 1
        print(str(number) + ". " + stdout[number - 1])

    backup_choice = input(show_input())
    file_to_restore = stdout[int(backup_choice) - 1]
    print("Vous avez choisi la sauvegarde " + file_to_restore)
    print(file_to_restore)
    sftp = ssh.open_sftp()
    sftp.get("/home/philippe/P6/backup/" + file_to_restore, "/home/philippe/P6/tmp/" + file_to_restore)
    sftp.close()

    #with SCPClient(ssh.get_transport()) as scp:
    #    scp.put(file_to_restore, '/home/philippe/P6/')
    #    #scp.get(file_to_restore)

    #os.system("sshpass -p password scp -r -p -v philippe@192.168.2.2:/home/philippe/P6/backup/" + file_to_restore + " /home/philippe/P6/tmp/")

    #print("sshpass -e sftp philippe@192.168.1.4:/var/www/html <<< $'put /home/philippe/P6/backup/'" + file_to_restore)
    #ssh.exec_command("sshpass -e sftp philippe@192.168.1.4:/var/www/html <<< $'put /home/philippe/P6/backup/'" + file_to_restore)
    #ssh.exec_command("sshpass -e scp /home/philippe/P6/backup/" + file_to_restore + " philippe@192.168.1.4:/var/www/html")
    #print("sshpass -e scp /home/philippe/P6/backup/" + file_to_restore)
    #print(" philippe@192.168.1.4:/var/www/html")
    #ssh.exec_command("sleep 5")
    #os.system("sleep 5")
    ssh.close()

    #ssh = paramiko.SSHClient()
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(hostname='192.168.1.4', username=username, password=password)
    #ssh.exec_command("tar -xzvf /var/www/html/" + file_to_restore + " -C /var/www/html/")
    #os.system("sleep 5")
    #print('File extraction successful')
    #ssh.exec_command("rm /var/www/html/" + file_to_restore)
    #ssh.exec_command("sudo mysql --user=philippe --password=password wordpress_db < dump.sql")
    #os.system("sleep 3")
    #ssh.exec_command("cd /var/www/html/20* && mv * /var/www/html")
    #ssh.close()
    #### TODO Vérifier que je peux envoyer sur le serveur et faire la restauration

def restore_from_aws():
    """
        Fonction permettant de faire une restauration depuis le bucket S3 AWS
    """
    restore_aws = print("restore aws")
    return restore_aws
    #### TODO Afficher liste des fichiers avec une boucle et saisir le choix (exemple: choix = input('Saisissez le choix')


# Affichage du menu
def menu():
    """
        Fonction permettant d'afficher le menu'
    """
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

menu()
choice = input(show_input())

if choice == "1":
    local_backup()
    rotate()
elif choice == "2":
    local_backup()
    remote_backup()
    rotate_remote()
    del_backup(zip_archive)
elif choice == "3":
    local_backup()
    aws_backup()
    del_backup(zip_archive)
elif choice == "4":
    three_rules()
elif choice == "5":
    restore_from_local()
elif choice == "6":
    restore_from_remote()
elif choice == "7":
    restore_from_aws()
elif choice == "0":
    os.system('clear'), sys.exit()
elif choice == "":
    menu()
elif not int(choice) in range(0, 9):
    menu()
    show_info("Choix indisponible !")
    sys.exit()