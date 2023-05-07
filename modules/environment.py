import os

def run(**args):
    print("[*] In enveironment module.")
    if '--protected' in args:
        return 'Environment Success'
    return os.environ
