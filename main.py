import paramiko
import os
from datetime import datetime

def transfer_execute_download(host, username, password, local_script_path, remote_script_path, remote_output_path, local_output_path, log_file):
    try:
        # Connect to the remote server via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Transfer script files from local machine to remote server
        transfer_command = f'sftp.put("{local_script_path}", "{remote_script_path}")'
        log(log_file, f"Transferring script file: {local_script_path} to {remote_script_path}", transfer_command)
        sftp.put(local_script_path, remote_script_path)

        # Unzip the transferred script file
        remote_script_dir = os.path.dirname(remote_script_path)
        unzip_command = f'unzip -o {remote_script_path} -d {remote_script_dir}'
        log(log_file, f"Unzipping transferred script file: {remote_script_path}", unzip_command)
        ssh.exec_command(unzip_command)

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log(log_file, error_msg)
        print(error_msg)
        # Close the SSH connection if it's established
        if ssh:
            ssh.close()


def read_credentials_from_file(file_path):

    credentials = []

    with open(file_path, 'r') as file:

        for line in file:

            host, username, password, local_script_path, remote_script_path  = line.strip().split(',')  # Adjust delimiter as needed

            credentials.append({'host': host, 'username': username, 'password': password,'local_script_path':local_script_path,'remote_script_path':remote_script_path})

    return credentials

def log(log_file, message, command=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{current_time}] {message}\n")
        if command:
            f.write(f"    Command Executed: {command}\n")



file_path = 'config.txt'
log_file = 'transfer_log.txt'

credentials = read_credentials_from_file(file_path)

for cred in credentials:

    transfer_execute_download(cred['host'],cred['username'],cred['password'],cred['local_script_path'],cred['remote_script_path'],log_file)

    
