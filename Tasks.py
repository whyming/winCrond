#-*- encoding:utf-8 -*-

import threading
import time
import subprocess
import signal
import os
from ProcessList import ProcessList
from ServiceLog import getLogger

class Task(threading.Thread):
    def __init__(self,command,name=None,timeout=3600):
        #super(threading.Thread,self).__init__()
        threading.Thread.__init__(self)
        self.setName(name)
        self.command = command
        self.timeout = timeout
        #self.Logger = getLogger()
    def run(self):
        #self.Logger.info("start thread,command name:"+self.command)
        self.start_time = time.time()
        c = Command(self.command,self.timeout)
        c.run()

class Command(object):
    def __init__(self,command,timeout=3600):
        self.command = command
        self.timeout = timeout
        #self.Logger = getLogger()
        #self.Logger.info("Get Command,Read to run:"+command)
    def run(self):
        p = subprocess.Popen(self.command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        #self.Logger.info("run command: "+self.command)
        begin_time = time.time()
        time_passed = 0
        while True:
            if p.poll() is not None:  
                break
            time_passed = time.time() - begin_time
            if self.timeout and time_passed >= self.timeout:
                #self.Logger.warn('comamnd timeout,kill command: '+self.command)
                self.killChildProcesses(p.pid)
                p.terminate()
            time.sleep(0.1)

    def killChildProcesses(self,parent_pid=None):
        p = ProcessList()
        child_pid = p.getChildren(parent_pid)
        for pid in child_pid:
            os.kill(pid, signal.SIGTERM)
