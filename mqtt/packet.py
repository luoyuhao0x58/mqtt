#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import constant as _
from util import decode_msb_lsb, encode_msb_lsb, gen_client_id


class Packet(object):

    _ENCODING = 'utf-8'

    QOS_AT_MOST_ONCE, QOS_AT_LEAST_ONCE, QOS_EXACTLY_ONCE = (0, 1, 2)

    _MSB_LSB_VALUE, _ONE_BYTE_VALUE, _ONE_WORD_VALUE = (0, 1, 2)

    def __init__(
            self, mtype=None, dup=False, qos=QOS_AT_MOST_ONCE, retain=False,
            **kwargs):
        self.mtype = mtype
        self.dup = dup
        self.qos = qos
        self.retain = retain

        if len(kwargs):
            f = getattr(self, '_init%sPacket' % self.mtype.capitalize())
            f(**kwargs)

    def _initConnectPacket(
            self, pname='MQIsdp', pversion=3, clean_session=True,
            keep_alive_time=240, client_id=None,
            **kwargs):
        self.pname = pname
        self.pversion = pversion
        self.cleanSession = clean_session
        self.keepAliveTime = keep_alive_time

        if not client_id:
            client_id = gen_client_id()
        self.clientId = client_id

        if kwargs.get('will_topic'):
            self.willTopic = kwargs['will_topic']
        if kwargs.get('will_message'):
            self.willMessage = kwargs['will_message']
        if kwargs.get('will_qos'):
            self.willQOS = kwargs['will_qos']
        if kwargs.get('will_retain'):
            self.willRetain = kwargs['will_retain']

        if kwargs.get('username'):
            self.username = kwargs['username']
        if kwargs.get('password'):
            self.password = kwargs['password']

    def _initConnackPacket(self, return_code=_.CONNECT_ACCEPTED):
        self.returnCode = return_code

    def _initSubscribePacket(self, message_id, topics=[]):
        self.messageId = message_id
        self.topics = topics

    def _initSubackPacket(self, message_id, granted_qos=[]):
        self.messageId = message_id
        self.grantedQos = granted_qos

    def _initUnsubscribePacket(self, message_id, topics=[]):
        self.messageId = message_id
        self.topics = topics

    def _initUnsubackPacket(self, message_id):
        self.messageId = message_id

    def _initPublishPacket(self, topic, message, message_id=None):
        self.topic = topic
        self.message = message
        if message_id:
            self.messageId = message_id

    def _initPubackPacket(self, message_id):
        self.messageId = message_id

    def _initPubrecPacket(self, message_id):
        self.messageId = message_id

    def _initPubrelPacket(self, message_id):
        self.messageId = message_id

    def _initPubcompPacket(self, message_id):
        self.messageId = message_id

    def __repr__(self):
        return "Packet(%s)" % self.mtype

    @classmethod
    def fromData(cls, data):
        if not isinstance(data, basestring):
            data = bytes(data)
        packet = Packet(**cls.parseFirstByte(ord(data[0])))
        remain_length = cls.calculateRemainLength(data)
        data = buffer(data, len(data) - remain_length)
        packet._parse(data)
        return packet

    @classmethod
    def parseFirstByte(cls, byte):
        mtype = _.MSG_T[byte >> _.MSG_T_SHIFT]
        dup = bool((byte & _.DUP_MASK) >> _.DUP_SHIFT)
        qos = (byte & _.QOS_MASK) >> _.QOS_SHIFT
        retain = bool(byte & _.RETAIN_MASK)
        return {'mtype': mtype, 'dup': dup, 'qos': qos, 'retain': retain}

    @classmethod
    def calculateRemainLength(self, data, max_byte_length=4):
        multiplier = 1
        length = 0
        data = bytearray(buffer(data, 1, max_byte_length))
        for digit in data:
            length += (digit & _.REMAIN_LEN_MASK) * multiplier
            multiplier *= _.REMAIN_LEN_MULTIPLIER
            if ((digit & _.REMAIN_LEN_NEXT_BYTE_MASK) == 0):
                break
        return length

    def _parseNextValue(self, data, dtype=_MSB_LSB_VALUE):
        if dtype == self._MSB_LSB_VALUE:
            length = decode_msb_lsb(ord(data[0]), ord(data[1]))
            value = unicode(buffer(data, 2, length), self._ENCODING)
            remain_data = buffer(data, length + 2)
        elif dtype == self._ONE_BYTE_VALUE:
            value = ord(data[0])
            remain_data = buffer(data, 1)
        elif dtype == self._ONE_WORD_VALUE:
            value = decode_msb_lsb(ord(data[0]), ord(data[1]))
            remain_data = buffer(data, 2)
        return (value, remain_data)

    def _parse(self, data):
        f = getattr(self, '_parse%sData' % self.mtype.capitalize(), None)
        if f:
            f(data)

    def _parseConnectData(self, data):
        self.pname, data = self._parseNextValue(data)
        self.pversion, data = self._parseNextValue(data, self._ONE_BYTE_VALUE)

        connect_flag_b, data = self._parseNextValue(data, self._ONE_BYTE_VALUE)
        cfd = self._parseConnectFlag(connect_flag_b)
        self.cleanSession = cfd['clean_session']

        self.keepAliveTime, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)
        self.clientId, data = self._parseNextValue(data)

        if cfd['will_flag']:
            self.willTopic, data = self._parseNextValue(data)
            self.willMessage, data = self._parseNextValue(data)
            self.willQOS = cfd['will_qos']
            self.willRetain = cfd['will_retain']

        if cfd['username_flag']:
            self.username, data = self._parseNextValue(data)
            self.password, data = self._parseNextValue(data)

    def _parseConnectFlag(self, byte):
        return {
            'username_flag': bool((byte & _.USERNAME_FLAG_MASK)
                                  >> _.USERNAME_FLAG_SHIFT),
            'password_flag': bool((byte & _.PASSWORD_FLAG_MASK)
                                  >> _.PASSWORD_FLAG_SHIFT),
            'will_retain': bool((byte & _.WILL_RETAIN_MASK)
                                >> _.WILL_RETAIN_SHIFT),
            'will_qos': (byte & _.WILL_QOS_MASK) >> _.WILL_QOS_SHIFT,
            'will_flag': bool((byte & _.WILL_FLAG_MASK) >> _.WILL_FLAG_SHIFT),
            'clean_session': bool((byte & _.CLEAN_SESSION_MASK)
                                  >> _.CLEAN_SESSION_SHIFT),
        }

    def _parseConnackData(self, data):
        self.returnCode = ord(data[1])

    def _parseSubscribeData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

        self.topics = []
        while data:
            topic_name, data = self._parseNextValue(data)
            qos, data = self._parseNextValue(data, self._ONE_BYTE_VALUE)
            self.topics.append((topic_name, qos))

    def _parseSubackData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)
        self.grantedQos = []
        while data:
            qos, data = self._parseNextValue(
                data, self._ONE_BYTE_VALUE)
            self.grantedQos.append(qos)

    def _parseUnsubscribeData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

        self.topics = []
        while data:
            topic_name, data = self._parseNextValue(data)
            self.topics.append(topic_name)

    def _parseUnsubackData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

    def _parsePublishData(self, data):
        self.topic, data = self._parseNextValue(data)
        if self.qos != self.QOS_AT_MOST_ONCE:
            self.messageId, data = self._parseNextValue(
                data, self._ONE_WORD_VALUE)
        self.message = unicode(data, self._ENCODING)

    def _parsePubackData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

    def _parsePubrecData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

    def _parsePubrelData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

    def _parsePubcompData(self, data):
        self.messageId, data = self._parseNextValue(
            data, self._ONE_WORD_VALUE)

    def __str__(self):
        return self.encode()

    def encode(self):
        first_byte = self._encodeFirstByte()
        remain_data = self._encodeData()
        remain_length = self._encodeRemainLength(len(remain_data))

        barray = bytearray()
        barray.append(first_byte)
        barray.extend(remain_length)
        barray.extend(remain_data)
        return bytes(barray)

    def _encodeFirstByte(self):
        b = _.MSG_CODES[self.mtype] << _.MSG_T_SHIFT
        b |= int(self.dup) << _.DUP_SHIFT
        b |= self.qos << _.QOS_SHIFT
        b |= int(self.retain)
        return b

    def _encodeRemainLength(self, x):
        remaining_length = []
        while True:
            digit = x % _.REMAIN_LEN_MULTIPLIER
            x = x / _.REMAIN_LEN_MULTIPLIER
            if x > 0:
                digit |= _.REMAIN_LEN_NEXT_BYTE_MASK
            remaining_length.append(digit)
            if x <= 0:
                break
        return remaining_length

    def _encodeData(self):
        f = getattr(self, '_encode%sData' % self.mtype.capitalize(), None)
        if f:
            return f()
        else:
            return bytearray()

    def _encodeConnectData(self):
        barray = bytearray()

        v = self.pname.encode(self._ENCODING)
        barray.extend(encode_msb_lsb(len(v)))
        barray.extend(v)

        barray.append(self.pversion)
        barray.append(self._encodeConnectFlag())
        barray.extend(encode_msb_lsb(self.keepAliveTime))

        v = self.clientId.encode(self._ENCODING)
        barray.extend(encode_msb_lsb(len(v)))
        barray.extend(v)

        if getattr(self, 'willTopic', None):
            v = self.willTopic.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(v)))
            barray.extend(v)
        if getattr(self, 'willMessage', None):
            v = self.willMessage.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(v)))
            barray.extend(v)
        if getattr(self, 'username', None):
            v = self.username.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(v)))
            barray.extend(v)
        if getattr(self, 'password', None):
            v = self.password.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(v)))
            barray.extend(v)
        return barray

    def _encodeConnectFlag(self):
        byte = 0
        if getattr(self, 'username', None):
            byte |= _.USERNAME_FLAG_MASK
        if getattr(self, 'password', None):
            byte |= _.PASSWORD_FLAG_MASK
        if getattr(self, 'willRetain', None):
            byte |= _.WILL_RETAIN_MASK
        byte |= getattr(self, 'willQOS', 0) << _.WILL_QOS_SHIFT
        if getattr(self, 'willTopic', None
                   ) and getattr(self, 'willMessage', None):
            byte |= _.WILL_FLAG_MASK
        if self.cleanSession:
            byte |= _.CLEAN_SESSION_MASK
        return byte

    def _encodeConnackData(self):
        barray = bytearray()
        barray.append(0)
        barray.append(self.returnCode)
        return barray

    def _encodeSubscribeData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        for topic_name, qos in self.topics:
            topic_name = topic_name.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(topic_name)))
            barray.extend(topic_name)
            barray.append(qos)
        return barray

    def _encodePublishData(self):
        barray = bytearray()
        topic_name = self.topic.encode(self._ENCODING)
        barray.extend(encode_msb_lsb(len(topic_name)))
        barray.extend(topic_name)

        if getattr(self, 'messageId', None):
            barray.extend(encode_msb_lsb(self.messageId))

        message = self.message.encode(self._ENCODING)
        barray.extend(message)
        return barray

    def _encodeSubackData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        for qos in self.grantedQos:
            barray.append(qos)
        return barray

    def _encodeUnsubscribeData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        for topic_name in self.topics:
            topic_name = topic_name.encode(self._ENCODING)
            barray.extend(encode_msb_lsb(len(topic_name)))
            barray.extend(topic_name)
        return barray

    def _encodeUnsubackData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        return barray

    def _encodePubackData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        return barray

    def _encodePubrecData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        return barray

    def _encodePubrelData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        return barray

    def _encodePubcompData(self):
        barray = bytearray()
        barray.extend(encode_msb_lsb(self.messageId))
        return barray
