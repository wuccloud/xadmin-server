#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project : xadmin-server
# filename : local
# author : ly_13
# date : 10/18/2024


from werkzeug.local import Local

thread_local = Local()


def _find(attr):
    return getattr(thread_local, attr, None)