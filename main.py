import paramiko
import os
 
def transfer_execute_download(host, username, password, local_script_path, remote_script_path, remote_output_path, local_output_path):
    try:
        # Connect to the remote server via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
 
        # Open an SFTP session
        sftp = ssh.open_sftp()
 
        # Transfer script files from local machine to remote server
        sftp.put(local_script_path, remote_script_path)
 
        # Unzip the transferred script file
        remote_script_dir = os.path.dirname(remote_script_path)
        ssh.exec_command(f'unzip -o {remote_script_path} -d {remote_script_dir}')
 
        # Execute the script on the remote server
        ssh.exec_command(f'bash {remote_script_path[:-4]}')
 
        # Save the output of the script locally on the server
        remote_output_file = os.path.join(remote_output_path, os.path.basename(local_script_path) + ".out")
        ssh.exec_command(f'cp {remote_script_path[:-4]}.out {remote_output_file}')
 
        # Transfer the output file from the remote server to local machine
        sftp.get(remote_output_file, local_output_path)
 
        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()
 
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Close the SSH connection if it's established
        if ssh:
            ssh.close()
 
# Example usage
host = 'your_server_host'
username = 'your_username'
password = 'your_password'
local_script_path = '/path/to/local/script.zip'
remote_script_path = '/path/to/remote/script.zip'
remote_output_path = '/path/to/remote/output'
local_output_path = '/path/to/local/output'
 
transfer_execute_download(host, username, password, local_script_path, remote_script_path, remote_output_path, local_output_path)
