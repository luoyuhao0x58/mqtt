#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import uuid
import random


def decode_msb_lsb(msb=0, lsb=0):
    return msb << 8 | lsb


def encode_msb_lsb(num):
    return (num >> 8, num & 0xFF)


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac


def gen_client_id(prefix='mqtt'):
    return '%s_%s%06d' % (
        prefix, get_mac_address(), random.randint(0, 999999))
