from multiprocessing import Process, Pipe

def f(conn):
    conn.send([42, None, 'hello'])
    conn.send([42, None, 'hello2'])
    print(f"child received: {conn.recv()}")
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=f, args=(child_conn,))
    p.start()
    parent_conn.send([42, None, 'from parent'])
    print(f"parent received: {parent_conn.recv()}")
    print(f"parent received: {parent_conn.recv()}")
    p.join()