import paramiko
import os
import stat
from datetime import datetime

def upload_directory(local_dir, remote_dir, sftp):
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir.replace('\\', '/') + '/' + item

        if os.path.isdir(local_path):
            try:
                sftp.mkdir(remote_path)
            except OSError:
                pass  # Directory already exists

            upload_directory(local_path, remote_path, sftp)
        else:
            sftp.put(local_path, remote_path)

def read_command_from_file(file_path):
    with open(file_path, 'r') as file:
        command = file.read().strip()
    return command

def extract_file(remote_path, local_path, sftp):
    try:
        sftp.get(remote_path, local_path)
        print(f"File extracted successfully: {local_path}")
    except Exception as e:
        print(f"An error occurred while extracting the file: {e}")

def transfer_execute_download(host, username, password, local_script_path, local_output_path, remote_script_path, log_file, command):
    try:
        log(log_file, f"*")
        log(log_file, f"Starting Execution on machine {host}")

        # Connect to the remote server via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Create "collection" directory on the remote server
        remote_collection_dir = remote_script_path.replace('\\', '/') + '/Collection'
        log(log_file, f"Creating directory on remote server: {remote_collection_dir}")
        ssh.exec_command(f'mkdir -p {remote_collection_dir}')
        log(log_file, f'Executing command: mkdir -p {remote_collection_dir}')

        # Transfer script files from local machine to remote server
        remote_script_path_file = remote_collection_dir + '/Collection.zip'
        log(log_file, f"Transferring script file: {local_script_path} to {remote_script_path_file}")
        sftp.put(local_script_path, remote_script_path_file)
        log(log_file, f'Executing command: sftp.put {local_script_path} {remote_script_path_file}')

        # Unzip the transferred script file
        log(log_file, f"Unzipping transferred script file: {remote_script_path_file}")
        stdin, stdout, stderr = ssh.exec_command(f'unzip -o {remote_script_path_file} -d {remote_collection_dir}')
        stdout.channel.recv_exit_status()  # wait for unzip to finish
        log(log_file, f'Executing command: unzip -o {remote_script_path_file} -d {remote_collection_dir}')
        errors = stderr.read().decode('utf-8')

        if errors:
            log(log_file, f"Unzip Error: {errors}")
            print(f"Unzip Error: {errors}")

        # Set permissions for Collect.sh file
        collection_file_path = remote_collection_dir + '/Collection/bin/'
        log(log_file, "Setting permissions for Collect.sh file")
        ssh.exec_command(f'chmod 775 {collection_file_path}/Collect.sh')
        log(log_file, f'Executing command: chmod 775 {collection_file_path}/Collect.sh')

        # Execute the script on the remote server
        full_command = f'cd {collection_file_path} && {command}'
        log(log_file, f"Executing script on remote server: {collection_file_path}")
        stdin, stdout, stderr = ssh.exec_command(full_command)
        stdout.channel.recv_exit_status()  # wait for the command to finish
        log(log_file, f"Executing Command {full_command}")

        # Extract File named Collection
        remote_output_dir = collection_file_path + 'output/'
        stdin, stdout, stderr = ssh.exec_command(f'ls {remote_output_dir}Collection-*.tar')
        output_files = stdout.read().decode().strip().split()
        errors = stderr.read().decode('utf-8')
        if errors:
            log(log_file, f"Error listing output files: {errors}")
            print(f"Error listing output files: {errors}")

        if output_files:
            remote_output_path_file = output_files[0]  # Assuming there's only one matching file
            local_output_path_file = os.path.join(local_output_path, f'Collection_{host}_{username}_all.tar').replace('\\', '/')
            extract_file(remote_output_path_file, local_output_path_file, sftp)
            log(log_file, f"Transferring output file from remote server to local machine: {local_output_path_file}")
        else:
            log(log_file, "No matching output file found")
            print("No matching output file found")

        # Extract file named debug
        stdin, stdout, stderr = ssh.exec_command(f'ls {remote_output_dir}debug_*.tar')
        output_files = stdout.read().decode().strip().split()
        errors = stderr.read().decode('utf-8')
        if errors:
            log(log_file, f"Error listing output files: {errors}")
            print(f"Error listing output files: {errors}")

        if output_files:
            remote_output_path_file = output_files[0]  # Assuming there's only one matching file
            local_output_path_file = os.path.join(local_output_path, f'debug_{host}_{username}_all.tar').replace('\\', '/')
            extract_file(remote_output_path_file, local_output_path_file, sftp)
            log(log_file, f"Transferring output file from remote server to local machine: {local_output_path_file}")
        else:
            log(log_file, "No matching output file found")
            print("No matching output file found")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

        log(log_file, f"Finished Execution on machine {host}")
        log(log_file, f"")

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log(log_file, error_msg)
        print(error_msg)

        # Close the SSH connection if it's established
        if ssh:
            ssh.close()

def log(log_file, message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{current_time}] {message}\n")

def read_credentials_from_file(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        for line in file:
            host, username, password, local_script_path, local_output_path, remote_script_path = line.strip().split(',')
            credentials.append({
                'host': host, 
                'username': username, 
                'password': password,
                'local_script_path': local_script_path,
                'local_output_path': local_output_path,
                'remote_script_path': remote_script_path
            })
    return credentials

file_path = 'config.txt'
log_file = 'transfer_log.txt'
command_file_path = 'command.txt'

# Read the credentials from the credentials file
credentials = read_credentials_from_file(file_path)

# Read the command from the command file
command = read_command_from_file(command_file_path)

for cred in credentials:
    transfer_execute_download(
        cred['host'],
        cred['username'],
        cred['password'],
        cred['local_script_path'],
        cred['local_output_path'],
        cred['remote_script_path'],
        log_file,
        command
    )
