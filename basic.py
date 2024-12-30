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
    
    list = getData(data)
    
    ssh_master, ssh_slave1, ssh_slave2 = testSSHConnection(data)
        
    sentToFile(ssh_master, ssh_slave1, ssh_slave2)
        
    installDB(ssh_master, ssh_slave1, ssh_slave2, list)
    
    settingDB(ssh_master, ssh_slave1, ssh_slave2, list)
    
    setLogFile()

    return "finished process"
    
def checkValidation(data):
    if not data:
        return "Invalid or missing JSON data"
    
    return "successfully received data"
    
def getData(data):
    
    host = data.get('host')
    port = data.get('port')
    userName = data.get('username')
    password = data.get('password')
    # isHA = data.get('isHA')
    # replica = data.get('replica')
    mysqlPort = data.get('mysqlPort')
    slave1 = data.get('slave1')
    slave2 = data.get('slave2')
    serverID1 = data.get('serverID1')
    serverID2 = data.get('serverID2')
    
    list = [host, port, userName, password, mysqlPort, slave1, slave2, serverID1, serverID2]
    
    return list    

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
        
        print("Executing command:", script_command_master)
        print("Executing command:", script_command_slave1)
        print("Executing command:", script_command_slave2)
        
    except: "connection failed"
    
    return ssh_master, ssh_slave1, ssh_slave2

def sentToFile(ssh_master, ssh_slave1, ssh_slave2):
    scp_master = SCPClient(ssh_master.get_transport())
    scp_slave1 = SCPClient(ssh_slave1.get_transport())
    scp_slave2 = SCPClient(ssh_slave2.get_transport())
    try:
        
        scp_master.put('/Users/user/Desktop/test/basic_install.sh', '/root/basic_install.sh')
        scp_slave1.put('/Users/user/Desktop/test/basic_install.sh', '/root/basic_install.sh')
        scp_slave2.put('/Users/user/Desktop/test/basic_install.sh', '/root/basic_install.sh')
        
        print("basic_install.sh 파일이 정상적으로 전송되었습니다.")
        
    except: print("파일이 정상적으로 전송되지 않았습니다. 다시 시도해 주세요.")
    
    
    try:
        scp_master.put('/Users/user/Desktop/test/master_db.sh', '/root/master_db.sh')
        scp_slave1.put('/Users/user/Desktop/test/slave_db.sh', '/root/slave_db.sh')
        scp_slave2.put('/Users/user/Desktop/test/slave_db.sh', '/root/slave_db.sh')
        
        print("master_db.sh, slave_db.sh 파일이 정상적으로 전송되었습니다.")
        
    except: print("파일이 정상적으로 전송되지 않았습니다. 다시 시도해 주세요.")
    
            
        
# 자동 설치에 필요한 명령들 실행시키는 함수
def installDB(ssh_master, ssh_slave1, ssh_slave2,list):
    
    
    # 셋 다 동일하게 db 설치부터
    try:
        arg1 = list[3] # password
        arg2 = list[4] # mysqlPort
        count = 0
        
        script_command = f'/root/basic_install.sh {arg1} {arg2}' # 테스트 용도
        ssh_list = [ssh_master, ssh_slave1, ssh_slave2]
        for s in ssh_list:
            print(count + "번째 DB 설치를 시작합니다.")
            count += 1
            stdout, stderr = s.exec_command(script_command)
            showScriptOutput(stdout, stderr)    

        
    except: "DB 설치가 제대로 진행되지 않았습니다. 다시 시도해 주세요."
    finally:
        ssh_master.close()
        ssh_slave1.close()
        ssh_slave2.close()
                
    return

def settingDB(ssh_master, ssh_slave1, ssh_slave2, list):
    
    # master DB
    try:
        master_arg1=list[3] # password
        master_arg2=list[5] # slave 1 ip
        master_arg3=list[6] # slave 2 ip
        script_command = f'/root/master_db.sh {master_arg1} {master_arg2} {master_arg3}' 
        stdout, stderr = ssh_master.exec_command(script_command)
        showScriptOutput(stdout, stderr)
        
    except: print("Master DB 환경 설정이 정상적으로 진행되지 않았습니다.")
    
    slave_arg1=list[7] # server id 1
    slave_arg2=list[8] # server id 2
    slave_arg3=list[0] # host
    slave_arg4=list[3] # password
    slave_arg5=list[4] # mysqlPort
    
    # slave DB
    try:
        script_command = f'/root/slave_db.sh {slave_arg1} {slave_arg3} {slave_arg4}, {slave_arg5}' 
        stdout, stderr = ssh_slave1.exec_command(script_command)
        showScriptOutput(stdout, stderr)
    except: print("첫 번쩨 Slave DB 환경 설정이 정상적으로 진행되지 않았습니다.")
    
    try: 
        script_command = f'/root/slave_db.sh {slave_arg2} {slave_arg3} {slave_arg4}, {slave_arg5}' 
        stdout, stderr = ssh_slave2.exec_command(script_command)
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
        
    
def setLogFile():
    
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