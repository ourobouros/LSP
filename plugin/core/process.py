from .logging import debug, exception_log, server_log
import subprocess
import os
import threading

try:
    from typing import Any, List, Dict, Tuple, Callable, Optional, Union
    assert Any and List and Dict and Tuple and Callable and Optional and Union
except ImportError:
    pass


def start_server(server_binary_args: 'List[str]', working_dir: str,
                 env: 'Dict[str,str]') -> 'Optional[subprocess.Popen]':
    debug("starting " + str(server_binary_args))
    si = None
    if os.name == "nt":
        si = subprocess.STARTUPINFO()  # type: ignore
        si.dwFlags |= subprocess.SW_HIDE | subprocess.STARTF_USESHOWWINDOW  # type: ignore

    return subprocess.Popen(
        server_binary_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir,
        env=env,
        startupinfo=si)


def attach_logger(process: 'subprocess.Popen', stream) -> None:
    threading.Thread(target=log_stream, args=(process, stream)).start()


def log_stream(process: 'subprocess.Popen', stream) -> None:
    """
    Reads any errors from the LSP process.
    """
    running = True
    while running:
        running = process.poll() is None

        try:
            content = stream.readline()
            if not content:
                break
            try:
                decoded = content.decode("UTF-8")
            except UnicodeDecodeError:
                decoded = content
            server_log(decoded.strip())
        except IOError as err:
            exception_log("Failure reading stream", err)
            return

    debug("LSP stream logger stopped.")
