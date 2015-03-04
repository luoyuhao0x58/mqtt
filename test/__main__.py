#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '../')
sys.path.insert(0, path)

import unittest
from test.packet import TestPacket

if __name__ == '__main__':
    unittest.main()
