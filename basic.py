from flask import Flask, request, jsonify
import paramiko
import logging

logger = logging.getLogger()
app = Flask(__name__)

@app.route('/install', methods=['POST'])    
def executeProcess():
    
    
    data = request.get_json()
    
    checkValidation(data)
    
    list = getData(data)
    
    ssh_master, ssh_slave1, ssh_slave2 = testSSHConnection(data)
        
    sshCommand(ssh_master, ssh_slave1, ssh_slave2, list)
    
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
    isHA = data.get('isHA')
    replica = data.get('replica')
    mysqlPort = data.get('mysqlPort')
    slave1 = data.get('slave1')
    slave2 = data.get('slave2')
    serverID1 = data.get('serverID1')
    serverID2 = data.get('serverID2')
    
    list = [host, port, userName, password, isHA, replica, mysqlPort, slave1, slave2, serverID1, serverID2]
    
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
        
# 자동 설치에 필요한 명령들 실행시키는 함수
def sshCommand(ssh_master, ssh_slave1, ssh_slave2,list):
    
    
    # 셋 다 동일하게 db 설치부터
    try:
        arg1 = list[3]
        script_command = f'/root/install.sh {arg1}' # 테스트 용도
        stdout, stderr = ssh_master.exec_command(script_command)
    
        # 실시간으로 출력 읽기
        while not stdout.channel.exit_status_ready():
        # stdout에서 한 줄씩 읽고 출력
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode("utf-8")
                print(output, end='') 
        error = stderr.read().decode("utf-8")
        print(error)

        
    except: "설치가 제대로 진행되지 않았습니다. 다시 시도해 주세요."
    finally:
        ssh_master.close()
        ssh_slave1.close()
        ssh_slave2.close()
                
    return
    
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