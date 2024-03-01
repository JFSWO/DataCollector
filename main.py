
import paramiko
import os
from datetime import datetime



def transfer_execute_download(host, username, password, local_script_path, remote_script_path, log_file):

    try:

        # Connect to the remote server via SSH

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)



        # Open an SFTP session

        sftp = ssh.open_sftp()



        # Create "collection" directory on the remote server

        remote_collection_dir = os.path.join(remote_script_path, "collection")
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
        ssh.exec_command(f'unzip -o {remote_script_path_file} -d {remote_collection_dir}')
        log(log_file, f'Executing command: unzip -o {remote_script_path_file} -d {remote_collection_dir}')



        # Set permissions for Collect.sh file

        collection_file_path= remote_collection_dir + '/Collection/bin/'
        log(log_file, "Setting permissions for Collect.sh file")
        ssh.exec_command(f'chmod 775 {os.path.join(collection_file_path, "Collect.sh")}')
        log(log_file, f'Executing command: chmod 775 {os.path.join(collection_file_path, "Collection.sh")}')



        # Execute the script on the remote server

        #log(log_file, f"Executing script on remote server: {collection_file_path}")
        #ssh.exec_command(f'bash {collection_file_path[:-4]}')
        #log(log_file, f'Executing command: bash {collection_file_path[:-4]}')


        # Save the output of the script locally on the server
        
        #remote_output_file = os.path.join(remote_output_path, os.path.basename(local_script_path) + ".out")
        #log(log_file, f"Copying output file from remote server to local machine: {remote_output_file}")
        #ssh.exec_command(f'cp {remote_script_path[:-4]}.out {remote_output_file}')
        #log(log_file, f'Executing command: cp {remote_script_path[:-4]}.out {remote_output_file}')

        
        # Transfer the output file from the remote server to local machine
        
        #log(log_file, f"Transferring output file from remote server to local machine: {remote_output_file}")
        #sftp.get(remote_output_file, local_output_path)
        #log(log_file, f'Executing command: sftp.get {remote_output_file} {local_output_path}')


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



def log(log_file, message):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a') as f:

        f.write(f"[{current_time}] {message}\n")



def read_credentials_from_file(file_path):

    credentials = []

    with open(file_path, 'r') as file:

        for line in file:

            host, username, password, local_script_path, remote_script_path = line.strip().split(',')  # Adjust delimiter as needed

            credentials.append({'host': host, 'username': username, 'password': password,'local_script_path':local_script_path,'remote_script_path':remote_script_path})

    return credentials





file_path = 'config.txt'
log_file = 'transfer_log.txt'
credentials = read_credentials_from_file(file_path)



for cred in credentials:
    transfer_execute_download(cred['host'],cred['username'],cred['password'],cred['local_script_path'],cred['remote_script_path'],log_file)



    



    

    

    
