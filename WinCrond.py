#-*- encoding:utf-8 -*-

import win32service
import win32serviceutil
import win32event
import win32evtlogutil
import win32traceutil
import servicemanager
import winerror
import time
import sys
import os

class WinSerivce(win32serviceutil.ServiceFramework):
    _svc_name_ = "WinCrond"
    _svc_display_name_ = "Windows Crond"
    #_svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop=win32event.CreateEvent(None, 0, 0, None)
        self.isAlive=True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # set the event to call
        win32event.SetEvent(self.hWaitStop)
        self.isAlive=False

    def SvcDoRun(self):
        import servicemanager
        from  Worker import App
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))
        #启动应用
        app = App()
        app.start()
        self.timeout=1000  # In milliseconds (update every second)

        while self.isAlive:
            # wait for service stop signal, if timeout, loop again
            rc=win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            app.refresh()
        
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STOPPED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        return

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(WinSerivce)
            servicemanager.Initialize('WinSerivce', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(WinSerivce)