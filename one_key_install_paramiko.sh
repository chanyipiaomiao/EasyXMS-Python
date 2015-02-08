#!/bin/bash

#--------------------------------------------------
# Name:         one_key_install_paramiko
# Purpose:      一键安装paramiko需要的环境
# Version:      1.0
# Author:       LEO
# BLOG:         http://linux5588.blog.51cto.com
# EMAIL:        chanyipiaomiao@163.com
# Created:      2013-09-06
# Copyright:    (c) LEO 2013
#---------------------------------------------------

export PATH=/usr/kerberos/sbin:/usr/kerberos/bin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin

# 检测GCC是否安装
checkGCC(){
	if ! gcc -v &>/dev/null; then
		echo
		echo "GCC not Found! Please use < yum -y install gcc* > "
		echo 
		exit 1
	fi
}

# 安装新版本gmp包
installNewGMP(){
	wget http://ftp.gnu.org/gnu/gmp/gmp-5.1.2.tar.bz2
	tar jxf gmp-5.1.2.tar.bz2
	cd gmp-5.1.2
	./configure && make && make install
	echo "/usr/local/lib" >> /etc/ld.so.conf
	ldconfig
}


# 安装easy_install工具
installEasy_install(){
	if easy_install -h &>/dev/null ;then
		echo
		echo "easy_install already installed"
		echo
	else
		wget http://peak.telecommunity.com/dist/ez_setup.py
		python ez_setup.py
	fi
}

# 安装paramiko模块
installParamiko(){
	easy_install paramiko
}


# 安装Python2.7
installPython27(){
	wget http://www.python.org/ftp/python/2.7.5/Python-2.7.5.tar.bz2
	tar jxf Python-2.7.5.tar.bz2
	cd Python-2.7.5
	./configure --prefix=/usr/local/python2.7
	make && make install
	echo "export PATH=/usr/local/python2.7/bin:$PATH" >> /etc/profile
	source /etc/profile
}


# 检查Python版本是否符合要求
TEMP="tempfile"			
checkPython(){
	python -V 2>${TEMP}
	VERSION=$(awk -F. '{print $2}' ${TEMP})
	rm -f ${TEMP}
	if [[ $VERSION -lt 7 ]]; then
		echo
		echo "Python Version does not meet the requirements，We Will auto download and install."
		echo
		installPython27
		installEasy_install
		installParamiko
	else
		installEasy_install
		installParamiko
	fi
}

# 调用函数检查GCC
checkGCC

# 调用函数安装新版本gmp
installNewGMP

# 调用函数检查Python
checkPython
