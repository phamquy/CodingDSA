import multiprocessing
import os

def info(title):
    print(f\"{title} node name: {os.uname().nodename}\")
    print(f\"process id: {os.getpid()}\")

def f(name):
    info('function f')
    print(f\"hello {name}\")

if __name__ == '__main__':
    info('main line')
    p = multiprocessing.Process(target=f, args=('bob',))
    p.start()
    p.join()