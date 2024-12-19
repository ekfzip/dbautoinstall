from flask import Flask, request, jsonify
import paramiko
import logging

app = Flask(__name__)

@app.route('/')
def hello_world():
    
    return "hello"

@app.route('/example', methods=['GET', 'POST'])
def connectExample():
    data = request.get_json()
    isHA = data.get('isHA')
    print(isHA)
    if not data:
        return "No JSON data received", 400
    return jsonify({"isHA": isHA})

@app.route('/install', methods=['GET', 'POST'])    
def executeProcess():
    
    setLogFile()
    data = request.get_json()
    
    list = checkValidation(data)
    for i in list:
        print(i)
        
    sshCommand(list)
    

    return "Exit"
    
def checkValidation(data):
    if not data:
        return jsonify(error="Invalid or missing JSON data"), 400
    
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
        ssh.connect(hostname=list[0], port=list[1], username=list[2], password=list[3])
        stdin, stdout, stderr = ssh.exec_command("ls")
        
        # 실시간으로 출력 읽기
        while not stdout.channel.exit_status_ready():
        # stdout에서 한 줄씩 읽고 출력
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode("utf-8")
                print(output, end='')  # 실시간 출력



        # 실행 후 남은 출력 읽기
        output = stdout.read().decode("utf-8")
        print(output)

        
        # 성공 시
        return jsonify("success"), 200
    except paramiko.AuthenticationException:
        return jsonify(error="Authentication failed"), 401

def setLogFile():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    
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