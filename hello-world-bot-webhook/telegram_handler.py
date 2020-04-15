# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import json
import random
import logging
import datetime
import math
from suntime import Sun, SunTimeException
from flask import request
from inference import HWBase
from hw_db.database_wrapper import HWDB
from hw_docs.hw_drive_auth import HWDocs

import telegram
from telegram.ext import Updater
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup



class TBOT:
    __tbot_token = '907125689:AAHZ__kBMDydgVL9jc8B4qUS37Dp-mcrQXM'
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
        # Documents Object
        self.hwdocs = HWDocs()
        # Logging Object
        self.logger = logging.getLogger()
        self.logger.info('Telegram Initialized')

        # All countries by continent
        self.all_Europe_countries = self.hwbase.hwb_all_countries('Europe')
        self.all_Asia_countries = self.hwbase.hwb_all_countries('Asia')

        # All experiences by continent
        self.all_Europe_experiences = self.hwbase.hwb_all_experiences('Europe') 
        self.all_Asia_experiences = self.hwbase.hwb_all_experiences('Asia')


    def __del__(self):
        """
        Cleanup/Destroy created objects.
        """
        del self.hwdb
        del self.hwbase
        del self.logger

    ## 
    # Default function #
    ##
    def tbot_default_method(self, query_result, payload):
        self.logger.error('Function is not defined, check the callback function name')

    ##
    # All Menus #
    ##
    def tbot_flag(self, code):
        """
        Country Flag Emoji code
        """
        code = code.upper()
        return chr(ord(code[0]) + self.__flag_offset) + chr(ord(code[1]) + self.__flag_offset)



    def tbot_get_location_n_contact(self):
        """
        Request for User Contact and Location information.
        """
        location_keyboard = KeyboardButton(text="Share My Location", request_location=True)
        contact_keyboard = KeyboardButton(text="Share My Contact", request_contact=True)
        custom_keyboard = [[ location_keyboard, contact_keyboard ]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
        return reply_markup


    def tbot_continents_menu(self):
        """
        Continents Menu.
        """
        button_list = [
                InlineKeyboardButton('Europe', callback_data='TELEGRAM_CONTINENT Europe'),
                InlineKeyboardButton('Asia', callback_data='TELEGRAM_CONTINENT Asia'),
            ]
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
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


    def tbot_do_you_mean_destinations_menu(self, sugg_dest, continent):
        """
        User may mis spelled or searching for a destination.
        """
        button_list = []

        sugg_dest.sort()
        for s in sugg_dest:
            button_list.append(InlineKeyboardButton(s, callback_data=s))
        button_list.append(InlineKeyboardButton('Try Again', callback_data='TELEGRAM_BY_DESTINATION ' + continent))

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


    def tbot_main_menu(self, continent):
        """
        Main or Start Menu.
        """

        button_list = [
                InlineKeyboardButton('By Countries', callback_data='TELEGRAM_BY_COUNTRY ' + continent),
                InlineKeyboardButton('By Experience', callback_data='TELEGRAM_BY_EXPERIENCE ' + continent),
                InlineKeyboardButton('By Destination', callback_data='TELEGRAM_BY_DESTINATION ' + continent),
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


    def tbot_create_itinerary_menu(self, country, all_cat):
        """
        Destination menu : Add to bucketlist or Best time to visit.
        """
        cat_in_country = self.hwbase.hwb_all_experiences_for_a_country(country)
        c_list = list(set(cat_in_country) & set(all_cat))
        cat_str = ''
        cat_str = ' '.join(c_list)

        button_list = [
                InlineKeyboardButton('Create Itinerary', callback_data='Create Itinerary ' + country + ' ' + cat_str),
            ]
        self.logger.debug('Callback: Create Itinerary {0} {1}'.format(country, cat_str))
        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup



    def tbot_create_itinerary_country_experiences_menu(self, country, exp):
        """
        By Country --> Selected Country expereinces.
        """
        button_list = []
        exp_in_country = self.hwbase.hwb_all_experiences_for_a_country(country)
        self.logger.debug('tbot_create_itinerary_country_experiences_menu() {0} {1}'.format(exp_in_country, exp))
        exp_in_country.sort()

        for s in exp_in_country:
            if s in exp:
                button_list.append(InlineKeyboardButton(s + ' *', callback_data=s))
            else:
                button_list.append(InlineKeyboardButton(s, callback_data=s))
        button_list.append(InlineKeyboardButton("DONE", callback_data='DONE'))

        reply_markup = InlineKeyboardMarkup(self.tbot_build_menu(button_list, n_cols=2))
        return reply_markup


    def tbot_by_country_create_itinerary_menu(self, country, all_cat):
        """
        Destination menu : Add to bucketlist or Best time to visit.
        """
        cat_in_country = self.hwbase.hwb_all_experiences_for_a_country(country)
        c_list = list(set(cat_in_country) & set(all_cat))
        cat_str = ''
        cat_str = ' '.join(c_list)

        button_list = [
                InlineKeyboardButton('Create Itinerary ', callback_data='Create Itinerary ' + country + ' ' + cat_str),
            ]
        self.logger.debug('Callback: Create Itinerary by country: {0} {1}'.format(country, cat_str))
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



    def tbot_find_countries(self, sess_data, chat_id):
        """Returns a string containing text with a response to the user
        with the list of countries.
        Takes categories and continent as input
        """
        data = []

        sugg, ret_data, err = self.hwbase.hwb_find_top_countries_for_experiences(sess_data['continent'], sess_data['category'])
        self.logger.debug('RX Data {0}'.format(json.dumps(ret_data, indent=4)))
        self.logger.debug('Suggestions Data {0}'.format(json.dumps(sugg, indent=4)))

        prev_exp_str = ''
        for rec in ret_data:
            text_rsp = ''
            textToSend = ''
            exp_str = ', '.join(rec['Experiences'])
            if prev_exp_str != exp_str:
                textToSend += '\n\nFor *' + exp_str.upper() + '* preferred countries'
                prev_exp_str = exp_str

            country = rec['Country']
            country_url = self.hwbase.hwb_country_info_by_field(country, 'lonelyPlanetURL')
            if not country_url:
                country_url = ''

            text_rsp = '\n\n[' + country.upper() + '](' + country_url + ') ' + self.tbot_flag(self.hwbase.hwb_country_info_by_field(country, 'CountryCode')) + '\n'
            dest_list_str = ' | '.join(rec['Destinations'])
            dest_list_str = dest_list_str.replace(':', ', ')
            text_rsp += '( _' + dest_list_str + '_ )'
            textToSend += text_rsp
            reply_markup = self.tbot_create_itinerary_menu(country, rec['Experiences'])
            self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=False)

        if err != 200:
            sug_str = ''
            for i in range(len(sugg)):
                for key, value in sugg[i].items():
                    for idx in range(len(value)):
                        if idx == 0:
                            sug_str += '\n*' + ', '.join(value[idx]) +  '*'
                        else:
                            sug_str += ' OR *' + ', '.join(value[idx]) + '*'

            sugg_text = '\n\nRequested combinations of expereiences are not available in any country, my suggestions would be to try :\n' + sug_str 
            self.updater.bot.sendMessage(chat_id=chat_id, text=sugg_text, parse_mode=telegram.ParseMode.MARKDOWN)



    def tbot_explore_a_country(self, chat_id, country, categories, by_country):
        """Returns a string containing text with a response to the user
        with the destination other details.
        Takes the country and categories as input
        """
        textToSend = ''
        full_cat_list = []

        #country = country.replace(' ', '')
        if country == 'Czechia':
            country = 'CzechRepublic'
        self.logger.debug('Rx parameters: categories {0} country {1}'.format(categories, country))

        if country:
            sugg, ret_data, err = self.hwbase.hwb_find_destination_for_experiences(country, categories)
            self.logger.debug('RX Data {0}'.format(json.dumps(ret_data, indent=4)))
        else:
            self.logger.error('Country name is empty')
            return textToSend, full_cat_list


        textToSend = '\n\n In *' + country.upper() + '*:\n'
        for rec in ret_data:
            text_rsp = ''
            exp_str = ', '.join(rec['Experiences'])
            textToSend += '\n\nFor *' + exp_str.upper() + '* preferred destinations are:\n'
            dest_list_str = ' | '.join(rec['Destinations'])
            dest_list_str = dest_list_str.replace(':', ', ')
            text_rsp = '( _' + dest_list_str + '_ )'
            textToSend += text_rsp
            reply_markup = self.tbot_create_itinerary_menu(country, rec['Experiences'])
            self.updater.bot.sendMessage(chat_id=chat_id, text=textToSend, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=False)
            textToSend = ''

        if err != 200:
            sug_str = ''
            for i in range(len(sugg)):
                for key, value in sugg[i].items():
                    for idx in range(len(value)):
                        if idx == 0:
                            sug_str += '\n*' + ', '.join(value[idx]) + '*'
                        else:
                            sug_str += ' OR *' + ', '.join(value[idx]) + '*'

            sugg_text = '\n\nRequested combinations of expereiences are not available in a specific destination, my suggestions would be to try :\n' + sug_str 
            self.updater.bot.sendMessage(chat_id=chat_id, text=sugg_text, parse_mode=telegram.ParseMode.MARKDOWN)



    def tbot_cb_pick_continents(self, query_result, payload):
        chat_id = payload.get('callback_query').get('from').get('id')
        continent = query_result.get('parameters').get('continents_of_world')

        if continent.lower() == 'europe':
            continent_text = '_There simply is no way to tour Europe and not be awestruck by its natural beauty, epic history and dazzling artistic and culinary diversity._'
        elif continent.lower() == 'asia':
            continent_text = '_From the nomadic steppes of Kazakhstan to the frenetic streets of Hanoi, Asia is a continent so full of intrigue, adventure, solace and spirituality that it has fixated and confounded travellers for centuries._'
        else:
            continent_text = ''

        reply_markup = self.tbot_main_menu(continent)
        self.updater.bot.edit_message_text(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'), text='\n\n' + continent_text + '\n\nHow would you like to explore *' + continent.upper() + '*?', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)


    ##
    # FIXME : This should be converted to callback and should have itinerary in bucketlist. 
    # Bucket list operations.
    ##
    def tbot_trips_processing(self, query_result, payload):
        categories = []

        chat_id = payload.get('callback_query').get('from').get('id')
        country = query_result.get('parameters').get('geo-country')
        operation = query_result.get('parameters').get('trips_ops')

        if operation == 'Show':
            self.updater.bot.send_message(chat_id=chat_id, text='Coming soon', parse_mode=telegram.ParseMode.MARKDOWN)
            """
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
            """

        else:
            self.logger.error('Bucket list operation is not permitted : {0} for user ID {1}'.format(operation, chat_id))



    def tbot_cb_by_options(self, query_result, payload):
        chat_id = payload.get('callback_query').get('from').get('id')
        continent = (query_result.get('parameters').get('continents_of_world'))

        if 'TELEGRAM_BY_EXPERIENCE' in payload.get('callback_query').get('data'):
            self.hwdb.hwdb_user_session_delete(chat_id)
            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', 'NULL', continent, 'I')
            reply_markup = self.tbot_experience_menu(eval('self.all_' + continent + '_experiences'))
            self.updater.bot.edit_message_text(chat_id=chat_id,
                    message_id=payload.get('callback_query').get('message').get('message_id'),
                    text='\n\nPlease select the experiences in *' + continent + '* you would like to have during your vacation and hit *DONE*.', 
                        reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

        elif 'TELEGRAM_BY_COUNTRY' in payload.get('callback_query').get('data'):
            self.hwdb.hwdb_user_session_delete(chat_id)
            reply_markup = self.tbot_by_country_menu(eval('self.all_' + continent + '_countries'))
            self.updater.bot.edit_message_text(chat_id=chat_id, 
                    message_id=payload.get('callback_query').get('message').get('message_id'),
                    text='\n\nPick the country of your preference :', reply_markup=reply_markup, 
                    parse_mode=telegram.ParseMode.MARKDOWN)

        elif 'TELEGRAM_BY_DESTINATION' in payload.get('callback_query').get('data'):
            self.hwdb.hwdb_user_session_delete(chat_id)
            sess_data = self.hwdb.hwdb_user_session_select(chat_id)
            self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], 'TELEGRAM_BY_DESTINATION', sess_data['category'], continent, 'I')
            self.updater.bot.edit_message_text(chat_id=chat_id,
                    message_id=payload.get('callback_query').get('message').get('message_id'),
                    text='\n\nText me your bucketlist *Destination* in ' + continent.upper() + '?', parse_mode=telegram.ParseMode.MARKDOWN)


        elif 'bycountry_' in payload.get('callback_query').get('data'):
            tokens = payload.get('callback_query').get('data').split('_', 2)
            country = tokens[1]
            continent = self.hwbase.hwb_get_continent_for_countries(country)

            supported_cat = self.hwbase.hwb_all_experiences_for_a_country(country)
            self.logger.debug('Categories for {0} are {1}'.format(country, supported_cat))

            self.hwdb.hwdb_user_session_delete(chat_id)
            self.hwdb.hwdb_user_session_upsert(chat_id, country, 'NULL', 'NULL', continent, 'I')

            reply_markup = self.tbot_experience_menu(supported_cat)
            self.updater.bot.sendMessage(chat_id=chat_id,
                    text='\n\nPlease select the experiences you would like to have in *' + country.upper() + '* during your vacation and hit DONE.', reply_markup=reply_markup,
                    parse_mode=telegram.ParseMode.MARKDOWN)

        else:
            self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nOops. Please check your command and try again.')



    def tbot_cb_find_places(self, query_result, payload):
        """
        This method parse Telegram find_places callback intents.
        """

        self.logger.debug('callback data - {0}'.format(payload.get('callback_query').get('data')))
        chat_id = payload.get('callback_query').get('message').get('chat').get('id')
        sess_data = self.hwdb.hwdb_user_session_select(chat_id)

        if 'select the experiences' in payload.get('callback_query').get('message').get('text'):
          
            if sess_data['country'] == 'NULL':
                self.logger.debug('Received experience : {0} expereince in the user list {1}'.format(payload.get('callback_query').get('data'), sess_data['category']))
                if 'DONE' in payload.get('callback_query').get('data'):
                    if len(sess_data['category']) == 0:
                        self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                        return 'ok'
                    self.tbot_find_countries(sess_data, chat_id)
                    for cat in sess_data['category']:
                        self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'NULL', 'D')
                else:
                    category = payload.get('callback_query').get('data')
                    if len(list(set(sess_data['category']) & set([category]))) == 0:
                        self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, sess_data['continent'], 'I')
                    else:
                        self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'NULL', 'D')

                    rec = self.hwdb.hwdb_user_session_select(chat_id)
                    reply_markup = self.tbot_update_experience_menu(eval('self.all_' + sess_data['continent'] + '_experiences'), rec['category'])
                    self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                            reply_markup=reply_markup)
            else:
                if 'DONE' in payload.get('callback_query').get('data'):
                    if len(sess_data['category']) == 0:
                        self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                        return 'ok'
                    self.tbot_explore_a_country(chat_id, sess_data['country'], sess_data['category'], True)
                    for cat in sess_data['category']:
                        self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'NULL', 'D')

                else:
                    self.logger.debug('SELECTED Country : {0}'.format(sess_data['country']))
                    supported_cat = self.hwbase.hwb_all_experiences_for_a_country(sess_data['country'])
                    category = payload.get('callback_query').get('data')
                    if len(list(set(sess_data['category']) & set([category]))) == 0:
                        self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], 'NULL', category, sess_data['continent'], 'I')
                    else:
                        self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'NULL', 'D')

                    rec = self.hwdb.hwdb_user_session_select(chat_id)
                    reply_markup = self.tbot_update_experience_menu(supported_cat, rec['category'])
                    self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                            reply_markup=reply_markup)

        elif 'Explore country' in payload.get('callback_query').get('data'):
            categories = query_result.get('parameters').get('experiences')
            country = query_result.get('outputContexts')[0].get('parameters').get('geo-country')

            if sess_data['country'] == 'NULL':
                self.hwdb.hwdb_user_session_upsert(chat_id, country, 'NULL', 'NULL', 'NULL', 'I')
            else:
                self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], 'NULL', 'NULL', 'NULL', 'D')
                self.hwdb.hwdb_user_session_upsert(chat_id, country, 'NULL', 'NULL', 'NULL', 'I')

            self.tbot_explore_a_country(chat_id, country, categories, False)


        elif 'Would you like to add more expereinces' in payload.get('callback_query').get('message').get('text'):
          
            if 'DONE' in payload.get('callback_query').get('data'):
                if len(sess_data['category']) == 0:
                    self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                    return 'ok'

                out_context = {}
                for out_context in query_result.get('outputContexts'):
                    if out_context.get('parameters').get('num_days'):
                        break

                num_days = out_context.get('parameters').get('num_days')
                num_adults = out_context.get('parameters').get('adults')
                num_kids = out_context.get('parameters').get('kids')

                payload = {}
                payload['Chat_ID'] = chat_id
                payload['Experiences'] = sess_data['category']
                payload['Country'] = sess_data['country']
                payload['NumDays'] = num_days
                payload['NumAdults'] = num_adults
                payload['NumKids'] = num_kids

                msg = 'Generating your itinerary ...'
                self.updater.bot.send_message(chat_id=payload['Chat_ID'], text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

                doc_id = self.hwdocs.hwd_pick_a_template(sess_data['country'], 'Telegram', chat_id)
                sugg, itinerary_data, err = self.hwbase.hwb_destinations_itinerary_data(payload)
                self.logger.debug('Itinerary Data {0}'.format(json.dumps(itinerary_data, indent=4)))

                self.tbot_populate_itinerary_data(doc_id, payload, itinerary_data)

                for cat in sess_data['category']:
                    self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'NULL', 'D')


            else:
                supported_cat = self.hwbase.hwb_all_experiences_for_a_country(sess_data['country'])
                category = payload.get('callback_query').get('data')
                self.logger.debug('SELECTED Country : {0} Rx Category {1} Existing Cats {2}'.format(sess_data['country'], category, sess_data['category']))
                if len(set(sess_data['category']) & set([category])) == 0:
                    self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], 'NULL', category, sess_data['continent'], 'I')
                else:
                    self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'NULL', 'D')

                rec = self.hwdb.hwdb_user_session_select(chat_id)
                reply_markup = self.tbot_update_experience_menu(supported_cat, rec['category'])
                self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                        reply_markup=reply_markup)

        elif 'Once you select the expereinces hit DONE to get your itinerary created' in payload.get('callback_query').get('message').get('text'):

            self.logger.debug('Received experience : {0} expereince in the user list {1}'.format(payload.get('callback_query').get('data'), sess_data['category']))
            if 'DONE' in payload.get('callback_query').get('data'):
                if len(sess_data['category']) == 0:
                    self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nPlease select atleast one experience', parse_mode=telegram.ParseMode.MARKDOWN)
                    return 'ok'

                msg = 'Generating your itinerary ...'
                self.updater.bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

                doc_id = self.hwdocs.hwd_pick_a_template(sess_data['country'], 'Telegram', chat_id)

                payload = {}
                payload['Chat_ID'] = chat_id
                payload['Experiences'] = sess_data['category']
                payload['Country'] = sess_data['country']
                payload['Destination'] = sess_data['destination']
                payload['TravelDate'] = ''
                payload['NumDays'] = 4
                payload['NumAdults'] = 2
                payload['NumKids'] = 1
                sugg, itinerary_data, err = self.hwbase.hwb_a_destination_itinerary_data(payload)
                self.logger.debug('Itinerary Data {0}'.format(json.dumps(itinerary_data, indent=4)))

                self.tbot_populate_itinerary_data(doc_id, payload, itinerary_data)

                for cat in sess_data['category']:
                    self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'NULL', 'D')

            else:
                category = payload.get('callback_query').get('data')
                if len(list(set(sess_data['category']) & set([category]))) == 0:
                    self.hwdb.hwdb_user_session_upsert(chat_id, sess_data['country'], sess_data['destination'], category, sess_data['continent'], 'I')
                else:
                    self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', category, 'NULL', 'D')

                rec = self.hwdb.hwdb_user_session_select(chat_id)
                supported_cat, _ = self.hwbase.hwb_all_experiences_for_by_destination(sess_data['continent'], sess_data['destination'])
                reply_markup = self.tbot_update_experience_menu(supported_cat, rec['category'])
                self.updater.bot.edit_message_reply_markup(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                        reply_markup=reply_markup)

        else:
            self.logger.error('Unsupported callback message!')


    def tbot_cb_bydestination_message(self, query_result, payload):
        chat_id = payload.get('callback_query').get('from').get('id')
        sess_data = self.hwdb.hwdb_user_session_select(chat_id)

        destination = query_result.get('queryText')

        supported_cat, country = self.hwbase.hwb_all_experiences_for_by_destination(sess_data['continent'], destination)
        continent = self.hwbase.hwb_get_continent_for_countries(country)
        self.logger.debug('Categories for country/destination {0}/{1} are {2}'.format(destination, country, supported_cat))

        self.hwdb.hwdb_user_session_delete(chat_id)
        self.hwdb.hwdb_user_session_upsert(chat_id, country, destination, 'NULL', continent, 'I')

        reply_markup = self.tbot_experience_menu(supported_cat)
        self.updater.bot.edit_message_text(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'),
                text='\n*' + destination + '* is in ' + country.upper() + ', has following experiences. '
                'Once you select the expereinces hit DONE to get your itinerary created.', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
        

    #############################
    # Callback Intent Table
    #############################
    callbackIntents = {
            'input.pick_continent': tbot_cb_pick_continents,
            'input.my_trips': tbot_trips_processing,
            'input.pick_by_option': tbot_cb_by_options,
            'input.telegram_by_country_name': tbot_cb_by_options,
            'input.find_places': tbot_cb_find_places,
            'find_places.find_places-followup': tbot_cb_find_places,
            'input.bydestination': tbot_cb_bydestination_message 
    }


    def tbot_call_callback_intents_methods(self, query_result, payload):
        action = query_result.get('action')
        f = lambda self, a, qr, p : self.callbackIntents.get(a, lambda a, qr, p : self.tbot_default_method(qr, p))(self, qr, p)
        f(self, action, query_result, payload)



    def tbot_process_telegram_callback_intents(self, query_result, payload):
        """
        This method parse all the Telegram specific WITH callback intents.
        """
        if ((query_result.get('action') == 'input.pick_by_option') or
            (query_result.get('action') == 'input.pick_continent') or
            (query_result.get('action') == 'input.telegram_by_country_name') or
            (query_result.get('action') == 'input.my_trips') or
            (query_result.get('action') == 'find_places.find_places-followup') or
            (query_result.get('action') == 'input.find_places') or
            (query_result.get('action') == 'input.when_to_visit') or
            (query_result.get('action') == 'input.activites_to_do') or
            (query_result.get('action') == 'input.bydestination')):

            self.logger.debug('Intent without callback : {0}'.format(query_result.get('action')))
            self.tbot_call_callback_intents_methods(query_result, payload)



    def tbot_process_telegram_intents(self, query_result, payload):
        """
        This method parse Telegram specific WITHOUT callback intents.
        """

        if ((query_result.get('action') == 'input.cb_welcome') or
            (query_result.get('action') == 'input.unknown') or
            (query_result.get('action') == 'find_places.find_places-followup') or
            (query_result.get('action') == 'input.find_places') or
            (query_result.get('action') == 'settings.country-name') or
            (query_result.get('action') == 'input.pick_continent') or
            (query_result.get('action') == 'create_itinerary.ci_travel_date.ci_people') or
            (query_result.get('action') == 'input.bydestination')):

            self.logger.debug('Intent without callback : {0}'.format(query_result.get('action')))
            self.tbot_call_normal_intents_methods(query_result, payload)

        else:
            self.logger.debug('Bad message received')


    ##
    # Commands #
    ##
    def tbot_start_command(self, query_result, payload):
        chat_id = payload.get('chat').get('id')

        reply_markup = self.tbot_continents_menu()
        self.updater.bot.send_message(chat_id=chat_id, text='Hello *' + payload.get('from').get('first_name') + '*, to create your travel itinerary, kindly let me know your preferred continent for travel?', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
        f_name = payload.get('from').get('first_name')
        l_name = payload.get('from').get('last_name')
        username = payload.get('from').get('username')
        self.hwdb.hwdb_columbus_user_bucketlist_upsert(chat_id, f_name, l_name, 'NULL', 'NULL', username)



    def tbot_user_settings(self, query_result, payload):
        chat_id = payload.get('chat').get('id')

        user_country = query_result.get('parameters').get('geo-country')
        chat_id = payload.get('from').get('id')
        self.hwdb.hwdb_columbus_user_bucketlist_upsert(chat_id, 'NULL', 'NULL', 'NULL', user_country, 'NULL')
        self.logger.debug('User updated his/her native country {0}'.format(user_country))


    def tbot_continent_menu(self, query_result, payload):
        chat_id = payload.get('chat').get('id')
        continent = query_result.get('parameters').get('continents_of_world')

        if continent.lower() == 'europe':
            continent_text = '_There simply is no way to tour Europe and not be awestruck by its natural beauty, epic history and dazzling artistic and culinary diversity._'
        elif continent.lower() == 'asia':
            continent_text = '_From the nomadic steppes of Kazakhstan to the frenetic streets of Hanoi, Asia is a continent so full of intrigue, adventure, solace and spirituality that it has fixated and confounded travellers for centuries._'
        else:
            continent_text = ''

        reply_markup = self.tbot_main_menu(continent)
        self.updater.bot.edit_message_text(chat_id=chat_id, message_id=payload.get('callback_query').get('message').get('message_id'), text='\n\n' + continent_text + '\n\nHow would you like to explore *' + continent.upper() + '*?', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
        



    def tbot_populate_itinerary_data(self, doc_id, payload, data):
        """
        Populate the data that needs to be updated in the itinerary and send the batch update. 
        """

        request = []
        #
        # 1. Insert text 
        #  

        # Find table dimensions.
        prev_exp_dest = ''
        count = 0
        elements_counts = []
        for idx in range(len(data)):
            exp_dest_str = ''.join(data[idx]['Experiences']) + data[idx]['Destination']

            if prev_exp_dest != exp_dest_str:
                prev_exp_dest = exp_dest_str
                if count:
                    elements_counts.append(count)
                count = 1
            else:
                count += 1
        elements_counts.append(count)
        self.logger.debug('Table Dimensions : {0}'.format(elements_counts))


        # Find the write index
        _, wr_idx = self.hwdocs.hwd_get_text_range_idx(doc_id, 'Make changes to the plan based on your convenience')

        prev_idx = 0
        element = -1

        prev_exp_str = ''
        prev_exp_and_dest_str = ''
        for rec in data:

            curr_exp = ', '.join(rec['Experiences'])
            if curr_exp != prev_exp_str:
                req, idx = self.hwdocs.hwd_insert_text(wr_idx, '\n' + ' ' + curr_exp + '.\n')
                request.append(req)
                req = self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, False, False, False, 'Roboto', 18, 400, '#ffffff', '#999999')
                request.append(req)
                prev_exp_str = curr_exp
                wr_idx += idx

            if curr_exp + rec['Destination'] != prev_exp_and_dest_str:
                prev_exp_and_dest_str = curr_exp + rec['Destination']
                req, idx = self.hwdocs.hwd_insert_text(wr_idx, '\n' + rec['Destination'].replace(':', ', '))
                request.append(req)
                req = self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, True, False, False, 'Roboto', 18, 400, '#3c91f4')
                request.append(req)
                prev_dest_str = rec['Destination']
                wr_idx += idx

                if rec['TopSights']:
                    element += 1
                    # Add one extra row for header.
                    request.append(self.hwdocs.hwd_create_table_at_index(elements_counts[element] + 1, 2, wr_idx))
                    wr_idx += 1  # This is required
                    request.append(self.hwdocs.hwd_modify_table_columns_property(wr_idx, 0, 100))
                    request.append(self.hwdocs.hwd_modify_table_cell_style(elements_counts[element], 2, wr_idx, '#ffffff'))
                    wr_idx += 3
                    req, idx = self.hwdocs.hwd_insert_text(wr_idx, 'Date & Time')
                    request.append(req)
                    request.append(self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, False, False, False, 'Roboto', 11, 400, '#999999'))
                    wr_idx += (idx + 2) 

                    req, idx = self.hwdocs.hwd_insert_text(wr_idx, 'Things To Do')
                    request.append(req)
                    request.append(self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, False, False, False, 'Roboto', 11, 400, '#999999'))
                    wr_idx += (idx + 2 + 1) 
                    

            self.hwdocs.hwd_batch_update(doc_id, request)
            
            request = []
            if elements_counts[element]:
                req, idx = self.hwdocs.hwd_insert_text(wr_idx, '____________')
                request.append(req)
                request.append(self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, False, False, False, 'Roboto Mono', 10, 400, '#999999'))
                wr_idx += (idx + 2)

                sub_str = ''
                if rec['Type']:
                    sub_str += rec['Type']

                if rec['TypicalTimeSpent']:
                    travel_str = str(rec['TypicalTimeSpent']) + ' mins. typically spent by people'
                    sub_str += travel_str if not len(sub_str) else ', ' + travel_str

                if rec['Kid-friendly']:
                    kids_str = 'Kids friendly'
                    sub_str += kids_str if not len(sub_str) else ', ' + kids_str

                if rec['Amusement-Parks']:
                    a_park = 'Amusement park'
                    sub_str += a_park if not len(sub_str) else ', ' + a_park
              
                if (not math.isnan(rec['Latitude']))  and (not math.isnan(rec['Longitude'])):
                    sun = Sun(rec['Latitude'], rec['Longitude'])
                    sr = sun.get_sunrise_time()
                    ss = sun.get_sunset_time()
                    sr_ss = 'Sunrise {}, Sunset {} UTC'.format(sr.strftime('%H:%M'), ss.strftime('%H:%M'))
                    sub_str += sr_ss if not len(sr_ss) else ', ' + sr_ss

                if len(sub_str):
                    req, idx = self.hwdocs.hwd_insert_text(wr_idx, rec['TopSights'] + '\n' + sub_str)
                    request.append(req)
                    request.append(self.hwdocs.hwd_format_text(wr_idx, wr_idx + len(rec['TopSights']), True, False, False, 'Roboto', 12, 700))
                    request.append(self.hwdocs.hwd_format_text(wr_idx + len(rec['TopSights'] + '\n'), wr_idx + idx, False, False, False, 'Roboto Mono', 10, 300, '#434343'))
                else:
                    req, idx = self.hwdocs.hwd_insert_text(wr_idx, rec['TopSights'])
                    request.append(req)
                    request.append(self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, True, False, False, 'Roboto', 12, 700))
                wr_idx += idx + 2 + 1
            
            else:
                req, idx = self.hwdocs.hwd_insert_text(wr_idx, '\n\n')
                request.append(req)
                req = self.hwdocs.hwd_format_text(wr_idx, wr_idx + idx, False, False, False, 'Roboto Mono', 10, 400, '#434343')
                request.append(req)

        self.hwdocs.hwd_batch_update(doc_id, request)

        #
        # 2. Replace the text with the required values. 
        #
        request.clear()
        request.append(self.hwdocs.hwd_replace_text('country', payload['Country']))
        request.append(self.hwdocs.hwd_replace_text('trip_subtitle', 'Itinerary during the trip'))
        request.append(self.hwdocs.hwd_replace_text('essential_subtitle', 'Information for your smooth trip'))
        request.append(self.hwdocs.hwd_replace_text('when_to_visit', self.hwbase.hwb_country_info_by_field(payload['Country'], 'WhenToVisit')))
        request.append(self.hwdocs.hwd_replace_text('native_currency', self.hwbase.hwb_country_info_by_field(payload['Country'], 'Currency')))
        request.append(self.hwdocs.hwd_replace_text('native_language', self.hwbase.hwb_country_info_by_field(payload['Country'], 'Languages')))
        request.append(self.hwdocs.hwd_replace_text('power_plug', self.hwbase.hwb_country_info_by_field(payload['Country'], 'PlugSocketVoltage')))

        self.hwdocs.hwd_batch_update(doc_id, request)

        msg = payload['Country'].upper() + ' itinearary is created. ' + 'https://docs.google.com/document/d/' + doc_id
        self.logger.info('user-id {0} {1}'.format(payload['Chat_ID'], msg))

        msg = 'Congratulations! Your ' + payload['Country'].upper() + ' itinearary is created. Have a safe trip!\nhttps://docs.google.com/document/d/' + doc_id 
        self.updater.bot.send_message(chat_id=payload['Chat_ID'], text=msg, disable_web_page_preview=False)



    def tbot_create_itinerary_exp_menu(self, query_result, payload):
        """
        Create itinerary will request for few inputs from user and based on it, 
        create travel itinerary document. 
        """
        chat_id = payload.get('chat').get('id')
        sess_data = self.hwdb.hwdb_user_session_select(chat_id)

        experiences = query_result.get('outputContexts')[2].get('parameters').get('experiences')
        country = query_result.get('outputContexts')[2].get('parameters').get('for_country')

        for cat in sess_data['category']:
            self.hwdb.hwdb_user_session_upsert(chat_id, 'NULL', 'NULL', cat, 'NULL', 'D')

        for cat in experiences:
            self.hwdb.hwdb_user_session_upsert(chat_id, country, 'NULL', cat, self.hwbase.hwb_get_continent_for_countries(country), 'I')

        reply_markup = self.tbot_create_itinerary_country_experiences_menu(country, experiences)
        self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nWould you like to add more expereinces to your *' + country.upper() + '* itinerary\n\n', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)



    def tbot_unknown_message(self, query_result, payload):
        """
        These are unknown messages and need to parse them.. 
        """
        chat_id = payload.get('chat').get('id')
        sess_data = self.hwdb.hwdb_user_session_select(chat_id)

        msg = payload.get('text')
        if msg == '/Start':
            self.tbot_start_command(query_result, payload)

        if sess_data['destination'] == 'TELEGRAM_BY_DESTINATION':
            found_dest, df_status, sugg_destinations = self.hwbase.hwb_fuzz_extract(sess_data['continent'], msg, self.hwbase.hwb_all_destinations_per_continent(sess_data['continent']))

            if found_dest and df_status:
                supported_cat, country = self.hwbase.hwb_all_experiences_for_by_destination(sess_data['continent'], found_dest)
                continent = self.hwbase.hwb_get_continent_for_countries(country)
                self.logger.debug('Categories for country/destination {0}/{1} are {2}'.format(found_dest, country, supported_cat))

                self.hwdb.hwdb_user_session_delete(chat_id)
                self.hwdb.hwdb_user_session_upsert(chat_id, country, found_dest, 'NULL', continent, 'I')

                reply_markup = self.tbot_experience_menu(supported_cat)
                self.updater.bot.edit_message_text(chat_id=chat_id, message_id=payload.get('message_id'),
                        text='\n*' + found_dest + '* is in ' + country.upper() + ', has following experiences. '
                        'Once you select the expereinces hit DONE to get your itinerary created.', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
            
            elif found_dest and (not df_status):
                self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nDestination *' + found_dest + '*, but without experiences\n', parse_mode=telegram.ParseMode.MARKDOWN)
            
            else:
                reply_markup = self.tbot_do_you_mean_destinations_menu(sugg_destinations, sess_data['continent'])
                self.updater.bot.sendMessage(chat_id=chat_id,
                        text='\n Do you mean :', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

        else:
            self.logger.debug('Bad message Received : {0}'.format(msg))
            self.updater.bot.sendMessage(chat_id=chat_id, text="\n\nSorry i didn't get it, can you say that again?")


    def tbot_bydestination_message(self, query_result, payload):
        """
        These are unknown messages and need to parse them.. 
        """
        chat_id = payload.get('chat').get('id')
        sess_data = self.hwdb.hwdb_user_session_select(chat_id)

        msg = payload.get('text')

        if sess_data['destination'] == 'TELEGRAM_BY_DESTINATION':
            found_dest, df_status, sugg_destinations = self.hwbase.hwb_fuzz_extract(sess_data['continent'], msg, self.hwbase.hwb_all_destinations_per_continent(sess_data['continent']))

            if found_dest and df_status:
                supported_cat, country = self.hwbase.hwb_all_experiences_for_by_destination(sess_data['continent'], found_dest)
                continent = self.hwbase.hwb_get_continent_for_countries(country)
                self.logger.debug('Categories for country/destination {0}/{1} are {2}'.format(found_dest, country, supported_cat))

                self.hwdb.hwdb_user_session_delete(chat_id)
                self.hwdb.hwdb_user_session_upsert(chat_id, country, found_dest, 'NULL', continent, 'I')

                reply_markup = self.tbot_experience_menu(supported_cat)
                self.updater.bot.sendMessage(chat_id=chat_id, message_id=payload.get('message_id'),
                        text='\n*' + found_dest + '* is in ' + country.upper() + ', has following experiences. '
                        'Once you select the expereinces hit DONE to get your itinerary created.', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
            
            elif found_dest and (not df_status):
                self.updater.bot.sendMessage(chat_id=chat_id, text='\n\nDestination *' + found_dest + '*, but without experiences\n', parse_mode=telegram.ParseMode.MARKDOWN)
            
            else:
                reply_markup = self.tbot_do_you_mean_destinations_menu(sugg_destinations, sess_data['continent'])
                self.updater.bot.sendMessage(chat_id=chat_id,
                        text='\n Do you mean :', reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)


        else:
            self.logger.debug('Bad message Received : {0}'.format(msg))
            self.updater.bot.sendMessage(chat_id=chat_id, text="\n\nSorry i didn't get it, can you say that again?")


    #############################
    # Normal Intent Table
    #############################
    normalIntents = {
            'input.unknown' : tbot_unknown_message,
            'input.cb_welcome' : tbot_start_command,
            'settings.country-name' : tbot_user_settings,
            'input.pick_continent' : tbot_continent_menu,
            'create_itinerary.ci_travel_date.ci_people': tbot_create_itinerary_exp_menu,
            'input.bydestination': tbot_bydestination_message
    }


    def tbot_call_normal_intents_methods(self, query_result, payload):
        action = query_result.get('action')
        f = lambda self, a, qr, p : self.normalIntents.get(a, lambda a, qr, p : self.tbot_default_method(qr, p))(self, qr, p)
        f(self, action, query_result, payload)



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
            #self.normalIntents.get(query_result.get('action'), lambda : self.default())()
            self.tbot_process_telegram_intents(query_result, payload)


