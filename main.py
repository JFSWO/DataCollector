import os
import paramiko
from datetime import datetime

def upload_directory(local_dir, remote_dir, sftp):
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = os.path.join(remote_dir, item)
        
        if os.path.isdir(local_path):
            try:
                sftp.mkdir(remote_path)
            except OSError as e:
                pass  # Directory already exists
            upload_directory(local_path, remote_path, sftp)
        else:
            sftp.put(local_path, remote_path)

def read_command_from_file(file_path):
    with open(file_path, 'r') as file:
        command = file.readline().strip()
    return command

def extract_file(remote_path, local_path, sftp):
    try:
        sftp.get(remote_path, local_path)
        print(f"File extracted successfully: {local_path}")
    except Exception as e:
        print(f"An error occurred while extracting the file: {e}")

def transfer_execute_download(host, username, password, local_script_path, local_output_path, log_file, command):
    try:
        log(log_file, f"*")
        log(log_file, f"Starting Execution on machine {host}")

        # Connect to the remote server via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Create remote directory for script on the remote server
        remote_home = ssh.exec_command("echo %USERPROFILE%")[1].read().decode().strip()  # Home directory on Windows
        remote_collection_dir = os.path.join(remote_home, 'Collection')
        log(log_file, f"Creating directory on remote server: {remote_collection_dir}")
        ssh.exec_command(f'mkdir -p {remote_collection_dir}')
        log(log_file, f'Executing command: mkdir -p {remote_collection_dir}')

        # Transfer script files from local machine to remote server
        remote_script_path_file = os.path.join(remote_collection_dir, 'Collection.zip')
        log(log_file, f"Transferring script file: {local_script_path} to {remote_script_path_file}")
        sftp.put(local_script_path, remote_script_path_file)
        log(log_file, f'Executing command: sftp.put {local_script_path} {remote_script_path_file}')

        # Unzip the transferred script file
        log(log_file, f"Unzipping transferred script file: {remote_script_path_file}")
        ssh.exec_command(f'powershell.exe Expand-Archive -Path {remote_script_path_file} -DestinationPath {remote_collection_dir} -Force')
        log(log_file, f'Executing command: Expand-Archive -Path {remote_script_path_file} -DestinationPath {remote_collection_dir} -Force')

        # Set path for executing PowerShell script
        collection_file_path = remote_collection_dir + '\\Collection\\bin\\'
        full_command = f'powershell.exe {collection_file_path}Collect.ps1 {command}'
        log(log_file, f"Executing script on remote server: {full_command}")
        stdin, stdout, stderr = ssh.exec_command(full_command)
        stdout.channel.recv_exit_status()  # wait for the command to finish
        log(log_file, f"Executing Command: {full_command}")

        # Transfer output file(s) from remote server
        remote_output_dir = os.path.join(collection_file_path, 'output')
        log(log_file, f"Searching for output files in {remote_output_dir}")

        # Extract 'Collection' file
        stdin, stdout, stderr = ssh.exec_command(f'ls {remote_output_dir}Collection-*.tar')
        output_files = stdout.read().decode().strip().split()
        if output_files:
            remote_output_path_file = output_files[0]
            local_output_path_file = os.path.join(local_output_path, f'Collection_{host}_{username}_all.tar')
            extract_file(remote_output_path_file, local_output_path_file, sftp)
            log(log_file, f"Transferred output file to local machine: {local_output_path_file}")
        else:
            log(log_file, "No matching 'Collection' output file found")

        # Extract 'debug' file
        stdin, stdout, stderr = ssh.exec_command(f'ls {remote_output_dir}debug_*.tar')
        output_files = stdout.read().decode().strip().split()
        if output_files:
            remote_output_path_file = output_files[0]
            local_output_path_file = os.path.join(local_output_path, f'debug_{host}_{username}_all.tar')
            extract_file(remote_output_path_file, local_output_path_file, sftp)
            log(log_file, f"Transferred output file to local machine: {local_output_path_file}")
        else:
            log(log_file, "No matching 'debug' output file found")

        # Close SFTP session and SSH connection
        sftp.close()
        ssh.close()

        log(log_file, f"Finished Execution on machine {host}")
        log(log_file, f"")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log(log_file, error_msg)
        print(error_msg)

def log(log_file, message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{current_time}] {message}\n")

def read_credentials_from_file(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        command = file.readline().strip()  # Read the first line as the command
        for line in file:
            host, username, password = line.strip().split(',')
            credentials.append({'host': host, 'username': username, 'password': password, 'command': command})
    return credentials

# Main code
config_directory = 'configs'  # Directory containing multiple config files
log_file = 'transfer_log.txt'
local_script_path = os.path.join(os.path.dirname(_file_), 'Collection.zip')  # Script file in the same directory

# Iterate over each config file in the directory
for config_file in os.listdir(config_directory):
    config_file_path = os.path.join(config_directory, config_file)
    credentials = read_credentials_from_file(config_file_path)

    for cred in credentials:
        transfer_execute_download(cred['host'], cred['username'], cred['password'], local_script_path, './output', log_file, cred['command'])
