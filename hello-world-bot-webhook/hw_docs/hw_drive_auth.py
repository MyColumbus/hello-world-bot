# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

from __future__ import print_function
import pickle
import os.path
import sys
import random
import json
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


logger = logging.getLogger()

class HWDocs:
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
        self.creds = None
        self.itinerary_templates = ['14L4Ib36Rn0Ielc3yM2m2PWHGG467ty4fU_TpN7IF8UQ']
        self.drive_service = None
        self.docs_service = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('hw_docs/token.pickle'):
            with open('hw_docs/token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'hw_docs/credentials.json', self.DRIVE_SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('hw_docs/token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        if self.creds == None:
            print('ERROR : Service credentials unavailable!')
            sys.exit()

        # Start drive and docs services.
        self.drive_service = build('drive', 'v3', credentials=self.creds, cache_discovery=False)
        self.docs_service = build('docs', 'v1', credentials=self.creds, cache_discovery=False)


    def hwd_pick_a_template(self, country, platform, uid):
        """
        There are list of templates that a itinerary can be created from.
        The pick from list is random, to give users none bot expereince.
        """

        logger.debug('Country {0}'.format(country))
        copy_title = country + '_' + platform + '_' + str(uid)
        body = {
            'name': copy_title,
            'description': 'Columbus generated travel itinerary.',
        }
        drive_response = self.drive_service.files().copy(
            fileId=random.choice(self.itinerary_templates), body=body).execute()
        document_copy_id = drive_response.get('id')
        print('Dup copy ID : {0}'.format(document_copy_id))

        # File permissions
        user_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        self.drive_service.permissions().create(
                fileId=document_copy_id,
                body=user_permission,
                fields='id').execute()

        return document_copy_id



    def hwd_replace_text(self, key, value):
        """
        Replace text request structure. 
        """
        req = {'replaceAllText': {
                     'containsText': {
                         'text': '{{' + key + '}}',
                         'matchCase':  'true'
                     },
                     'replaceText': value,
                 }}

        return req


    def hwd_insert_text(self, idx, text):
         """
         Insert raw text without formating.
         """
         req = {'insertText': {
                 'location': {
                     'index': idx,
                 },
                 'text': text
             }}

         return req, len(text)


    def hwd_format_text(self, starti, endi, is_bold, is_italic, is_underline):
        """
        Format the text as following: 
        - Bold
        - Italic
        """
        req = {'updateTextStyle': {
                'range': {
                    'startIndex': starti,
                    'endIndex': endi
                },
                'textStyle': {
                    'bold': is_bold,
                    'italic': is_italic,
                    'underline': is_underline
                },
                'fields': 'bold, italic'
            }}

        return req


    def hwd_insert_bullet_item(self, idx, title):

         req = {
             'insertText': {
                 'location': {
                     'index': idx,
                 },
                 'text': title
             }},{
                 'createParagraphBullets': {
                  'range': {
                      'startIndex': idx,
                      'endIndex':  idx + len(title)
                  },
                  'bulletPreset': 'BULLET_DIAMONDX_ARROW3D_SQUARE',
              }}

         return req, len(title)


    def hwd_insert_hyperlink(self, start_idx, end_idx, url):
        """
        Insert hyperlink to the text for a given range in the
        document body.
        """

        return {
           "updateTextStyle": {
            "textStyle": {
             "link": {
              "url": url
             }
            },
            "range": {
             "startIndex": start_idx,
             "endIndex": end_idx
            },
            "fields": "link"
        }}


    def hwd_get_text_range_idx(self, doc_id, match_text):

        # Do a document "get" request and print the results as formatted JSON
        result = self.docs_service.documents().get(documentId=doc_id).execute()
        data = result.get('body').get('content')
        startIdx = 0
        endIdx = 0

        for d in data:
            para = d.get('paragraph')
            if para is None:
                continue
            else:
                elements = para.get('elements')
                for e in elements:
                    content = e.get('textRun').get('content')
                    if match_text in content:
                        startIdx = e.get('startIndex')
                        endIdx = e.get('endIndex')

        return startIdx, endIdx


    def hwd_batch_update(self, doc_id, requests):
         """
         Populdate itinerary data in the picked template.
         """

         result = self.docs_service.documents().batchUpdate(
             documentId=doc_id, body={'requests': requests}).execute()


#docs = HWDocs()
#doc_id = docs.hwd_pick_a_template('France', 'Telegram', 1234)
#doc_id = '1KmPa9AQjUYddgoBL8d0CfJ6hfrrQm5AwuRzLljOGEhI'
#docs.hwd_populate_data(doc_id)
#s, e = docs.hwd_get_text_range_idx(doc_id, 'Check live prices')
#print('startIdx {0} endIdx {1}'.format(s, e))
#docs.hwd_insert_hyperlink(doc_id, s, e, 'https://thehelloworld.xyz')

