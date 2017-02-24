#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.ansible, name='ansible'),
    url(r'^playbook', views.playbook, name='playbook'),
]