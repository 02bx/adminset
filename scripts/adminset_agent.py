#!/usr/bin/python
# coding=utf-8

import os
from subprocess import Popen, PIPE
import re
import urllib
import urllib2
import platform
import socket
import psutil
import time
import schedule
import redis
import json

token = 'HPcWR7l4NJNJ'
server_url = 'http://192.168.47.130/cmdb/collect'


def get_ip():
    hostname = socket.getfqdn(socket.gethostname())
    ipaddr = socket.gethostbyname(hostname)
    return ipaddr


def get_dmi():
    p = Popen('dmidecode', stdout=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


def parser_dmi(dmidata):
    pd = {}
    line_in = False
    for line in dmidata.split('\n'):
        if line.startswith('System Information'):
             line_in = True
             continue
        if line.startswith('\t') and line_in:
                 k,v = [i.strip() for i in line.split(':')]
                 pd[k] = v
        else:
            line_in = False
    return pd


def get_mem_total():
    cmd = "grep MemTotal /proc/meminfo"
    p = Popen(cmd, stdout=PIPE, shell = True)
    data = p.communicate()[0]
    mem_total = data.split()[1]
    memtotal = int(round(int(mem_total)/1024.0/1024.0, 0))
    return memtotal


def get_cpu_model():
    cmd = "cat /proc/cpuinfo"
    p = Popen(cmd, stdout=PIPE, stderr = PIPE, shell = True)
    stdout, stderr = p.communicate()
    return stdout


def get_cpu_cores():
    cpu_cores = {"logical": psutil.cpu_count(logical=False), "physical": psutil.cpu_count()}
    return cpu_cores


def parser_cpu(stdout):
    groups = [i for i in stdout.split('\n\n')]
    group = groups[-2]
    cpu_list = [i for i in group.split('\n')]
    cpu_info = {}
    for x in cpu_list:
        k, v = [i.strip() for i in x.split(':')]
        cpu_info[k] = v
    return cpu_info


def get_disk_info():
    ret = {}
    disk_dev = re.compile(r'Disk\s/dev/sd[a-z]{1}')
    disk_name = re.compile(r'/dev/sd[a-z]{1}')
    pcmd = Popen(['fdisk', '-l'], shell=False,stdout=PIPE)
    stdout, stderr = pcmd.communicate()
    for i in stdout.split('\n'):
        disk = re.match(disk_dev,i)
        if disk:
            dk = re.search(disk_name, disk.group()).group()
            n = Popen('smartctl -i %s' % dk, shell=True, stdout=PIPE)
            p = n.communicate()
            ret[dk] = p
    return ret


def parser_disk_info(diskdata):
    pd = {}
    disknum = diskdata.keys()
    user_capacity = re.compile(r'(User Capacity):(\s+[\d,]{1,50})')
    for num in disknum:
        t = str(diskdata[num])
        for line in t.split('\n'):
            user = re.search(user_capacity, line)
            if user:
                diskvo = user.groups()[1].strip()
                nums = int(diskvo.replace(',', ''))
                endnum = str(nums/1000/1000/1000)
                pd[num] = endnum
    return pd


def post_data(data):
    postdata = urllib.urlencode(data)
    req = urllib2.urlopen(server_url, postdata)
    req.read()
    return True


def asset_info():
    data_info = dict()
    data_info['memory'] = get_mem_total()
    data_info['disk'] = parser_disk_info(get_disk_info())
    cpuinfo = parser_cpu(get_cpu_model())
    cpucore = get_cpu_cores()
    data_info['cpu_num'] = cpucore['logical']
    data_info['cpu_physical'] = cpucore['physical']
    data_info['cpu_model'] = cpuinfo['model name']
    data_info['ip'] = get_ip()
    data_info['sn'] = parser_dmi(get_dmi())['Serial Number']
    data_info['vendor'] = parser_dmi(get_dmi())['Manufacturer']
    data_info['product'] = parser_dmi(get_dmi())['Version']
    data_info['osver'] = platform.linux_distribution()[0] + " " + platform.linux_distribution()[1] + " " + platform.machine()
    data_info['hostname'] = platform.node()
    data_info['token'] = token
    return data_info


def asset_info_post():
    osenv = os.environ["LANG"]
    os.environ["LANG"] = "us_EN.UTF8"
    os.environ["LANG"] = osenv
    print 'Get the hardwave infos from host:'
    print asset_info()
    print '----------------------------------------------------------'
    post_data(asset_info())
    print 'Post the hardwave infos to CMDB successfully!'


def get_sys_cpu():
    sys_cpu = {}
    cpu_time = psutil.cpu_times_percent(interval=1)
    sys_cpu['percent'] = psutil.cpu_percent(interval=1)
    sys_cpu['lcpu_percent'] = psutil.cpu_percent(interval=1, percpu=True)
    sys_cpu['user'] = cpu_time.user
    sys_cpu['nice'] = cpu_time.nice
    sys_cpu['system'] = cpu_time.system
    sys_cpu['idle'] = cpu_time.idle
    sys_cpu['iowait'] = cpu_time.iowait
    sys_cpu['irq'] = cpu_time.irq
    sys_cpu['softirq'] = cpu_time.softirq
    sys_cpu['guest'] = cpu_time.guest
    return sys_cpu


def get_sys_mem():
    sys_mem = {}
    mem = psutil.virtual_memory()
    sys_mem["total"] = mem.total/1024/1024
    sys_mem["percent"] = mem.percent
    sys_mem["available"] = mem.available/1024/1024
    sys_mem["used"] = mem.used/1024/1024
    sys_mem["free"] = mem.free/1024/1024
    sys_mem["buffers"] = mem.buffers/1024/1024
    sys_mem["cached"] = mem.cached/1024/1024
    return sys_mem


def parser_sys_disk(mountpoint):
        partitions_list = {}
        d = psutil.disk_usage(mountpoint)
        partitions_list['mountpoint'] = mountpoint
        partitions_list['total'] = round(d.total/1024/1024/1024.0, 2)
        partitions_list['free'] = round(d.free/1024/1024/1024.0, 2)
        partitions_list['used'] = round(d.used/1024/1024/1024.0, 2)
        partitions_list['percent'] = d.percent
        return partitions_list


def get_sys_disk():
    sys_disk = {}
    partition_info = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        partition_info.append(parser_sys_disk(p.mountpoint))
    sys_disk = partition_info
    return sys_disk


def agg_sys_info():
    sys_info = dict()
    sys_info['hostname'] = platform.node()
    sys_info['timestamp'] = int(time.time())
    sys_info['cpu'] = get_sys_cpu()
    sys_info['mem'] = get_sys_mem()
    sys_info['disk'] = get_sys_disk()
    return json.dumps(sys_info)


if __name__ == "__main__":
    asset_info_post()
    schedule.every(10).seconds.do(asset_info_post)
    while True:
        schedule.run_pending()
        time.sleep(1)
