#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

MSG_T = {
    # 0x00: 'reserved',
    0x01: 'connect',
    0x02: 'connack',
    0x03: 'publish',
    0x04: 'puback',
    0x05: 'pubrec',
    0x06: 'pubrel',
    0x07: 'pubcomp',
    0x08: 'subscribe',
    0x09: 'suback',
    0x0A: 'unsubscribe',
    0x0B: 'unsuback',
    0x0C: 'pingreq',
    0x0D: 'pingresp',
    0x0E: 'disconnect',
    # 0x0F: 'reserved',
}
MSG_CODES = dict((v, k) for k, v in MSG_T.items())
MSG_T_SHIFT = 4

DUP_MASK = 0x08
DUP_SHIFT = 3

QOS_MASK = 0x06
QOS_SHIFT = 1

RETAIN_MASK = 0x01

REMAIN_LEN_NEXT_BYTE_MASK = 0x80
REMAIN_LEN_MASK = 0x7F
REMAIN_LEN_MULTIPLIER = 0x80

USERNAME_FLAG_MASK = 0x80
USERNAME_FLAG_SHIFT = 7

PASSWORD_FLAG_MASK = 0x40
PASSWORD_FLAG_SHIFT = 6

WILL_RETAIN_MASK = 0x20
WILL_RETAIN_SHIFT = 5

WILL_QOS_MASK = 0x18
WILL_QOS_SHIFT = 3

WILL_FLAG_MASK = 0x04
WILL_FLAG_SHIFT = 2

CLEAN_SESSION_MASK = 0x02
CLEAN_SESSION_SHIFT = 1

CONNECT_ACCEPTED = 0x00
CONNECT_UNACCEPTABLE_PROTOCOL_VERSION = 0x01
CONNECT_IDENTIFIER_REJECTED = 0X02
CONNECT_SERVER_UNAVAILABLE = 0x03
CONNECT_BAD_USERNAME_OR_PASSWORD = 0x04
CONNECT_NOT_AUTHORIZED = 0x05
