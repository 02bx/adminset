#! /usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE, STDOUT, call
from cmdb.models import Host, HostGroup
from django.shortcuts import render_to_response, redirect, RequestContext
from django.http import HttpResponse
import os
from config.views import get_dir
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify


ansible_dir = get_dir("a_path")
roles_dir = get_dir("r_path")
playbook_dir = get_dir("p_path")


@login_required()
@permission_verify()
def index(request):
    temp_name = "setup/setup-header.html"
    all_host = Host.objects.all()
    all_dir = get_roles(roles_dir)
    all_pbook = get_playbook(playbook_dir)
    all_group = HostGroup.objects.all()
    return render_to_response('setup/ansible.html', locals(), RequestContext(request))


def get_roles(args):
    dir_list = []
    dirs = os.listdir(args)
    for d in dirs:
        if d[0] == '.':
            pass
        elif os.path.isfile(args+d):
            pass
        else:
            dir_list.append(d)
    return dir_list


def get_playbook(args):
    files_list = []
    dirs = os.listdir(args)
    for d in dirs:
        if d[0] == '.':
            pass
        elif os.path.isdir(args+d):
            pass
        elif d.endswith(".retry"):
            os.remove(args+d)
        else:
            files_list.append(d)
    return files_list


@login_required()
def playbook(request):
    ret = []
    temp_name = "setup/setup-header.html"
    if os.path.exists(ansible_dir + '/gexec.yml'):
        os.remove(ansible_dir + '/gexec.yml')
    else:
        pass
    if request.method == 'POST':
        host = request.POST.getlist('mserver', [])
        group = request.POST.getlist('mgroup', [])
        pbook = request.POST.getlist('splaybook', [])
        roles = request.POST.getlist('mplaybook', [])
    if host:
        if roles:
            for h in host:
                f = open(ansible_dir + '/gexec.yml', 'w+')
                flist = ['- hosts: '+h+'\n', '  remote_user: root\n', '  gather_facts: false\n', '  roles:\n']
                for r in roles:
                    rs = '    - ' + r + '\n'
                    flist.append(rs)
                f.writelines(flist)
                f.close()
                cmd = "ansible-playbook"+" " + ansible_dir+'/gexec.yml'
                p = Popen(cmd, stderr=PIPE, stdout=PIPE, shell=True)
                data = p.communicate()[0]
                ret.append(data)
        else:
            for h in host:
                for p in pbook:
                    f = open(playbook_dir + p, 'r+')
                    flist = f.readlines()
                    flist[0] = '- hosts: '+h+'\n'
                    f = open(playbook_dir + p, 'w+')
                    f.writelines(flist)
                    f.close()
                    cmd = "ansible-playbook"+" " + playbook_dir + p
                    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
                    data = p.communicate()[0]
                    ret.append(data)
        return render_to_response('setup/result.html', locals(), RequestContext(request))


@login_required()
@permission_verify()
def ansible_command(request):
    command_list = []
    ret2 = []
    count = 1
    temp_name = "setup/setup-header.html"
    if request.method == 'POST':
        mcommand = request.POST.get('mcommand')
        command_list = mcommand.split('\n')
        for command in command_list:
            if command.startswith("ansible"):
                p = Popen(command, stdout=PIPE, stderr=PIPE,shell=True)
                data = p.communicate()
                ret2.append(data)
            else:
                data = "your command " + str(count) + "  is invalid!"
                ret2.append(data)
            count += 1
        return render_to_response('setup/result.html', locals(), RequestContext(request))


@login_required()
@permission_verify()
def host_sync(request):
    group = HostGroup.objects.all()
    ansible_file = open(ansible_dir+"/hosts", "wb")
    all_host = Host.objects.all()
    for host in all_host:
        #gitlab ansible_host=10.100.1.76 host_name=gitlab
        host_item = host.hostname+" "+"ansible_host="+host.ip+" "+"host_name="+host.hostname+"\n"
        ansible_file.write(host_item)
    for g in group:
        group_name = "["+g.name+"]"+"\n"
        ansible_file.write(group_name)
        members = Host.objects.filter(group__name=g)
        for m in members:
            group_item = m.hostname+"\n"
            ansible_file.write(group_item)
    ansible_file.close()
    return HttpResponse("ok")