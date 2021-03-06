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
import config

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
##################################################"""

"""############### VARIABLES #####################"""
backup_path = '/home/philippe/P6/backup/'
wordpress_path = "/var/www/html/"
source_directory = '/var/www/wordpress'
todays_date = (time.strftime("%Y%m%d_%HH%M"))
free_space_needed = 1000000  # 1 Go
backup_site_name = 'wordpress'
database_name = 'wordpress_db'
archive = todays_date + "_" + backup_site_name + ".tar "
zip_archive = todays_date + "_" + backup_site_name + ".tar.gz"
archive_db = "dump.sql"
archive_db_path = backup_path + todays_date + database_name + ".sql"
rotation_time = '1440'  # 1 week = 10080, 1 day = 1440

def banner():
    """
        Fonction permettant de d??finir une banni??re pour le menu
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
        size = os.statvfs(backup_path)
        free_space = (size.f_bavail * size.f_frsize) / 1024
        if free_space > free_space_needed:
            os.system("tar -cvf " + archive + "/var/www/wordpress/*" + " --transform " + 's,^var/www/wordpress,' + todays_date + backup_site_name + ', ' + source_directory)
            os.system("mysqldump -u " + config.username + " -p" + config.password + " " + database_name + "  > " + archive_db)
            os.system("tar -rf " + archive + archive_db + " && " + "rm " + archive_db + " && " + "gzip -9 " + archive)
            os.system("mv " + zip_archive + " " + backup_path)
            print('Local backup successful ...')
        else:
            print('Not enough space !')
    except:
        print('An error occured !')

def del_backup(zip_archive):
    """
        Fonction permettant de supprimer une sauvegarde sur le serveur local
    """
    os.system("rm " + backup_path + zip_archive)

def remote_backup():
    """
        Fonction permettant de faire une sauvegarde sur le serveur distant

        Documentation:
        https://blog.ruanbekker.com/blog/2018/04/23/using-paramiko-module-in-python-to-execute-remote-bash-commands/
    """
    try:
        transport = paramiko.Transport((config.files_hostname, config.ssh_port))
        transport.connect(username=config.username, password=config.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Connection succesfully established ... ")
        sftp.put(backup_path + zip_archive, backup_path + zip_archive)
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
        Fonction permettant de faire une rotation sur le serveur distant
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.files_hostname, username=config.username, password=config.password)
    ssh.exec_command("find " + backup_path + ". -type f +" + rotation_time + " -delete")
    print('Remote backup rotation successful ...')
    ssh.close()

def aws_backup():
    """
        Fonction permettant de faire une sauvegarde dans un bucket S3 AWS

        Documentation:
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
        https://adamtheautomator.com/boto3-s3/

        NB: Une configuration de cycle de vie a directement ??t?? cr????e dans le bucket pour supprimer les objets apr??s 7 jours.
    """
    # Create an S3 Client
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )
    except:
        print('pb de connexion')

    # Upload object
    try:
        # Creating a bucket
        s3_client.create_bucket(Bucket=config.aws_bucket_name)
        print("Bucket created succesfully")
        print('Uploading object ...')
        """
            Upload a file to S3 with a progress bar.

            From https://alexwlchan.net/2021/04/s3-progress-bars/
        """
        file_size = os.stat(backup_path + zip_archive).st_size
        with tqdm.tqdm(total=file_size, unit="B", unit_scale=True, desc=zip_archive) as pbar:
            s3_client.upload_file(
                backup_path + zip_archive,
                config.aws_bucket_name,
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

    transport = paramiko.Transport((config.restore_hostname, config.ssh_port))
    transport.connect(username=config.username, password=config.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connection succesfully established ... ")
    sftp.put(backup_path + file_to_restore, wordpress_path + file_to_restore)
    sftp.close()
    transport.close()
    print('File has been sent ...')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.restore_hostname, username=config.username, password=config.password)
    ssh.exec_command("tar -xzvf " + wordpress_path + file_to_restore + " -C " + wordpress_path)
    os.system("sleep 5")
    print('File extraction successful')
    ssh.exec_command("rm " + wordpress_path + file_to_restore)
    ssh.exec_command("sudo mysql --user=philippe --password=password wordpress_db < dump.sql")
    os.system("sleep 3")
    ssh.exec_command("cd /var/www/html/20* && mv * /var/www/html")
    ssh.close()

def restore_from_remote():
    """
        Fonction permettant de faire une restauration depuis le serveur distant
    """

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.files_hostname, username=config.username, password=config.password)
    sftp = ssh.open_sftp()

    sftp.chdir(backup_path)
    for filename in sorted(sftp.listdir()):
        if filename.startswith('202'):
            sftp.get(filename, filename)
    ssh.close()

    backups = os.listdir("/home/philippe/P6")
    filtered_backups = [backup for backup in backups if backup.startswith("2021")]
    print("""\033[96m
            Quelle sauvegarde choisissez-vous ?
            \033[0m
        """)
    number = 0

    while number < len(filtered_backups):
        number = number + 1
        print(str(number) + ". " + filtered_backups[number - 1])

    backup_choice = input(show_input())
    file_to_restore = filtered_backups[int(backup_choice) - 1]
    print("Vous avez choisi la sauvegarde " + file_to_restore)

    transport = paramiko.Transport((config.restore_hostname, config.ssh_port))
    transport.connect(username=config.username, password=config.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connection succesfully established ... ")
    sftp.put("/home/philippe/P6/" + file_to_restore, wordpress_path + file_to_restore)
    sftp.close()
    transport.close()
    print('File has been sent ...')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.restore_hostname, username=config.username, password=config.password)
    ssh.exec_command("tar -xzvf " + wordpress_path + file_to_restore + " -C " + wordpress_path)
    os.system("sleep 5")
    print('File extraction successful')
    ssh.exec_command("rm " + wordpress_path + file_to_restore)
    ssh.exec_command("sudo mysql --user=" + config.username + " --password=" + config.password + " wordpress_db < dump.sql")
    os.system("sleep 3")
    ssh.exec_command("cd /var/www/html/20* && mv * /var/www/html")
    ssh.close()
    os.system("rm -f 2021*")

def restore_from_aws():
    """
        Fonction permettant de faire une restauration depuis le bucket S3 AWS
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )
    print("""\033[96m
        Quelle sauvegarde choisissez-vous ?
        \033[0m
    """)
    number = 0
    s3_objects = s3_client.list_objects(Bucket='p6-eu-west-1-bucket')['Contents']
    for key in s3_objects:
        number = number + 1
        print(str(number) + ". " + key['Key'])

    backup_choice = input(show_input())
    file_to_restore = s3_objects[int(backup_choice) - 1]['Key']
    print("Vous avez choisi la sauvegarde " + file_to_restore)

    s3_client.download_file(config.aws_bucket_name, file_to_restore, file_to_restore)

    transport = paramiko.Transport((config.restore_hostname, config.ssh_port))
    transport.connect(username=config.username, password=config.password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print("Connection succesfully established ... ")
    sftp.put("/home/philippe/P6/" + file_to_restore, wordpress_path + file_to_restore)
    sftp.close()
    transport.close()
    print('File has been sent ...')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.restore_hostname, username=config.username, password=config.password)
    ssh.exec_command("tar -xzvf " + wordpress_path + file_to_restore + " -C " + wordpress_path)
    os.system("sleep 5")
    print('File extraction successful')
    ssh.exec_command("rm /var/www/html/" + file_to_restore)
    ssh.exec_command("sudo mysql --user=" + config.username + " --password=" + config.password + " wordpress_db < dump.sql")
    os.system("sleep 3")
    ssh.exec_command("cd /var/www/html/20* && mv * /var/www/html")
    ssh.close()
    os.system("rm -f 2021*")

# Affichage du menu
def menu():
    """
        Fonction permettant d'afficher le menu'
    """
    print(banner() + """\033[96m
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
    print("D??but de la sauvegarde locale")
    local_backup()
    rotate()
elif choice == "2":
    print("D??but de la sauvegarde sur site distant")
    local_backup()
    remote_backup()
    rotate_remote()
    del_backup(zip_archive)
elif choice == "3":
    print("D??but de la sauvegarde sur AWS")
    local_backup()
    aws_backup()
    del_backup(zip_archive)
elif choice == "4":
    print("D??but de la r??gle 3-2-1")
    three_rules()
elif choice == "5":
    print("D??but de la restauration depuis la machine locale")
    restore_from_local()
elif choice == "6":
    print("D??but de la restauration depuis la machine distante")
    restore_from_remote()
elif choice == "7":
    print("D??but de la restauration depuis AWS")
    restore_from_aws()
elif choice == "0":
    os.system('clear'), sys.exit()
elif choice == "":
    menu()
elif not int(choice) in range(0, 9):
    menu()
    show_info("Choix indisponible !")
    sys.exit()