# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

from bot_entry_point import app

if __name__ == '__main__':
    major = sys.version_info.major
    if major < 3:
        print('Upgrade your Python version to 3.x.x')
        sys.exit()

    # Error serveiry
    HWLogs(40)

    # run Flask application.
    app.run()

