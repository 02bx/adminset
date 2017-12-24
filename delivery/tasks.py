#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.shortcuts import HttpResponse
from subprocess import Popen, PIPE


@shared_task
def deploy(job_name, server_list, app_path, source_address):
    ret = []
    job_workspace = "/var/opt/adminset/workspace/{}/code".format(job_name)
    if app_path.endswith("/"):
        app_path += "/"
    cmd = "git clone {0} {1}".format(source_address, job_workspace)
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    data = p.communicate()
    with open(job_workspace + '/deploy.log', 'w+') as f:
        f.writelines(data)
    for server in server_list:
        cmd = "rsync --progress -raz --delete --exclude '.git' --exclude '.svn' {0} {1}:{2}".format(job_workspace, server, app_path)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        data = p.communicate()
        with open(job_workspace + '/deploy.log', 'a+') as f:
            f.writelines(data)
        ret.append(data)
    return ret
