"""Windows held-process identity and read-only owner inventory.

No process access on import. The held handle survives PID reuse. Launch policy
belongs to the adapter; this module never kills or attaches instrumentation.
"""
import ctypes
import json
import os
import subprocess
from ctypes import wintypes


def native_inventory(*, allowed=()):
    # Refuse an idle research/observer worker too, even if Civ has not launched.
    code = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match "
            "'^(CivilizationVI|FireTuner)' -or ($_.Name -match '^python(w)?[.]exe$' "
            "-and $_.CommandLine -match 'csc-native|trace_daemon|producer-decision|csc-rh5|ai_baseline|ai_tuning|full_game_controller') } "
            "| Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine,CreationDate | ConvertTo-Json -Compress")
    raw = subprocess.check_output(['powershell', '-NoProfile', '-Command', code],
                                  text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
    rows = json.loads(raw) if raw else []
    if isinstance(rows, dict):
        rows = [rows]
    result = []
    for row in rows:
        if row['ProcessId'] == os.getpid():
            continue
        held = HeldProcess(row['ProcessId'])
        try:
            identity = held.identity
        finally:
            held.close()
        if identity not in allowed:
            result.append(dict(row, pid=row['ProcessId'], identity=identity))
    return result


class HeldProcess:
    def __init__(self, pid):
        self.pid = pid
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        k = self.kernel
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.OpenProcess.restype = wintypes.HANDLE
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CloseHandle.restype = wintypes.BOOL
        k.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
        k.GetProcessTimes.restype = wintypes.BOOL
        k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        k.QueryFullProcessImageNameW.restype = wintypes.BOOL
        k.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k.WaitForSingleObject.restype = wintypes.DWORD
        k.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.GetExitCodeProcess.restype = wintypes.BOOL
        self.handle = k.OpenProcess(0x1000 | 0x100000, False, pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            created, ended, kernel, user = (wintypes.FILETIME() for _ in range(4))
            if not k.GetProcessTimes(self.handle, *(ctypes.byref(t) for t in (created, ended, kernel, user))):
                raise ctypes.WinError(ctypes.get_last_error())
            text = ctypes.create_unicode_buffer(32768)
            size = wintypes.DWORD(len(text))
            if not k.QueryFullProcessImageNameW(self.handle, 0, text, ctypes.byref(size)):
                raise ctypes.WinError(ctypes.get_last_error())
            self.identity = dict(pid=pid, executable_path=text.value,
                                 creation_filetime=(created.dwHighDateTime << 32) | created.dwLowDateTime)
        except BaseException:
            self.close()
            raise

    @classmethod
    def from_popen(cls, process):
        # The original Popen handle is the authority. A reopened handle must
        # have exactly the same native creation time and executable identity.
        held = cls(process.pid)
        k = held.kernel
        times = [wintypes.FILETIME() for _ in range(4)]
        if not k.GetProcessTimes(int(process._handle), *(ctypes.byref(t) for t in times)):
            held.close()
            raise ctypes.WinError(ctypes.get_last_error())
        created = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        if created != held.identity['creation_filetime'] or process.poll() is not None:
            held.close()
            raise RuntimeError('Launch process exited or identity changed')
        return held

    def poll(self):
        status = self.kernel.WaitForSingleObject(self.handle, 0)
        if status == 258:  # WAIT_TIMEOUT, process is still running.
            return None
        if status != 0:
            raise ctypes.WinError(ctypes.get_last_error())
        code = wintypes.DWORD()
        if not self.kernel.GetExitCodeProcess(self.handle, ctypes.byref(code)):
            raise ctypes.WinError(ctypes.get_last_error())
        return code.value

    def close(self):
        if self.handle:
            if not self.kernel.CloseHandle(self.handle):
                raise ctypes.WinError(ctypes.get_last_error())
            self.handle = None
