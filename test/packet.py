#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import sys
sys.path.append("..")

from mqtt.packet import Packet


class TestPacket(unittest.TestCase):

    def setUp(self):
        self._encoding = 'utf-8'

    def test_parseFirstByte(self):
        byte = 0b00011101
        d = Packet.parseFirstByte(byte)
        self.assertEqual(d['mtype'], 'connect')
        self.assertEqual(d['dup'], True)
        self.assertEqual(d['qos'], Packet.QOS_EXACTLY_ONCE)
        self.assertEqual(d['retain'], True)

    def test_calculateRemainLength(self):
        barray = bytearray()
        barray.extend([0, 0x7F])
        length = Packet.calculateRemainLength(bytes(barray))
        self.assertEqual(length, 0x7F)

        barray = bytearray()
        barray.extend([0, 0xFF, 0x7F])
        length = Packet.calculateRemainLength(bytes(barray))
        self.assertEqual(length, 16383)

        barray = bytearray()
        barray.extend([0, 0xFF, 0xFF, 0x7F])
        length = Packet.calculateRemainLength(bytes(barray))
        self.assertEqual(length, 2097151)

        barray = bytearray()
        barray.extend([0, 0xFF, 0xFF, 0xFF, 0x7F])
        length = Packet.calculateRemainLength(bytes(barray))
        self.assertEqual(length, 268435455)

        barray = bytearray()
        barray.extend([0, 0xFF, 0xFF, 0xFF, 0xFF])
        length = Packet.calculateRemainLength(bytes(barray))
        self.assertEqual(length, 268435455)

    def test_encodeRemainLength(self):
        p = Packet()

        length = p._encodeRemainLength(127)
        self.assertEqual(length, [0x7F])

        length = p._encodeRemainLength(16383)
        self.assertEqual(length, [0xFF, 0x7F])

        length = p._encodeRemainLength(2097151)
        self.assertEqual(length, [0xFF, 0xFF, 0x7F])

        length = p._encodeRemainLength(268435455)
        self.assertEqual(length, [0xFF, 0xFF, 0xFF, 0x7F])

    def test_parseNextValue(self):
        p = Packet()

        barray = bytearray()
        barray.extend([0, 4])
        barray.extend('testtest'.encode(self._encoding))
        v, d = p._parseNextValue(bytes(barray))
        self.assertEqual(v, 'test')
        self.assertEqual(d, 'test')

        barray = bytearray()
        barray.extend([5])
        barray.extend('test'.encode(self._encoding))
        v, d = p._parseNextValue(bytes(barray), Packet._ONE_BYTE_VALUE)
        self.assertEqual(v, 5)
        self.assertEqual(d, 'test')

        barray = bytearray()
        barray.extend([1, 0])
        barray.extend('test'.encode(self._encoding))
        v, d = p._parseNextValue(bytes(barray), Packet._ONE_WORD_VALUE)
        self.assertEqual(v, 256)
        self.assertEqual(d, 'test')

    def test_connect_packet(self):
        data = bytearray()
        data.append(0b00010000)

        barray = bytearray()
        barray.extend([0, 6])
        barray.extend('MQIsdp'.encode(self._encoding))
        barray.append(3)
        barray.append(0b11110110)
        barray.extend([0, 60])
        barray.extend([0, 11])
        barray.extend('test_client'.encode(self._encoding))
        barray.extend([0, 9])
        barray.extend('test/test'.encode(self._encoding))
        barray.extend([0, 15])
        barray.extend('This is a test.'.encode(self._encoding))
        barray.extend([0, 5])
        barray.extend('admin'.encode(self._encoding))
        barray.extend([0, 5])
        barray.extend('admin'.encode(self._encoding))

        data.append(len(barray))
        data.extend(barray)

        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.pname, 'MQIsdp')
        self.assertEqual(p.pversion, 3)
        self.assertEqual(p.cleanSession, True)
        self.assertEqual(p.clientId, 'test_client')
        self.assertEqual(p.keepAliveTime, 60)
        self.assertEqual(p.willTopic, 'test/test')
        self.assertEqual(p.willMessage, 'This is a test.')
        self.assertEqual(p.willQOS, 2)
        self.assertEqual(p.willRetain, True)
        self.assertEqual(p.username, 'admin')
        self.assertEqual(p.password, 'admin')
        self.assertEqual(p._encodeConnectFlag(), 0b11110110)

        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'connect',
            'dup': False,
            'qos': 0,
            'retian': False,
            'keep_alive_time': 60,
            'client_id': 'test_client',
            'will_topic': 'test/test',
            'will_message': 'This is a test.',
            'will_retain': True,
            'will_qos': 2,
            'username': 'admin',
            'password': 'admin',
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_connack_packet(self):
        barray = bytearray()
        barray.append(0b00100000)
        barray.extend([2, 0, 0])
        data = bytes(barray)
        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'connack')
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'connack',
            'dup': False,
            'qos': 0,
            'retain': False,
            'return_code': 0x00,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_pingreq_packet(self):
        barray = bytearray()
        barray.extend([0b11000000, 0])
        data = bytes(barray)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'pingreq')
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'pingreq',
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_pingresp_packet(self):
        barray = bytearray()
        barray.extend([0b11010000, 0])
        data = bytes(barray)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'pingresp')
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'pingresp',
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_disconnect_packet(self):
        barray = bytearray()
        barray.extend([0b11100000, 0])
        data = bytes(barray)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'disconnect')
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'disconnect',
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_subscribe_packet(self):
        data = bytearray()
        data.append(0b10000010)

        barray = bytearray()
        barray.extend([0, 10])
        barray.extend([0, 3])
        barray.extend('a/b'.encode(self._encoding))
        barray.append(0)
        barray.extend([0, 3])
        barray.extend('c/d'.encode(self._encoding))
        barray.append(1)

        data.append(len(barray))
        data.extend(barray)
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'subscribe')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(p.topics[0][0], 'a/b')
        self.assertEqual(p.topics[0][1], 0)
        self.assertEqual(p.topics[1][0], 'c/d')
        self.assertEqual(p.topics[1][1], 1)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'subscribe',
            'dup': False,
            'qos': 1,
            'message_id': 10,
            'topics': [('a/b', 0), ('c/d', 1)],
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_publish_packet(self):
        data = bytearray()
        data.append(0b00110010)

        barray = bytearray()
        barray.extend([0, 3])
        barray.extend('a/b'.encode(self._encoding))
        barray.extend([0, 10])
        msg = '这是一条测试消息。'
        barray.extend(msg.encode(self._encoding))

        data.append(len(barray))
        data.extend(barray)
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'publish')
        self.assertEqual(p.topic, 'a/b')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(p.message, msg)

        d = {
            'mtype': 'publish',
            'dup': False,
            'qos': 1,
            'retain': False,
            'topic': 'a/b',
            'message_id': 10,
            'message': msg,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

        data = bytearray()
        data.append(0b00110000)

        barray = bytearray()
        barray.extend([0, 3])
        barray.extend('a/b'.encode(self._encoding))
        msg = '这是一条测试消息。'
        barray.extend(msg.encode(self._encoding))

        data.append(len(barray))
        data.extend(barray)
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'publish')
        self.assertEqual(p.topic, 'a/b')
        self.assertEqual(p.message, msg)

        d = {
            'mtype': 'publish',
            'dup': False,
            'qos': 0,
            'retain': False,
            'topic': 'a/b',
            'message': msg,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_suback_packet(self):
        data = bytearray()
        data.append(0b10010000)

        barray = bytearray()
        barray.extend([0, 10])
        barray.extend([0, 2])

        data.append(len(barray))
        data.extend(barray)
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'suback')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(p.grantedQos[0], 0)
        self.assertEqual(p.grantedQos[1], 2)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'suback',
            'message_id': 10,
            'granted_qos': [0, 2]
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_unsubscribe_packet(self):
        data = bytearray()
        data.append(0b10100010)

        barray = bytearray()
        barray.extend([0, 10])

        topic1 = 'a/b'.encode(self._encoding)
        barray.extend([0, len(topic1)])
        barray.extend(topic1)
        topic2 = 'c/d'.encode(self._encoding)
        barray.extend([0, len(topic2)])
        barray.extend(topic2)

        data.append(len(barray))
        data.extend(barray)
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'unsubscribe')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(p.topics[0], topic1)
        self.assertEqual(p.topics[1], topic2)

        d = {
            'mtype': 'unsubscribe',
            'dup': False,
            'qos': 1,
            'message_id': 10,
            'topics': [topic1, topic2],
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_unsuback_packet(self):
        data = bytearray()
        data.append(0b10110000)
        data.append(2)
        data.extend([0, 10])
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'unsuback')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'unsuback',
            'message_id': 10,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_puback_packet(self):
        data = bytearray()
        data.append(0b01000000)
        data.append(2)
        data.extend([0, 10])
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'puback')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'puback',
            'message_id': 10,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_pubrec_packet(self):
        data = bytearray()
        data.append(0b01010000)
        data.append(2)
        data.extend([0, 10])
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'pubrec')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'pubrec',
            'message_id': 10,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_pubrel_packet(self):
        data = bytearray()
        data.append(0b01100010)
        data.append(2)
        data.extend([0, 10])
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'pubrel')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'pubrel',
            'qos': 1,
            'message_id': 10,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)

    def test_pubcomp_packet(self):
        data = bytearray()
        data.append(0b01110000)
        data.append(2)
        data.extend([0, 10])
        data = bytes(data)

        p = Packet.fromData(data)
        self.assertEqual(p.mtype, 'pubcomp')
        self.assertEqual(p.messageId, 10)
        self.assertEqual(bytes(p), data)

        d = {
            'mtype': 'pubcomp',
            'message_id': 10,
        }
        p = Packet(**d)
        self.assertEqual(bytes(p), data)
