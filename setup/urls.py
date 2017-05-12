#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views, ansible, shell, jobs


urlpatterns = [
    url(r'ansible/$', ansible.index, name='ansible'),
    url(r'^shell/$', shell.index, name='shell'),
    url(r'^job/list/$', jobs.index, name='job_list'),
    url(r'^job/add/$', jobs.job_add, name='job_add'),
    url(r'^job/del/$', jobs.job_del, name='job_del'),
    url(r'^job/interval/list/$', jobs.job_interval_list, name='job_interval_list'),
    url(r'^job/interval/add/$', jobs.job_interval_add, name='job_interval_add'),
    url(r'^job/interval/del/$', jobs.job_interval_del, name='job_interval_del'),
    url(r'^job/interval/edit/(?P<ids>\d+)/$', jobs.job_interval_edit, name='job_interval_edit'),
    url(r'^job/crontab/$', jobs.job_crontab, name='job_crontab'),
    url(r'^job/edit/(?P<ids>\d+)/$', jobs.job_edit, name='job_edit'),
    url(r'^scripts/exec/$', shell.exec_scripts, name='exec_scripts'),
    url(r'^playbook/$', ansible.playbook, name='playbook'),
    url(r'^ansible/command/$', ansible.ansible_command, name='acommand'),
    url(r'^host/sync/$', ansible.host_sync, name='host_sync'),
]