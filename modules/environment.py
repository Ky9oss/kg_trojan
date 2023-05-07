import os

def run(**args):
    if '--protected' in args:
        return 'Environment Success'
    print("[*] In enveironment module.")
    return os.environ
