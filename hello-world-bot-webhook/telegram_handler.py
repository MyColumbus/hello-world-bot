# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import json
import random
import logging
from flask import request
from inference import HWBase
from hw_db.database_wrapper import HWDB

import telegram
from telegram.ext import Updater
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup



class TBOT:
    __tbot_token = '629163526:AAGsj8KSmqYAilYjXwANoAgp9TH3WLfwfNM'
    __flag_offset = 127462 - ord('A')

    def __init__(self):
        """
        Telegram bot constructor.
        """
        self.updater = Updater(token = self.__tbot_token, use_context=True)
        # Database Object
        self.hwdb = HWDB()
        # Inference Object
        self.hwbase = HWBase()
        # Logging Object
        self.logger = logging.getLogger()
        self.logger.info('Telegram Initialized')

        self.all_experiences = self.hwbase.hwb_all_experiences()
        self.all_euro_countries = self.hwbase.hwb_all_countries('EUROPE')
        self.all_asia_countries = self.hwbase.hwb_all_countries('ASIA')
        self.all_euro_countries.remove('Monaco')
        self.all_euro_countries.remove('Ireland')
        self.all_euro_countries.remove('SanMarino')


    def __del__(self):
        """
        Cleanup/Destroy created objects.
        """
        del self.hwdb
        del self.hwbase
        del self.logger


    ##
    # All Menus #
    ##
    def tbot_flag(self, code):
        """
        Country Flag Emoji code
        """
        code = code.upper()
        return chr(ord(code[0]) + __flag_offset) + chr(ord(code[1]) + __flag_offset)


    def tbot_get_location_n_contact(self):
        """
        Request for User Contact and Location information.
        """
        location_keyboard = KeyboardButton(text="Share My Location", request_location=True)
        contact_keyboard = KeyboardButton(text="Share My Contact", request_contact=True)
        custom_keyboard = [[ location_keyboard, contact_keyboard ]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
        return reply_markup


    def tbot_build_menu(self, buttons, n_cols, header_buttons=None, footer_buttons=None):
        """
        Build Menu using provided buttons and their properties.
        """
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            menu.append([footer_buttons])
        return menu


    def tbot_update_experience_menu(self, exp_list, data):
        """
        Render experiences menu with updates.
        """
        button_list = []

        exp_list.sort()
        for s in exp_list:
            if s in data:
                button_list.append(InlineKeyboardButton(s + ' *', callback_data=s))
            else:
                button_list.append(InlineKeyboardButton(s, callback_data=s))
        button_list.append(InlineKeyboardButton("DONE", callback_data='DONE'))

        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_experience_menu(self, exp_list):
        """
        By Experience Menu.
        """
        button_list = []

        exp_list.sort()
        for s in exp_list:
            button_list.append(InlineKeyboardButton(s, callback_data=s))
        button_list.append(InlineKeyboardButton("DONE", callback_data='DONE'))

        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_pick_continent(self):
        """
        Pick the continent of the world.
        """
        button_list = [
                InlineKeyboardButton('Europe', callback_data='EUROPE'),
                InlineKeyboardButton('Asia', callback_data='ASIA'),
            ]
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_main_menu(self):
        """
        Main or Start Menu.
        """
        button_list = [
                InlineKeyboardButton('By Country', callback_data='TELEGRAM_BY_COUNTRY'),
                InlineKeyboardButton('By Experience', callback_data='TELEGRAM_BY_EXPERIENCE'),
                InlineKeyboardButton('My Bucket List', callback_data='Show my wish list')
            ]
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_by_country_menu(self, all_countries):
        """
        By Country Menu
        """
        button_list = []

        all_countries.sort()
        for c in all_countries:
            button_list.append(InlineKeyboardButton(c, callback_data='bycountry_' + c))

        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_select_country(self, country, cat):
        """
        By Country --> Selected Country expereinces.
        """
        cat_in_country = self.hwbase.hwb_all_experiences_for_a_country(country)
        rx_cat_list = cat.split(',')
        c_list = list(set(cat_in_country) & set(rx_cat_list))
        cat_str = ''
        for cat in c_list:
            if not cat_str:
                cat_str += cat
            else:
                cat_str += ', ' + cat

        button_list = [
                InlineKeyboardButton('Explore ' + country.upper(), callback_data='Explore country ' + country + ' ' + cat_str),
            ]
        self.logger.debug('Callback Text: Explore country {0} {1}'.format(country, cat_str))
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_a_country_menu(self, country, destination, cat):
        """
        Destination menu : Add to bucketlist or Best time to visit.
        """
        button_list = [
                InlineKeyboardButton('Add To Bucket List', callback_data='Add '+ country + ' ' + destination + ' to my wish list'),
                InlineKeyboardButton('Best Time To Visit', callback_data='When to visit '+ country),
            ]
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_bucket_list_menu(self, uid, country, destination):
        """
        Bucketlist Menu : Remove from bucketlist or Show Thing to do.
        """
        button_list = [
                InlineKeyboardButton('Remove', callback_data='Delete '+ country + ' ' + destination + ' from my wish list'),
                InlineKeyboardButton('Activities To Do', callback_data='Activities to do ' + country + ' ' + destination),
            ]
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_find_countries(self, req_categories, chat_id):
        """Returns a string containing text with a response to the user
        with the list of countries.
        Takes categories as input
        """
        data = []

        self.logger.debug('Create Itinerarary')

        rsp, err = cbml.cbml_create_itinerary(req_categories, 1)

        if len(rsp['Places']) == 0:
            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\n `This expereince is not available in any country`', parse_mode=telegram.ParseMode.MARKDOWN)
            return

        for idx in range(len(rsp['Places'])):
            payload = {}
            payload['Country'] = rsp['Places'][idx]['Country']
            payload['Destination'] = rsp['Places'][idx]['Destination']
            payload['Categories'] = rsp['Places'][idx]['Categories']
            payload['TTD'] = rsp['Places'][idx]['TTD'][0]['ThingsToDo']
            data.append(payload)

        self.logger.debug(json.dumps(data, indent=4))

        prev_cnty = ''
        prev_cat = ''
        textToSend = ''
        for r in data:

            all_cat = ''
            idx = 0
            textToSend = ''
            reply_markup = ''
            for cat in r['Categories']:
                if idx == 0:
                    all_cat += cat
                    idx += 1
                else:
                    all_cat += ', ' + cat

            if prev_cat != all_cat:
                textToSend += "\n\n*For " + all_cat.upper() + " preferred countries*"
                prev_cat = all_cat

            if prev_cnty == r['Country']:
                continue
            else:
                c_url = cbml.cbml_country_info_by_field(r['Country'], 'lonelyPlanetURL')
                text_rsp = "\n\n*" + r['Country'].upper() + "* " + self.tbot_flag(cbml.cbml_country_info_by_field(r['Country'], 'CountryCode')) + " [Details](" + c_url + ")\n"
                textToSend += text_rsp
                reply_markup = self.tbot_select_country(r['Country'], all_cat)
                self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=False)

                prev_cnty = r['Country']



    def tbot_explore_a_country(self, chat_id, country, categories):
        """Returns a string containing text with a response to the user
        with the destination, TTD and other details.
        Takes the country and categories as input
        """
        textToSpeech_rsp = ''
        full_cat_list = []

        country = country.replace(' ', '')
        if country == 'Czechia':
            country = 'CzechRepublic'
        self.logger.debug('Rx parameters: categories {0} country {1}'.format(categories, country))

        if country:
            rsp = cbml.cbml_get_destination(country, categories)
        else:
            self.logger.error('Country name is empty')
            return textToSpeech_rsp, full_cat_list

        #self.logger.debug(json.dumps(rsp, indent=4))


        cat_str = ''
        textToSend = ''
        idx = 0
        for cat in categories:
            if idx == 0:
                cat_str += cat
                idx += 1
            else:
                cat_str += ', ' + cat

        textToSend = '\n\n*For ' + cat_str.upper() + ' experiences in ' + country.upper() + ' preferred destinations are:\n*'

        if len(rsp['Places']) == 0:
            textToSend += '\n\n`This expereince is not available in ' + country + '`'
            self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, parse_mode=telegram.ParseMode.MARKDOWN)
            return

        for idx in range(len(rsp['Places'])):
            payload_1 = {}
            lp_url = ''
            payload_1['Destination'] = rsp['Places'][idx]['TTD'][0]['Destination']
            payload_1['TTD'] = rsp['Places'][idx]['TTD'][0]['ThingsToDo']
            lp_url = cbml.cbml_lonely_planet_urls(country, payload_1['Destination'])
            if lp_url:
                textToSend += '\n\* ' + payload_1['TTD'] + ' in [' + payload_1['Destination'] + '](' + lp_url + ')'
            else:
                textToSend += '\n\* ' + payload_1['TTD'] + ' in ' + payload_1['Destination']

            if len(rsp['Places'][idx]['TTD']) > 1:
                payload_2 = {}
                lp_url = ''
                payload_2['Destination'] = rsp['Places'][idx]['TTD'][1]['Destination']
                payload_2['TTD'] = rsp['Places'][idx]['TTD'][1]['ThingsToDo']
                lp_url = cbml.cbml_lonely_planet_urls(country, payload_2['Destination'])
                if lp_url:
                    textToSend += '\n\* ' + payload_2['TTD'] + ' in [' + payload_2['Destination'] + '](' + lp_url + ')'
                else:
                    textToSend += '\n\* ' + payload_2['TTD'] + ' in ' + payload_2['Destination']

            reply_markup = self.tbot_a_country_menu(country, payload_1['Destination'], cat_str)
            self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, reply_markup=reply_markup,
                    parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
            textToSend = ''



    def tbot_things_todo(self, chat_id, country, destination):
        """Returns a string containing text with a response to the user
        with the TTD and other details for a country and destination.
        Takes the country and destination as input
        """
        rsp = {}
        textToSend = ''
        total_time, rsp['TTD'] = cbml.cbml_find_thingstodo(country, destination, 2)

        self.logger.debug(json.dumps(rsp, indent=4))

        if len(rsp['TTD']) == 0:
            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\n `This expereince is not available in any country`', parse_mode=telegram.ParseMode.MARKDOWN)
            return

        textToSend = '\n\nActivities to do in *' + country.upper() + ', ' + destination + '*\n'
        for idx in range(len(rsp['TTD'])):
            text_rsp = ''
            text_rsp = '\n\* ' + rsp['TTD'][idx]['ThingsToDo'] + ' \[' + str(rsp['TTD'][idx]['TypicalTimeSpent']) + ' TS]'
            textToSend += text_rsp

        textToSend += '\n\n*Legends :* \n  TS - Typical Time Spent By People (in minutes)'

        self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, parse_mode=telegram.ParseMode.MARKDOWN)



    def tbot_callback_commands(self, query_result, payload):
        chat_id =payload.get('callback_query').get('message').get('chat').get('id')

        if 'TELEGRAM_BY_EXPERIENCE' == payload.get('callback_query').get('data'):
            self.hwdb.hwdb_user_session_delete(chat_id)
            reply_markup = self.tbot_experience_menu(self.all_experiences)
            self.updater.bot.sendMessage(chat_id=chat_id,
                    text='\n\nPlease select the experiences you would like to have during your vacation and hit DONE.', reply_markup=reply_markup)

        elif 'TELEGRAM_BY_COUNTRY' == payload.get('callback_query').get('data'):
            reply_markup = self.tbot_by_country_menu(self.all_countries)
            self.updater.bot.send_message(chat_id=chat_id,
                    text='\n\nPick the country you would like to explore.', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

        elif 'bycountry_' in payload.get('callback_query').get('data'):
            tokens = payload.get('callback_query').get('data').split('_', 2)
            country = tokens[1]
            supported_cat = cbml.cbml_all_categories_a_country(country)
            self.logger.debug('Categories for {0} are {1}'.format(country, supported_cat))

            self.hwdb.hwdb_user_session_delete(chat_id)
            self.hwdb.hwdb_user_session_upsert(chat_id, country, 'NULL', 'NULL', 'I')

            reply_markup = self.tbot_experience_menu(supported_cat)
            self.updater.bot.sendMessage(chat_id=chat_id,
                    text='\n\nPlease select the experiences you would like to have *' + country.upper() + '* during your vacation and hit DONE.', reply_markup=reply_markup,
                    parse_mode=telegram.ParseMode.MARKDOWN)

        elif 'When to visit' in payload.get('callback_query').get('data'):
            country = query_result.get('parameters').get('geo-country')
            when_to_visit_rsp = cbml.cbml_country_info_by_field(country, 'WhenToVisit')

            self.updater.bot.sendMessage(chat_id=chat_id,
                    text='\n\n*' + country + ' :* ' + when_to_visit_rsp, parse_mode=telegram.ParseMode.MARKDOWN)

        elif 'Activities to do ' in payload.get('callback_query').get('data'):
            country = query_result.get('parameters').get('geo-country')
            destination = query_result.get('parameters').get('geo-city')
            self.logger.debug('Activites for country {0} and destination {1}'.format(country, destination))
            self.tbot_things_todo(chat_id, country, destination)

        else:
            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nOops. Please check your command and try again.')


    ##
    # Commands #
    ##
    def tbot_commands(self, payload):
        chat_id = payload.get('chat').get('id')

        if payload.get('text') == '/start':
            reply_markup = self.tbot_main_menu()
            self.updater.bot.send_message(chat_id=chat_id, text='Hello ' + payload.get('from').get('first_name') + ',\nHow would you like to explore places *by country* or *by experience*.', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
            f_name = payload.get('from').get('first_name')
            l_name = payload.get('from').get('last_name')
            username = payload.get('from').get('username')
            self.hwdb.hwdb_columbus_user_bucketlist_upsert(chat_id, f_name, l_name, 'NULL', 'NULL', username)

        else:
            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nOops. Please check your command and try again.')



    ##
    # Messages to support
    # 1. Welcome
    # 2. Country, activities, city
    ##
    def tbot_messages(self, query_result, payload):
        chat_id = payload.get('chat').get('id')
        req_categories = []
        textToSpeech_rsp = ''

        req_categories = query_result.get('parameters').get('experiences')
        country = query_result.get('parameters').get('geo-country')

        if req_categories and country:
            self.tbot_explore_a_country(chat_id, country, req_categories)
        else:
            self.logger.error('Parameters are not set properly country : {0} categories : {1}'.format(country, req_categories))



    ##
    # Bucket list operations.
    ##
    def tbot_bucketlist_processing(self, query_result, payload):
        categories = []

        chat_id = payload.get('callback_query').get('from').get('id')
        country = query_result.get('parameters').get('geo-country')
        destination = query_result.get('parameters').get('geo-city')
        categories = query_result.get('parameters').get('experiences')
        operation = query_result.get('parameters').get('bucketlist_ops')


        if operation == 'Add':
            self.logger.debug('Add to bucket list userID {0} country {1} destination {2} cat{3}'.format(chat_id, country, destination, categories))
            if not categories:
                self.hwdb.hwdb_bucketlist_insert(chat_id, country, destination, 'NULL', 'NULL')
            else:
                for cat in categories:
                    self.hwdb.hwdb_bucketlist_insert(chat_id, country, destination, cat, 'NULL')
            self.updater.bot.sendMessage(chat_id=chat_id, text='Added to your bucket list.')

        elif operation == 'Delete':
            self.hwdb.hwdb_columbus_user_bucketlist_delete(chat_id, country, destination)
            self.logger.debug('Item deleted from user {0} bucketlist, country {1} destination {2}'.format(chat_id, country, destination))
            self.updater.bot.sendMessage(chat_id=chat_id, text='Deleted ' + country + ', ' + destination + ' from bucket list.')

        elif operation == 'Show':
            #FIXME : All Categories are not shown and display it in better way.
            result = self.hwdb.hwdb_bucketlist_select(chat_id)
            self.logger.debug(json.dumps(result, indent=4))

            prev_country = ''
            prev_destination = ''
            bucketlist_rsp = '\n\n*Your Bucket list :*\n\n'

            if not len(result):
                self.updater.bot.send_message(chat_id=chat_id,
                        text='\n\nYour bucket list is empty!', parse_mode=telegram.ParseMode.MARKDOWN)

            for idx in range(len(result)):
                country = result[idx].get('country')
                destination = result[idx].get('destination')
                category = result[idx].get('category')

                if idx == 0:
                    c_url = cbml.cbml_lonely_planet_urls(country, destination)
                    if not c_url:
                        c_url = cbml.cbml_country_info_by_field(country, 'lonelyPlanetURL')
                    bucketlist_rsp += '\n\* ' + destination + ', *' + country.upper() + '* ' + self.tbot_flag(cbml.cbml_country_info_by_field(country, 'CountryCode')) + ' [Details](' + c_url + ') \n'
                    reply_markup = self.tbot_bucket_list_menu(chat_id, country, destination)
                    self.updater.bot.send_message(chat_id=chat_id,
                            text=bucketlist_rsp, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=False)
                    prev_country = country
                    prev_destination = destination

                else:
                    if (prev_country == country) and (prev_destination == destination):
                        continue
                    else:
                        bucketlist_rsp = ''
                        c_url = cbml.cbml_lonely_planet_urls(country, destination)
                        if not c_url:
                            c_url = cbml.cbml_country_info_by_field(country, 'lonelyPlanetURL')
                        bucketlist_rsp = '\n\* ' + destination + ', *' + country.upper() + '* ' + self.tbot_flag(cbml.cbml_country_info_by_field(country, 'CountryCode')) + ' [Details](' + c_url + ') \n'
                        reply_markup = self.tbot_bucket_list_menu(chat_id, country, destination)
                        self.updater.bot.send_message(chat_id=chat_id,
                                text=bucketlist_rsp, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=False)
                        prev_country = country
                        prev_destination = destination


        else:
            self.logger.error('Bucket list operation is not permitted : {0} for user ID {1}'.format(operation, chat_id))




    def tbot_process_telegram_callback_intents(self, query_result, payload):
        """
        This method parse all the Telegram specific WITH callback intents.
        """

        if ((query_result.get('action') == 'input.telegram_by_country') or
            (query_result.get('action') == 'input.telegram_by_experience') or
            (query_result.get('action') == 'input.telegram_by_country_name') or
            (query_result.get('action') == 'input.bucket_list_show_ops') or
            (query_result.get('action') == 'input.bucket_list_ops') or
            (query_result.get('action') == 'find_places.find_places-followup') or
            (query_result.get('action') == 'input.find_places') or
            (query_result.get('action') == 'input.when_to_visit') or
            (query_result.get('action') == 'input.activites_to_do')):

            self.logger.debug('callback data - {0}'.format(payload.get('callback_query').get('data')))
            chat_id = payload.get('callback_query').get('message').get('chat').get('id')

            if (('TELEGRAM_BY_COUNTRY' == payload.get('callback_query').get('data')) or
                ('TELEGRAM_BY_EXPERIENCE' == payload.get('callback_query').get('data')) or
                ('When to visit' in payload.get('callback_query').get('data')) or
                ('bycountry_' in payload.get('callback_query').get('data')) or
                ('Activities to do ' in payload.get('callback_query').get('data'))):
                self.tbot_callback_commands(query_result, payload)


            elif (('Show my wish list' == payload.get('callback_query').get('data')) or
                  ('Add ' in payload.get('callback_query').get('data')) or
                  ('Delete ' in payload.get('callback_query').get('data'))):
                self.tbot_bucketlist_processing(query_result, payload)

            elif 'select the experiences' in payload.get('callback_query').get('message').get('text'):
                sess_data = self.hwdb.hwdb_user_session_select(chat_id)
                if sess_data['country'] == 'NULL':
                    self.logger.debug('Received experience : {0} expereince in the user list {1}'.format(payload.get('callback_query').get('data'), sess_data['category']))
                    if 'DONE' in payload.get('callback_query').get('data'):
                        if len(sess_data['category']) == 0:
                            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                            return 'ok'
                        self.tbot_find_countries(sess_data['category'], chat_id)
                        self.hwdb.hwdb_user_session_delete(chat_id)
                    else:
                        category = payload.get('callback_query').get('data')
                        if len(list(set(sess_data['category']) & set([category]))) == 0:
                            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'I')
                        else:
                            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'D')

                        rec = self.hwdb.hwdb_user_session_select(chat_id)
                        reply_markup = self.tbot_update_experience_menu(self.all_experiences, rec['category'])
                        self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                                reply_markup=reply_markup)
                else:
                    if 'DONE' in payload.get('callback_query').get('data'):
                        if len(sess_data['category']) == 0:
                            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                            return 'ok'
                        self.tbot_explore_a_country(chat_id, sess_data['country'], sess_data['category'])
                        for cat in sess_data['category']:
                            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'D')

                    else:
                        self.logger.debug('SELECTED Country : {0}'.format(sess_data['country']))
                        supported_cat = cbml.cbml_all_categories_a_country(sess_data['country'])
                        category = payload.get('callback_query').get('data')
                        if len(list(set(sess_data['category']) & set([category]))) == 0:
                            self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], 'NULL', category, 'I')
                        else:
                            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'D')

                        rec = self.hwdb.hwdb_user_session_select(chat_id)
                        reply_markup = self.tbot_update_experience_menu(supported_cat, rec['category'])
                        self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                                reply_markup=reply_markup)

            elif 'Explore country' in payload.get('callback_query').get('data'):
                categories = query_result.get('parameters').get('experiences')
                country = query_result.get('outputContexts')[0].get('parameters').get('geo-country')

                self.tbot_explore_a_country(chat_id, country, categories)

            else:
                self.logger.error('Unsupported callback message!')



    def tbot_process_telegram_intents(self, query_result, payload):
        """
        This method parse Telegram specific WITHOUT callback intents.
        """

        if ((query_result.get('action') == 'input.cb_welcome') or
            (query_result.get('action') == 'find_places.find_places-followup') or
            (query_result.get('action') == 'input.find_places')):

            self.logger.debug('Intent without callback : {0}'.format(query_result.get('action')))
            if payload.get('text')[0] == '/':
                self.tbot_commands(payload)
            else:
                self.tbot_messages(query_result, payload)

        elif (query_result.get('action') == 'input.when_to_visit'):

            chat_id = payload.get('from').get('id')
            self.logger.debug('Intent without callback : {0}'.format(query_result.get('action')))
            country = query_result.get('parameters').get('geo-country')
            when_to_visit_rsp = cbml.cbml_country_info_by_field(country, 'WhenToVisit')

            self.updater.bot.sendMessage(chat_id=chat_id,
                    text='\n\n*' + country + ' :* ' + when_to_visit_rsp, parse_mode=telegram.ParseMode.MARKDOWN)

        else:
            self.logger.debug('Bad message received')



    def tbot_process_telegram_req(self, req):
        """This method handles the http requests for the Dialogflow webhook
        This is meant to be used in conjunction with the helloworld Dialogflow agent.
        This is telegram specific processing.

        There are 3 types of requests that can come from bot:
            1. Intents with callback
            2. Intents without callback - Commands (/start)
            3. Intents without callback - Plain text query
        """

        try:
            query_result = req.get('queryResult')
            payload = req.get('originalDetectIntentRequest').get('payload').get('data')

        except AttributeError:
            self.logger.error('Error in the JSON received data')
            return 'json error'

        # 1. Intent with callback
        if 'callback_query' in payload:
            self.tbot_process_telegram_callback_intents(query_result, payload)

        # 2 & 3. Intent without callback
        else:
            self.tbot_process_telegram_intents(query_result, payload)


        return 'ok'
