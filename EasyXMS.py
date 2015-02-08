#!/usr/bin/env python
# coding=utf-8

#-------------------------------------------------------------------------------
# Name:         EasyXMS
# Purpose:      Multithreading Batch Execution Commands and Upload Files
# Version:      1.0
# Author:       LEO
# BLOG:         http://linux5588.blog.51cto.com
# EMAIL:        chanyipiaomiao@163.com
# Created:      2013-7-29
# Copyright:    (c) LEO 2013
#-------------------------------------------------------------------------------

from base64 import encodestring,decodestring
from os.path import basename,exists,isfile
from sys import exit,platform
from time import strftime
from Queue import Queue
from os import system
import threading
import paramiko


# 控制输出类
class PrintHelp(object):

    def __init__(self):
        """定义命令列表"""
        self.cmd_list = [' Add      Server ',
                         ' Load     File',
                         ' List     Servers ',
                         ' Delete   Server ',
                         ' Empty    File',
                         ' Execute  Command ',
                         ' Upload   File ',
                         ' Clear    Screen',
                         ]
        self.name = 'EasyXMS'
        self.example = '*** Example *** : '
        self.example_ip = '%s192.168.1.1:22:root:123456 192.168.1.3:test:123456 ' % self.example
        self.example_delete = '%s192.168.1.1 192.168.1.2 ' % self.example
        self.example_filepath = '%s: /tmp/1.txt /tmp' % self.example

    def printPrompt(self):
        """脚本运行提示符"""
        return "%s( ? Help ) >>> " % self.name

    def loopPrintCmd(self):
        """循环打印命令列表"""
        print
        print "Please Choose A Number : "
        print
        for i, v in enumerate(self.cmd_list):
            print "%5s %-5s" % (i, v)
        print

    def printHead(self):
        """输出头部提示信息"""
        print_string = 'Welcome to Use < %s > , Please Input < ? > ' \
                       'Get Help Or Direct < Enter > Exit' % self.name
        string_temp = "-" * len(print_string)
        print string_temp
        print
        print print_string
        print
        print string_temp
        print

    def wantQuit(self):
        """退出提示"""
        return "Want Quit? (y/n) [y|Enter]: "

    def printInputWrong(self):
        """提示命令输入有误"""
        print
        print "Wrong Input,Enter < ? > Get Help Or Enter Exit ! "
        print

    def printFileError(self, e):
        """提示读取主机配置文件出错"""
        print "Oops! Read File Occur Wrong : %s" % e

    def printFileNotExistOrEmpty(self):
        """提示主机配置文件不存在或者为空，请创建或者添加IP地址到文件"""
        print
        print "The File [ %s ] Not Exist Or Empty," \
              " Enter < 0/1 > to Create Or Add Server IP." % configfile
        print

    def printInvalidIP(self,info):
        """提示无效的信息"""
        print "Invalid Format [ %s ] !!! " % info
        print

    def printIPFormat(self):
        """添加服务器IP地址的格式"""
        print
        print self.example_ip

    def printDeleteIPFormat(self):
        """删除服务器IP时的格式"""
        print
        print self.example_delete
        print

    def printInputIP(self):
        """提示输入IP地址以空格分开"""
        return "Enter Server Info : "

    def printInputIPForDelete(self):
        """提示输入服务器的IP地址"""
        return "Enter Server IP (Only IP Address) : "

    def printAddIPSuccessful(self, ip):
        """提示增加服务器IP到配置文件成功"""
        print "Add Server [ %s ] to [ %s ] Successful !!! " % (ip, configfile)
        print

    def printRemoveIPSuccessful(self,ip):
        """提示从配置文件中删除IP地址成功"""
        print "Remove [ %s ] From [ %s ] Successful !!!" % (ip,configfile)
        print

    def printIPNotInFile(self, ip):
        """输出IP地址不在配置文件中"""
        print "%s is Not in [ %s ]" % (ip, configfile)
        print

    def printIPAlreadyInFile(self, ip):
        """输出IP地址已经在配置文件中"""
        print "IP [ %s ] Already in [ %s ] !!!" % (ip, configfile)
        print

    def youSureEmptyFile(self):
        """提示用户是否确认清空文件"""
        return "Are You Sure Empty [ %s ] (y/n) : " % configfile

    def emptySuccessful(self):
        """输出清空文件成功"""
        print "Empty Config File [ %s ] Successful !!!" % configfile
        print

    def emptyFileFailure(self, e):
        """输出清空文件失败"""
        print "Empyt File %s Failure !!! ( %s )" % (configfile, e)

    def enterCommand(self):
        """提示输入命令"""
        return "Enter Command( q|Q Quit ) : "

    def enterFilePath(self):
        """提示输入文件的路径"""
        return "Enter [ Local ] Path And < Remote > Path : "

    def enterFilePath2(self):
        """加载文件时，提示输入文件路径"""
        return "Enter File Path( File Include ip:username:password ) : "

    def invaildCommand(self):
        """输出无效的命令"""
        print "Invaild Command !!!"
        print

    def invaildFilePath(self,filepath):
        """无效的文件路径"""
        print "Invaild File Path ' %s ' !!!" % filepath
        print

    def printSSHBePatient(self):
        """输出正在初始化SSH连接，请耐心等待"""
        print "Initializing < SSH > Connections, Please Be Patient ..."
        print

    def printSFTPBePatient(self):
        """输出正在初始化SFTP连接，请耐心等待"""
        print "Initializing < SFTP > Connections, Please Be Patient ..."
        print

    def printCommandResult(self,ip,cmd,out,error):
        """输出命令执行的结果"""
        result = "======== [ %s ] Execute Command: ' %s ',The Result is : \n\n%s%s" % (ip,cmd,out,error)
        print result
        return result

    def printCanNotConnectIP(self,ip):
        """输出不能连接到该IP地址"""
        print "[ Error ] ... Can't Connect This IP ' %s ', Please Check !!!" % ip
        print

    def uploadFileOK(self, src, ip):
        """上传文件成功"""
        print "Upload File < %s > to %s ... OK " % (src, ip)
        print

    def uploadFileError(self, src, ip, e):
        """上传文件出现错误"""
        print "Upload File < %s > to %s ... Error: %s " % (src, ip, e)
        print

    def printFilePath(self):
        """输出上传文件时路径的例子"""
        print
        print self.example_filepath

    def printArgsNotenough(self):
        """输出参数不够提示"""
        print "Arguments Not Enough !!!"
        print

    def getDateTime(self):
        """获取日期和时间"""
        return strftime('%Y-%m-%d %H:%M:%S')

    def returnDateString(self):
        """返回一个日期加星号的字符串用于标识命令执行的结果"""
        return '\n********** %s **********\n\n' % self.getDateTime()

    def printCannotCreateFile(self,filename,error):
        """提示无法创建文件"""
        print
        print "Can't Create < %s > !!! : %s" % (filename, error)
        print


# 控制输入类
class InputValue(object):


    def __init__(self):
        self.inputValue = None


    def setInputvalue(self):
        """提示输入命令"""
        self.inputValue = raw_input(printhelp_obj.printPrompt())
        return self.inputValue


    def closeConnections(self):
        """关闭连接函数"""
        ssh_connect_pool_dict = connectSSH_obj.getConnectionPool()
        sftp_connect_pool_dict = connectSFTP_obj.getConnectionPool()
        if ssh_connect_pool_dict:
            for i in ssh_connect_pool_dict:
                ssh_connect_pool_dict[i].close()
        if sftp_connect_pool_dict:
            for j in sftp_connect_pool_dict:
                sftp_connect_pool_dict[j].close()


    def exitFunction(self):
        """退出本程序"""
        try:
            print
            quitp = raw_input(printhelp_obj.wantQuit())
            print
        except EOFError:
            self.closeConnections()
            print
            print
            exit(0)
        if not quitp or quitp == 'y' or quitp == 'Y':
            self.closeConnections()
            exit(0)
        else:
            self.loopGetValue()


    def loopGetValue(self):
        """循环得到用户的输入，并判断"""
        try:
            while self.setInputvalue():
                if self.inputValue == '?':
                    printhelp_obj.loopPrintCmd()
                elif self.inputValue == '0':
                    readwriteconfigFile_obj.writeIPToFile()
                elif self.inputValue == '1':
                    readwriteconfigFile_obj.loadFile()
                elif self.inputValue == '2':
                    readwriteconfigFile_obj.readIPFromFile()
                elif self.inputValue == '3':
                    readwriteconfigFile_obj.deleteIPFromFile()
                elif self.inputValue == '4':
                    readwriteconfigFile_obj.emptyConfigFile()
                elif self.inputValue == '5':
                    startExecAction_obj.startExecCommand()
                elif self.inputValue == '6':
                    startExecAction_obj.startSFTP()
                elif self.inputValue == '7':
                    startExecAction_obj.clearScreen()
                else:
                    printhelp_obj.printInputWrong()
            else:
                self.exitFunction()
        except EOFError :
            print
            self.exitFunction()
        except KeyboardInterrupt:
            print
            self.exitFunction()


# 操作配置文件类
class ReadWriteConfigFile(object):


    def readIPAsDict(self):
        """读取所有的IP地址为一个字典
        像这样: {'192.168.1.1':{'port':22,'user':root,'pwd':123456}, }
        """
        ip_dict = {}
        try:
            data = open(configfile,'r')
            config_file = data.readlines()
            if config_file:
                for i in config_file:
                    i = decodestring(i)
                    tempstring = i.split(':')
                    ip = tempstring[0]
                    if ip not in ip_dict:
                        ip_dict[ip] = {'port':int(tempstring[1]),
                                       'user':tempstring[2],
                                       'pwd':tempstring[3]}
        except:
            pass

        # 如果文件句柄被打开过，则关闭
        try:
            data.close()
        except:
            pass

        return ip_dict


    def readIPFromFile(self):
        """返回一个IP地址列表"""
        ip_list = self.readIPAsDict().keys()
        if ip_list:
            print
            for i in ip_list:
                print i
            print
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def fileAppendObject(self,filename):
        """以追加方式打开文件并返回对象"""
        data = None
        error = None
        try:
            data = open(filename,'a')
        except IOError,e:
            error = e
        return data,error


    def writeFile(self,data,server_list):
        """写文件函数，用于写服务器的配置信息"""
        ip_list = self.readIPAsDict().keys()
        for ip_info in server_list:
            ip,info = self.checkIPInfo(ip_info)
            if ip and info:
                if ip not in ip_list:
                    data.write(encodestring(info))
                    printhelp_obj.printAddIPSuccessful(ip)
                else:
                    printhelp_obj.printIPAlreadyInFile(ip)


    def loadFile(self):
        """加载一个包含 IP地址:端口:用户名:密码 的文件批量进行添加"""
        data2,error = self.fileAppendObject(configfile)
        if data2:
            print
            filename = raw_input(printhelp_obj.enterFilePath2())
            print
            if filename:
                try:
                    data = open(filename,'r')
                    file_ip_list = data.readlines()
                    data.close()
                    self.writeFile(data2, file_ip_list)
                except IOError,e:
                    printhelp_obj.printFileError(e)
                    print
                data2.close()
            else:
                printhelp_obj.printArgsNotenough()
        else:
            printhelp_obj.printCannotCreateFile(configfile,error)


    def checkIPInfo(self,ipinfo):
        """简单的检查输入的IP等信息格式是否正确"""
        ip,info = None,None
        maohao_num = ipinfo.count(':')
        if maohao_num in (2,3):
            if ipinfo.count('.') == 3:
                info_list = ipinfo.split(':')
                if maohao_num == 3:
                    ip, port, user, passwd = info_list
                if maohao_num == 2:
                    ip, user, passwd = info_list
                    port = 22
                if passwd:
                    info = '%s:%s:%s:%s' % (ip, port, user, passwd)
                else:
                    printhelp_obj.printInvalidIP(ipinfo)
            else:
                printhelp_obj.printInvalidIP(ipinfo)
        else:
            printhelp_obj.printInvalidIP(ipinfo)

        return ip,info


    def writeIPToFile(self):
        """写入IP地址到配置文件"""
        data,error = self.fileAppendObject(configfile)
        if data:
            printhelp_obj.printIPFormat()
            print
            hosts = raw_input(printhelp_obj.printInputIP())
            print
            if not hosts:
                printhelp_obj.printArgsNotenough()
            else:
                server_list = hosts.split()
                self.writeFile(data,server_list)
            data.close()
        else:
            printhelp_obj.printCannotCreateFile(configfile, error)


    def deleteIPFromFile(self):
        """从配置文件中删除指定的IP地址"""
        ip_from_configfile_dict = self.readIPAsDict()
        if ip_from_configfile_dict:
            printhelp_obj.printDeleteIPFormat()
            hosts = raw_input(printhelp_obj.printInputIPForDelete())
            print
            if len(hosts) == 0:
                printhelp_obj.printArgsNotenough()
            else:
                delete_ip_list = hosts.split()
                for i in delete_ip_list:
                    if i in ip_from_configfile_dict:
                        del ip_from_configfile_dict[i]
                        printhelp_obj.printRemoveIPSuccessful(i)
                    else:
                        printhelp_obj.printIPNotInFile(i)
                if ip_from_configfile_dict:
                    try:
                        data = open(configfile, 'w')
                        for key,value in ip_from_configfile_dict.items():
                            tempstring = "%s:%s:%s:%s" % (key, value['port'], value['user'], value['pwd'])
                            data.write(encodestring(tempstring))
                    except IOError, e:
                        print
                        printhelp_obj.printFileError(e)
                        print
                else:
                    data = open(configfile, 'w')
                try:
                    data.close()
                except:
                    pass
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def emptyConfigFile(self):
        """清空整个主机配置文件"""
        if self.readIPAsDict():
            print
            ok = raw_input(printhelp_obj.youSureEmptyFile())
            print
            if ok == 'y' or ok == 'Y':
                try:
                    data = open(configfile, 'w')
                except IOError,e:
                    printhelp_obj.emptyFileFailure(e)

                # 如果文件句柄被打开过，则关闭
                try:
                    data.close()
                    printhelp_obj.emptySuccessful()
                except:
                    pass
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def readCommandHistory(self):
        """读取历史执行命令"""
        command_history_list = []
        try:
            data = open(command_history,'r')
            for cmd in data.readlines():
                command_history_list.append(cmd.strip('\n'))
            data.close()
        except IOError:
            pass
        return command_history_list


    def writeCommandToFile(self,cmd):
        """命令写入到文件"""
        command_history_list = self.readCommandHistory()
        data,error = self.fileAppendObject(command_history)
        if data:
            if cmd not in command_history_list:
                data.write(cmd+'\n')
            data.close()
        else:
            printhelp_obj.printCannotCreateFile(command_history, error)


    def writeCommandResultToFile(self, result_list):
        """命令输出结果写入到文件"""
        data,error = self.fileAppendObject(command_result_history)
        if data:
            data.write(printhelp_obj.returnDateString())
            data.write(''.join(result_list))
            data.write('\n')
            data.close()
        else:
            printhelp_obj.printCannotCreateFile(command_result_history,error)


# 连接SSH和SFTP类的父类
class Connect(object):

    def __init__(self):
        self.connect_pool_dict = {}     # 用于存放连接到各个服务器的连接对象
        self.ip_list = []               # SSH/SFTP 连接成功的IP地址列表
        self.thread_num = None

    def getIPList(self):
        """获取SSH/SFTP连接成功的IP地址"""
        return self.ip_list

    def getThreadNum(self):
        """获取到线程数量，是通过计算IP地址数量得到"""
        return self.thread_num

    def getConnectionPool(self):
        """获取SFTP/SSH连接池信息"""
        return self.connect_pool_dict


# 连接SSH类
class ConnectSSH(Connect):


    def connectSSH(self):
        """连接到SSH服务"""
        paramiko.util.log_to_file(EasyXMS_log)
        server_dict = readwriteconfigFile_obj.readIPAsDict() # 首先获得ServerIP地址列表
        if server_dict:
            # 这一段就是判断，在ssh的connect_pool_dict这里面现存的IP地址列表跟从配置文件读取出来的列表是否一致
            # 如果不一致，那么以配置文件读取出来的IP地址列表为准，删除多余的连接
            if self.connect_pool_dict:
                connect_pool_list = self.connect_pool_dict.keys()
                for i in connect_pool_list:
                    if i not in server_dict:
                        del self.connect_pool_dict[i]
                        self.ip_list.remove(i)

            # 这一段是增加 成功进行SSH连接的IP地址到self.connect_pool_dict中去，同时也增加到成功IP地址列表去
            for ip,value in server_dict.items():
                if ip not in self.connect_pool_dict:
                    conn = paramiko.SSHClient()
                    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        conn.connect(ip,value['port'],value['user'],value['pwd'], timeout=0.8)
                        self.connect_pool_dict[ip] = conn
                        self.ip_list.append(ip)
                    except:
                        printhelp_obj.printCanNotConnectIP(ip)
            self.thread_num = len(self.ip_list)
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def setCommand(self,command):
        """设定命令行输入的命令"""
        self.command = command


    def getCommand(self):
        """返回命令"""
        return self.command


# 连接到SFTP类
class ConnectSFTP(Connect):


    def connectSFTP(self):
        """连接到SFTP服务"""
        paramiko.util.log_to_file(EasyXMS_log)
        server_dict = readwriteconfigFile_obj.readIPAsDict() # 首先获得ServerIP地址列表
        if server_dict:
            # 这一段就是判断，在sftp的connect_pool_dict这里面现存的IP地址列表跟从配置文件读取出来的列表是否一致
            # 如果不一致，那么以配置文件读取出来的IP地址列表为准，删除多余的连接
            if self.connect_pool_dict:
                connect_pool_list = self.connect_pool_dict.keys()
                for i in connect_pool_list:
                    if i not in server_dict:
                        del self.connect_pool_dict[i]
                        self.ip_list.remove(i)

            # 这一段是增加 成功进行SFTP连接的IP地址到self.connect_pool_dict中去，同时也增加到成功IP地址列表去
            for ip,value in server_dict.items():
                if ip not in self.connect_pool_dict:
                    try:
                        conn = paramiko.Transport((ip, value['port']))
                        conn.connect(username=value['user'], password=value['pwd'])
                        sftp = paramiko.SFTPClient.from_transport(conn)
                        self.connect_pool_dict[ip] = sftp
                        self.ip_list.append(ip)
                    except:
                        printhelp_obj.printCanNotConnectIP(ip)
            self.thread_num = len(self.ip_list)
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def getDirectoryName(self, filename, dest):
        """拼接目标文件名"""
        if dest.endswith('/'):
            dest = '%s/%s' % (dest.rstrip('/'), filename)
        else:
            dest = '%s/%s' % (dest, filename)

        return dest


    def setFilePath(self,filepath):
        """设定当前命令行输入的文件路径"""
        self.filepath = filepath


    def getFilePath(self):
        """返回命令行输入的文件路径"""
        return self.filepath


# 多线程类
class MutilThreadControl(threading.Thread):


    def setConnectionPool(self, pool):
        """设置使用那个连接池 有SSH和SFTP连接池"""
        self.init_pool = pool


    def initIPQueueAndtConnectionPool(self):
        """初始一个队列并把IP地址放入队列，返回IP地址列表的长度（指定产生线程的数量）和队列"""
        if self.init_pool == 'ssh':
            ip_list = connectSSH_obj.getIPList()
            connect_pool_dict = connectSSH_obj.getConnectionPool()
        elif self.init_pool == 'sftp':
            ip_list = connectSFTP_obj.getIPList()
            connect_pool_dict = connectSFTP_obj.getConnectionPool()
        thread_num = len(ip_list)
        ip_queue = Queue(thread_num)
        for ip in ip_list:
            ip_queue.put(ip)
        return ip_queue, thread_num, connect_pool_dict


    def run(self):
        """开始多线程执行命令和SFTP上传文件"""
        ip_queue, threads_num, connect_pool_dict = self.initIPQueueAndtConnectionPool()
        result_list = []
        if self.init_pool == 'ssh':
            cmd = connectSSH_obj.getCommand()
            for i in xrange(threads_num):
                ip = ip_queue.get()
                stdin,stdout,stderr = connect_pool_dict[ip].exec_command(cmd)
                result = printhelp_obj.printCommandResult(ip, cmd, stdout.read(), stderr.read())
                result_list.append(result)
            readwriteconfigFile_obj.writeCommandResultToFile(result_list)
        elif self.init_pool == 'sftp':
            file_path = connectSFTP_obj.getFilePath().split()
            if len(file_path) == 2:
                src,dest = file_path
                if exists(src) and isfile(src):
                    filename = basename(src)
                    dest = connectSFTP_obj.getDirectoryName(filename, dest)
                    for i in xrange(threads_num):
                        ip = ip_queue.get()
                        try:
                            connect_pool_dict[ip].put(src, dest)
                            printhelp_obj.uploadFileOK(src, ip)
                        except IOError, e:
                            printhelp_obj.uploadFileError(src, ip, e)
                else:
                    printhelp_obj.invaildFilePath(src)
            else:
                printhelp_obj.printArgsNotenough()


# 执行指定的动作（执行命令 上传文件 清屏）
class StartExecAction(object):


    def startExecCommand(self):
        """开始多线程执行命令"""
        mutilThreadControl_ssh_obj = MutilThreadControl()
        mutilThreadControl_ssh_obj.setConnectionPool('ssh')         # 设定连接池为ssh的连接池
        if readwriteconfigFile_obj.readIPAsDict():
            print
            cmd = raw_input(printhelp_obj.enterCommand())
            print
            if cmd:
                if cmd == 'q' or cmd == 'Q':
                    pass
                else:
                    readwriteconfigFile_obj.writeCommandToFile(cmd)
                    connectSSH_obj.setCommand(cmd)                      # 获取命令行输入的命令，以备多线程类使用
                    if not connectSSH_obj.getConnectionPool():         # 如果SSH连接池为空则初始化连接池
                        printhelp_obj.printSSHBePatient()               # 输出 耐心等待
                    connectSSH_obj.connectSSH()                         # 初始化SSH连接池
                    mutilThreadControl_ssh_obj.start()                  # 多线程开始执行
                    mutilThreadControl_ssh_obj.join()                   # 等待各个线程都执行完毕
                    self.startExecCommand()                             # 调用该方法自身，不退出命令执行，好继续执行命令
            else:
                printhelp_obj.invaildCommand()
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def startSFTP(self):
        """开始上传文件"""
        mutilThreadControl_sftp_obj = MutilThreadControl()
        mutilThreadControl_sftp_obj.setConnectionPool('sftp')           # 设定连接池为sftp的连接池
        if readwriteconfigFile_obj.readIPAsDict():
            printhelp_obj.printFilePath()
            print
            filepath = raw_input(printhelp_obj.enterFilePath())
            print
            if filepath:
                connectSFTP_obj.setFilePath(filepath)                   # 获取命令行输入的文件路径，以备多线程类使用
                if not connectSFTP_obj.getConnectionPool():            # 如果SFTP连接池为空则初始化连接池
                    printhelp_obj.printSFTPBePatient()                  # 输出 耐心等待
                connectSFTP_obj.connectSFTP()                           # 初始化SFTP连接池
                mutilThreadControl_sftp_obj.start()                     # 多线程开始执行
                mutilThreadControl_sftp_obj.join()                      # 等待各个线程都执行完毕
            else:
                printhelp_obj.printArgsNotenough()
        else:
            printhelp_obj.printFileNotExistOrEmpty()


    def clearScreen(self):
        """清屏"""
        clear_screen = {'win32':'cls','linux2':'clear',
                        'linux':'clear','darwin':'clear'}[platform]
        system(clear_screen)



if __name__ == '__main__':
    configfile = 'server.conf'                                 # 指定服务器IP地址配置文件
    EasyXMS_log = 'paramiko.log'                               # 指定使用paramiko时，产生的日志文件
    command_history = 'command_history.log'                   # 命令历史记录
    command_result_history = 'command_result_history.log'    # 命令执行结果的历史记录
    printhelp_obj = PrintHelp()                                 # 初始化一个打印帮助对象
    printhelp_obj.printHead()                                   # 输出头部信息
    readwriteconfigFile_obj = ReadWriteConfigFile()             # 初始化一个读写配置文件的对象
    connectSSH_obj = ConnectSSH()                               # 初始化一个SSH类对象
    connectSFTP_obj = ConnectSFTP()                             # 初始化一个SFTP对象
    startExecAction_obj = StartExecAction()                     # 初始化一个 开始执行动作对象
    input_obj = InputValue()                                    # 初始化一个输入类对象
    input_obj.loopGetValue()                                    # 调用方法循环得到输入