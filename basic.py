from flask import Flask, request, jsonify
import paramiko
import logging

logger = logging.getLogger()
app = Flask(__name__)

@app.route('/')
def hello_world():
    
    return "hello"

@app.route('/install', methods=['POST'])    
def executeProcess():
    
    data = request.get_json()
    
    checkValidation(data)
    list = getData(data=data)
    
    for i in list:
        print(i)
        
    sshCommand(list)
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
    
    list = [host, port, userName, password, isHA, replica, mysqlPort]
    
    return list    
    
def sshCommand(list):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy) # 서버 호스트 키 자동 추가
    
    try:
        # ssh 연결
        ssh = paramiko.SSHClient()
        ssh.connect(hostname=list[0], port=list[1], username=list[2], password=list[3])
        
        arg1 = list[0]
        arg2 = list[1]
        script_command = f'/root/test.sh {arg1} {arg2}' # 테스트 용도
        stdin, stdout, stderr = ssh.exec_command(script_command)
    
        # 실시간으로 출력 읽기
        while not stdout.channel.exit_status_ready():
        # stdout에서 한 줄씩 읽고 출력
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode("utf-8")
                print(output, end='')  # 실시간 출력
        # 실행 후 남은 출력 읽기
        
        error = stderr.read().decode("utf-8")
        print(error)

        
        # 성공 시
        return jsonify("success"), 200
    except paramiko.AuthenticationException:
        return jsonify(error="Authentication failed"), 401
    finally:
        ssh.close()
    
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