# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import json
import logging
from flask import Flask, request
from flask_restful import Resource, Api
from inference import HWBase
from telegram_handler import TBOT

app = Flask(__name__)
api = Api(app)
logger = logging.getLogger()


##########################################
# Bot Webhooks
##########################################

class TestHWorldBotWebhook(Resource):
    """
    Test Hello World Webhook: This hook is for Test Hello World bot interface.
    """
    def __init__(self):
        # Telegram Object
        self.teleg = TBOT()
        # Logging object
        self.logger = logging.getLogger()

    def __del__(self):
        # Clean up objects.
        del self.teleg
        del self.logger


    def post(self):
        """This method handles the http requests for the Dialogflow webhook
        This is meant to be used in conjunction with the columbus Dialogflow agent
        """

        req = request.get_json(silent=True, force=True)
        try:
            action = req.get('queryResult').get('action')
        except AttributeError:
            return 'json error'

        platform = req.get('originalDetectIntentRequest').get('source')
        self.logger.debug('New Message -- platform={0} action={1}'.format(platform, action))
        self.logger.debug('Message Dump ==> \n{0}'.format(json.dumps(req, indent=4)))

        if platform == 'telegram':
            self.teleg.process_telegram_req(req)

        else:
            self.logger.error('Unsupported platform')


#########################################
# Routing infromation for all the APIs. #
#########################################
api.add_resource(TestHWorldBotWebhook, '/test_hworldbot_webhook')

