#-*- encoding:utf-8 -*-
import configparser
import time
import os
import sys
from Tasks import Task
from  ServiceLog import getLogger
class Config(object):
    '''
        读取配置文件，返回一个任务列表
        默认使用ini配置文件，如果使用类似与crond的配置文件需要重写读取部分
    '''
    def __init__(self):
        self.file = None
        self.config_file = 'config.ini'
        if os.path.basename(sys.executable) == "python.exe":
            current_path = os.getcwd()
        else:
            current_path = os.path.dirname(sys.executable)
        config_file = os.path.join(current_path,self.config_file)
        self.Logger = getLogger()
        self.Logger.info("config file is:"+config_file)
        if os.path.isfile(config_file):
            self.file = config_file

    def getConfig(self):
        if self.file is None:
            return None
        all_config = configparser.RawConfigParser()
        all_config.read(self.file)
        workers = {}
        for section in all_config.sections():
            if all_config.has_option(section,'interval') and \
                all_config.has_option(section,'command'):
                interval = all_config.get(section,'interval')
                command = all_config.get(section,'command')
            else:
                continue
            if all_config.has_option(section,'timeout'):
                timeout = all_config.get(section,'timeout')
            else:
                timeout = 3600

            workers[section] = {
                'interval':int(eval(interval)),
                'command':command,
                'timeout':int(eval(timeout))
            }
        if not workers:
            self.Logger.error("Read config Fail!")
        return workers

class App(object):
    '''
        service真正执行的任务就是这个类
        这个类会根据配置创建多个进程
        进程结束后回收和是否需要创建新的进程

    '''
    def __init__(self):
        c = Config()
        tasks = c.getConfig()
        for name in tasks.keys():
            tasks[name]['thread'] = None
            tasks[name]['start'] = 0
        self.tasks = tasks
        self.Logger = getLogger()
        #初始化所有子线程
    def start(self):
        for task_name in self.tasks:
            self.__start(task_name)

    def stop(self,name = None):
        if self.tasks is not None:
            for task_name in self.tasks:
                self.__stop(task_name)
    def __start(self,name):
        if name in self.tasks:
            task = self.tasks[name]
            if task['thread'] == None or \
                ( task['thread'] != None and  not task['thread'].isAlive() ):
                del self.tasks[name]['thread']
                self.tasks[name]['thread'] = Task(self.tasks[name]['command'],timeout = self.tasks[name]['timeout'])
                self.tasks[name]['start'] = time.time()
                self.tasks[name]['thread'].start()
                self.Logger.info('start task '+name+" command is: "+task['command'])
            else:
                self.Logger.error('Cannot start task,there is no task named '+name)
    def __stop(self,name):
        pass
    def refresh(self):
        tasks = self.tasks
        for name in tasks.keys():
            if time.time() - tasks[name]['start'] > tasks[name]['interval'] and \
                not tasks[name]['thread'].isAlive():
                #上一次的进程已经结束了
                #距离上次开始执行已经超过了时间，可以开始下次执行
                self.__start(name)