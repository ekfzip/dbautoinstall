from flask import Flask, request, jsonify
from scp import SCPClient
import paramiko
import logging

logger = logging.getLogger()
app = Flask(__name__)

@app.route('/install', methods=['POST'])    
def executeProcess():
    
    
    data = request.get_json()
    
    print(checkValidation(data))
    
    ssh_master, ssh_slave1, ssh_slave2 = testSSHConnection(data)
        
    sentToFile(ssh_master, ssh_slave1, ssh_slave2)
    
    chmodChange(ssh_master, ssh_slave1, ssh_slave2)
        
    installDB(ssh_master, ssh_slave1, ssh_slave2, data)
    
    settingDB(ssh_master, ssh_slave1, ssh_slave2, data)
    
    setLogFile()

    return "finished process"
    
def checkValidation(data):
    if not data:
        return "Invalid or missing JSON data"
    
    return "successfully received data"
      

# master, slave 서버 연결 확인하는 함수
def testSSHConnection(data):
    
    ssh_master = paramiko.SSHClient()
    ssh_slave1 = paramiko.SSHClient()
    ssh_slave2 = paramiko.SSHClient()
    
    ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_slave1.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_slave2.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    
    try:
        ssh_master.connect(hostname=data.get('host'), port=data.get('port'), username=data.get('username'), password=data.get('password'))
        ssh_slave1.connect(hostname=data.get('slave1'), port=data.get('port'), username=data.get('username'), password=data.get('password'))
        ssh_slave2.connect(hostname=data.get('slave2'), port=data.get('port'), username=data.get('username'), password=data.get('password'))
        
        host = data.get('host')
        slave1 = data.get('slave1')
        slave2 = data.get('slave2')
        script_command_master = f'echo {host}'
        script_command_slave1 = f'echo {slave1}'
        script_command_slave2 = f'echo {slave2}'
        
        print("Master DB Executing command:", script_command_master)
        print("Slave DB 1 Executing command:", script_command_slave1)
        print("Slave DB 2 Executing command:", script_command_slave2)
        
    except: print("connection failed")
    
    return ssh_master, ssh_slave1, ssh_slave2

def sentToFile(ssh_master, ssh_slave1, ssh_slave2):
    
    scp_master = SCPClient(ssh_master.get_transport())
    scp_slave1 = SCPClient(ssh_slave1.get_transport())
    scp_slave2 = SCPClient(ssh_slave2.get_transport())
    
    basic_install_path = '/Users/user/Desktop/test/basic_install.sh'
    basic_install_file = '/root/basic_install.sh'
    try:
        
        scp_master.put(basic_install_path, basic_install_file)
        scp_slave1.put(basic_install_path, basic_install_file)
        scp_slave2.put(basic_install_path, basic_install_file)
        
        print("basic_install.sh 파일이 정상적으로 전송되었습니다.")
        
    except: print("파일이 정상적으로 전송되지 않았습니다. 다시 시도해 주세요.")
    
    
    try:
        scp_master.put('/Users/user/Desktop/test/master_db.sh', '/root/master_db.sh')
        scp_slave1.put('/Users/user/Desktop/test/slave_db.sh', '/root/slave_db.sh')
        scp_slave2.put('/Users/user/Desktop/test/slave_db.sh', '/root/slave_db.sh')
        
        print("master_db.sh, slave_db.sh 파일이 정상적으로 전송되었습니다.")
        
    except: print("파일이 정상적으로 전송되지 않았습니다. 다시 시도해 주세요.")
    
            
        
# 자동 설치에 필요한 명령들 실행시키는 함수
def installDB(ssh_master, ssh_slave1, ssh_slave2, data):
    
    
    # 셋 다 동일하게 db 설치부터
    try:
        arg1 = data.get('password') # password
        arg2 = data.get('mysqlPort') # mysqlPort
        count = 1
        
        script_command = f'/root/basic_install.sh {arg1} {arg2}' # 테스트 용도
        ssh_list = [ssh_master, ssh_slave1, ssh_slave2]
        
        for s in ssh_list:
            print(f"{count}번째 DB 설치를 시작합니다.")
            count += 1
            stdin, stdout, stderr = s.exec_command(script_command)
            showScriptOutput(stdout, stderr)    
        
        # stdin, stdout, stderr = ssh_master.exec_command(script_command)
        # showScriptOutput(stdout, stderr)

        
    except: "DB 설치가 제대로 진행되지 않았습니다. 다시 시도해 주세요."
                
    return

def settingDB(ssh_master, ssh_slave1, ssh_slave2, data):
    
    # master DB
    try:
        master_arg1 = data.get('password') # password
        master_arg2 = data.get('slave1') # slave 1 ip
        master_arg3 = data.get('slave2') # slave 2 ip
        script_command = f'/root/master_db.sh {master_arg1} {master_arg2} {master_arg3}' 
        stdin, stdout, stderr = ssh_master.exec_command(script_command)
        showScriptOutput(stdout, stderr)
        
    except: print("Master DB 환경 설정이 정상적으로 진행되지 않았습니다.")
    
    slave_arg1 = data.get('serverID1') # server id 1
    slave_arg2 = data.get('serverID2') # server id 2
    slave_arg3 = data.get('host') # host
    slave_arg4 = data.get('password') # password
    slave_arg5 = data.get('mysqlPort') # mysqlPort
    
    # slave DB
    try:
        script_command = f'/root/slave_db.sh {slave_arg1} {slave_arg3} {slave_arg4} {slave_arg5}' 
        stdin, stdout, stderr = ssh_slave1.exec_command(script_command)
        showScriptOutput(stdout, stderr)
    except: print("첫 번쩨 Slave DB 환경 설정이 정상적으로 진행되지 않았습니다.")
    
    try: 
        script_command = f'/root/slave_db.sh {slave_arg2} {slave_arg3} {slave_arg4} {slave_arg5}' 
        stdin, stdout, stderr = ssh_slave2.exec_command(script_command)
        showScriptOutput(stdout, stderr)
    except: print("두 번쩨 Slave DB 환경 설정이 정상적으로 진행되지 않았습니다.")
        
    
def showScriptOutput(stdout, stderr):
    # 실시간으로 출력 읽기
    while not stdout.channel.exit_status_ready():
    # stdout에서 한 줄씩 읽고 출력
        if stdout.channel.recv_ready():
            output = stdout.channel.recv(1024).decode("utf-8")
            print(output, end='') 
    error = stderr.read().decode("utf-8")
    print(error)

def chmodChange(ssh_master, ssh_slave1, ssh_slave2):
    
    ssh_list = [ssh_master, ssh_slave1, ssh_slave2]
    
    basic_command = f'chmod +x /root/basic_install.sh'
    ls_command = f'ls -al /root'
    
    for s in ssh_list:
        
        s.exec_command(basic_command)
        stdin_ls, stdout_ls, stderr_ls = s.exec_command(ls_command)
        showScriptOutput(stdout_ls, stderr_ls)
        
        if s == ssh_master:
            stdin_ls, stdout_ls, stderr_ls = s.exec_command("chmod +x /root/master_db.sh")
            showScriptOutput(stdout_ls, stderr_ls)
        else:
            stdin_ls, stdout_ls, stderr_ls = s.exec_command("chmod +x /root/slave_db.sh")
            showScriptOutput(stdout_ls, stderr_ls)
            
                
    
def setLogFile():
    
    for log in logger.handlers:
        log.flush()
    # 이건 콘솔에 출력하는 로그
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 파일 핸들러
    file_handler = logging.FileHandler('/Users/user/Documents/test_log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    
if __name__ == '__main__':
    app.run(debug=True)