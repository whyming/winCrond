#-*- encoding:utf-8 -*-
import ctypes;

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",ctypes.c_ulong),
        ("cntUsage",ctypes.c_ulong),
        ("th32ProcessID",ctypes.c_ulong),
        ("th32DefaultHeapID",ctypes.c_void_p),
        ("th32ModuleID",ctypes.c_ulong),
        ("cntThreads",ctypes.c_ulong),
        ("th32ParentProcessID",ctypes.c_ulong),
        ("pcPriClassBase",ctypes.c_long),
        ("dwFlags",ctypes.c_ulong),
        ("szExeFile",ctypes.c_char*260)
    ]
class ProcessList(object):
    def __init__(self):
        self.kernel32 = ctypes.windll.LoadLibrary("kernel32.dll");
        self.handle = self.kernel32.CreateToolhelp32Snapshot(0x2,0x0);
        self.process_list = []
    def getProcessList(self):
        process_list = []
        if self.handle != -1:
            proc = PROCESSENTRY32()
            proc.dwSize = ctypes.sizeof(proc)
            while self.kernel32.Process32Next(self.handle,ctypes.byref(proc)):
                process_list.append({'pid':int(proc.th32ProcessID),'ppid':int(proc.th32ParentProcessID)})
                #print("ProcessName : %s - ProcessID : %d"%(ctypes.string_at(proc.szExeFile),proc.th32ProcessID));
        self.kernel32.CloseHandle(self.handle);
        return process_list

    def getChildren(self,ppid=None):
        children = []
        if ppid is None or not ppid:
            return children
        
        if not self.process_list:
            self.process_list = self.getProcessList()
        for p in self.process_list:
            if p['ppid'] == ppid:
                children.append(p['pid'])
                children += self.getChildren(p['pid'])
        return children