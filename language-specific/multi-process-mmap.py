from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory
import os
import time

def writer(shm_name):
    # Attach to the existing shared memory block by its unique name
    existing_shm = SharedMemory(name=shm_name)
    print(f"[Writer {os.getpid()}] Writing to shared memory...")
    message = b"Hello from child process!"
    existing_shm.buf[:len(message)] = message
    existing_shm.close() # Detach, don't unlink

def reader(shm_name):
    time.sleep(0.5) # Give writer a head start
    # Attach to the existing shared memory block by its unique name
    existing_shm = SharedMemory(name=shm_name)
    print(f"[Reader {os.getpid()}] Reading from shared memory...")
    data = bytes(existing_shm.buf[:30]).decode('utf-8').strip('\x00')
    print(f"[Reader {os.getpid()}] Read: {data}")
    existing_shm.close()

if __name__ == '__main__':
    # Create a named shared memory block (works across spawn)
    shm = SharedMemory(create=True, size=1024)
    print(f"[Main {os.getpid()}] Created shared memory: {shm.name}")

    # Initialize with a starting value
    shm.buf[:5] = b"START"

    # Pass the NAME of the shared memory, not the object itself
    p1 = Process(target=writer, args=(shm.name,))
    p2 = Process(target=reader, args=(shm.name,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # Read final value in main process
    print(f"[Main {os.getpid()}] Final value: {bytes(shm.buf[:30]).decode('utf-8').strip()}")

    shm.close()
    shm.unlink() # Clean up the shared memory block from the OS
