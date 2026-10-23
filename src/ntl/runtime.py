"""Offline execution and process resource evidence using the standard library."""
from __future__ import annotations

import contextlib
import os
import socket
import sys
from pathlib import Path
from unittest.mock import patch


@contextlib.contextmanager
def offline():
    def denied(*args, **kwargs):
        raise RuntimeError("Network access is disabled during offline execution")
    with patch.object(socket.socket, "connect", denied), patch.object(socket.socket, "connect_ex", denied), patch.object(socket, "create_connection", denied):
        yield


def peak_memory() -> int:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        current_process = ctypes.windll.kernel32.GetCurrentProcess
        current_process.restype = wintypes.HANDLE
        memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        memory_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        memory_info.restype = wintypes.BOOL
        if not memory_info(current_process(), ctypes.byref(counters), counters.cb):
            raise OSError("Cannot measure process peak memory")
        return counters.PeakWorkingSetSize
    import resource
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def is_kaggle() -> bool:
    return Path("/kaggle/working").is_dir() and bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE"))
