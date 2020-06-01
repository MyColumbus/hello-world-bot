# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import logging


#
# Logging levels:
# Levels   : Numeric Values
# Notset   :     0
# Debug    :     10  (default, development)
# Info     :     20
# Warning  :     30
# Error    :     40  (default, release)
# Critical :     50

# logging fromat string.
LOG_FORMAT = '%(levelname)s %(asctime)s (%(process)d/%(thread)d) - %(filename)s:%(lineno)d [%(funcName)s] %(message)s'


class HWLogs:
    def __init__(self, log_level):

        #logging.basicConfig(filename = '/var/log/columbus.logs',
        logging.basicConfig(filename = './helloworld.logs',
                            level = log_level,
                            format = LOG_FORMAT)
        self.logger = logging.getLogger()

    def __del__(self):
        del self.logger
