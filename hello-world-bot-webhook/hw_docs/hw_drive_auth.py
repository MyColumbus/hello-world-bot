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
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



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
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)


    def hwd_pick_a_template(self, country, platform, uid):
        """
        There are list of templates that a itinerary can be created from.
        The pick from list is random, to give users none bot expereince.
        """

        copy_title = country + '_' + platform + '_' + str(uid)
        body = {
            'name': copy_title
        }
        drive_response = self.drive_service.files().copy(
            fileId=random.choice(self.itinerary_templates), body=body).execute()
        document_copy_id = drive_response.get('id')
        print('Dup copy ID : {0}'.format(document_copy_id))

        return document_copy_id


    def hwd_populate_data(self, doc_id):
        """
        Populdate itinerary data in the picked template.
        """

        country = 'France'

        requests = [
             {
                'replaceAllText': {
                    'containsText': {
                        'text': '{{country}}',
                        'matchCase':  'true'
                    },
                    'replaceText': country,
                }}
        ]

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()


    def hwd_insert_hyperlink(self, doc_id, start_idx, end_idx, url):
        """
        Insert hyperlink to the text for a given range in the
        document body.
        """

        requests = [
          {
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
        ]

        result = self.docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()


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
                    if content == match_text:
                        startIdx = e.get('startIndex')
                        endIdx = e.get('endIndex')

        return startIdx, endIdx


#docs = HWDocs()
#doc_id = docs.hwd_pick_a_template('France', 'Telegram', 1234)
#doc_id = '1KmPa9AQjUYddgoBL8d0CfJ6hfrrQm5AwuRzLljOGEhI'
#docs.hwd_populate_data(doc_id)
#s, e = docs.hwd_get_text_range_idx(doc_id, 'Check live prices')
#print('startIdx {0} endIdx {1}'.format(s, e))
#docs.hwd_insert_hyperlink(doc_id, s, e, 'https://thehelloworld.xyz')

