import os

def run(**args):
    print("[*] In dirlister module")
    if '--protected' in args:
        return 'Dirlister Success'
    files = os.listdir(".")
    return str(files)
