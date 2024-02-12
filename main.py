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
 
        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()
 
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Close the SSH connection if it's established
        if ssh:
            ssh.close()
