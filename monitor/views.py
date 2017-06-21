#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response, redirect, RequestContext, HttpResponse
from cmdb.models import Host
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from pymongo import MongoClient
import json
import time
from config.views import get_dir

TIME_SECTOR = (
            3600,
            3600*3,
            3600*5,
            86400,
            86400*3,
            86400*7,
)


class GetSysData(object):

    def __init__(self, hostname, monitor_item, timing, no=0):
        self.hostname = hostname
        self.monitor_item = monitor_item
        self.timing = timing
        self.no = no

    def get_data(self):
        mongodb_ip = get_dir("mongodb_ip")
        mongodb_port = get_dir("mongodb_port")
        client = MongoClient(mongodb_ip, int(mongodb_port))
        db = client.sys_info
        collection = db[self.hostname]
        now_time = int(time.time())
        find_time = now_time-self.timing
        cursor = collection.find({'timestamp': {'$gte': find_time}}, {self.monitor_item: 1, "timestamp": 1}).limit(self.no)
        return cursor


@login_required()
@permission_verify()
def get_cpu(request, hostname, timing):
    data_time = []
    cpu_percent = []
    range_time = TIME_SECTOR[int(timing)]
    cpu_data = GetSysData(hostname, "cpu", range_time)
    for doc in cpu_data.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        c_percent = doc['cpu']['percent']
        cpu_percent.append(c_percent)
    data = {"data_time": data_time, "cpu_percent": cpu_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def get_mem(request, hostname, timing):
    data_time = []
    mem_percent = []
    range_time = TIME_SECTOR[int(timing)]
    mem_data = GetSysData(hostname, "mem", range_time)
    for doc in mem_data.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        m_percent = doc['mem']['percent']
        mem_percent.append(m_percent)
    data = {"data_time": data_time, "mem_percent": mem_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def get_disk(request, hostname, timing, partition):
    data_time = []
    disk_percent = []
    disk_name = ""
    range_time = TIME_SECTOR[int(timing)]
    disk = GetSysData(hostname, "disk", range_time)
    for doc in disk.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        d_percent = doc['disk'][int(partition)]['percent']
        disk_percent.append(d_percent)
        if not disk_name:
            disk_name = doc['disk'][int(partition)]['mountpoint']
    data = {"data_time": data_time, "disk_name": disk_name, "disk_percent": disk_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def index(request):
    temp_name = "monitor/monitor-header.html"
    all_host = Host.objects.all()
    return render_to_response("monitor/index.html", locals(), RequestContext(request))


@login_required()
@permission_verify()
def host_info(request, hostname, timing):
    temp_name = "monitor/monitor-header.html"
    # 传递磁盘号给前端JS,用以迭代分区图表
    disk = GetSysData(hostname, "disk", 3600, 1)
    data = disk.get_data()
    partitions_len = []
    for d in data:
        p = len(d["disk"])
        for x in range(p):
            partitions_len.append(x)
    return render_to_response("monitor/host_info_{}.html".format(timing), locals(), RequestContext(request))

