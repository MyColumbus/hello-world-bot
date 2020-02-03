# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import pandas as pd

import logging
import sys
import pytz
import json
from datetime import datetime
from itertools import combinations

from hw_docs.hw_drive_auth import HWDocs

from logs import HWLogs
HWLogs(logging.DEBUG)
logger = logging.getLogger()


HW_DEBUG = 0
BATCH_SZ = 1

if HW_DEBUG:
    from IPython.display import display
    from pandas_summary import DataFrameSummary
    pd.set_option('display.max_columns', 70)


#
# Globals
#
BATCH_SIZE = 3
IMAGE_HOSTING_URL = 'http://127.0.0.1/dest-images/'


class HWBase:
    outdoors = ['OutdoorRecreation','Hiking','Golf','Rafting','Fishing','Kayaking','Camping','Snorkeling']
    adventures = ['Adventure','Skiing','Snowboarding','WinterSports','Surfing','Sailing','ScubaDiving',
             'Kitesurfing',  'Windsurfing','Climbing','Paragliding','BungeeJumping','AlpineSkiing','CoralReef']
    parks =  ['NationalParks','Wildlife','Elephant','Safari','Jaguar','WhaleWatching','Reindeer','Gorilla',
             'PolarBear','Tiger','Dolphin','WhaleShark','Penguin','Orangutan','Koala']
    beautiful_nature = ['Nature','Desert','Caves','Glacier','NatureReserve','Volcano','Birdwatching',
             'Rainforest','HotSpring','Beaches','AutumnLeafColor']
    arts_culture = ['Art','Museums','Theaters','Yoga','HistoricSite','Architecture']
    social = ['Casinos','Nightlife','WineTasting','Shopping']
    eco_torisum = ['Ecotourism']

    def __init__(self):
        """
        HWBase class constructor.
        """
        self.home = ''
        self.ts_experiences = []

        self.EUROPE = []
        self.ASIA = ['India', 'Malaysia', 'SriLanka', 'Bhutan', 'Indonesia', 'Myanmar', 'Nepal', 'Singapore', 'Thailand', 'UnitedArabEmirates', 'Vietnam']

        self.df_dest = pd.read_csv('data/Destination_v0.1.csv', low_memory=False, encoding='utf-8')
        self.df_tsights = pd.read_csv('data/TopSights_v0.1.csv', low_memory=False, encoding='utf-8')

        self.df_month_data = pd.read_csv(self.home + 'data/Months_v1.0.csv', low_memory=False, encoding='utf-8')
        self.df_country_info = pd.read_csv(self.home + 'data/country_info_v1.0.csv', low_memory=False, encoding='utf-8')
        self.df_lp_url = pd.read_csv(self.home + 'data/LP_urls_v1.0.csv', low_memory=False, encoding='utf-8')

        # Init functions.
        self.hwb_dataframe_processing()

    def hwb_drop_constant_value_column(self, dataframe):
        """
        Drops constant value columns of pandas dataframe.
        """
        return dataframe.loc[:, dataframe.apply(pd.Series.nunique) != 1]


    def hwb_drop_zero_value_column(self, dataframe):
        """
        Drops 'zero' value columns of pandas dataframe.
        """
        return dataframe.loc[:, dataframe.apply(pd.Series.nunique) != 0]


    def hwb_split_and_pick_right(self, list, position):
        """
        Split and pick the right side.
        """
        if type(list) == float:
            return list
        else:
            if len(list) == 1:
                return list[0]
            else:
                return list[position]


    def hwb_mul(self, x, position):
        """
        Convert hours to mins
        """
        if type(x) == float:
            return x
        else:
            if len(x) == 1:
                return x[0]
            else:
                return float(x[position]) * 60


    def hwb_dataframe_processing(self):

        #
        # 1. Month data
        #
        # Clean 'degree' and 'Precipitation' special characters.

        self.df_month_data['MinTemp'] = self.df_month_data['MinTemp'].replace('\u00b0','', regex=True)
        self.df_month_data['MinTemp'] = pd.to_numeric(self.df_month_data['MinTemp'])
        self.df_month_data['MaxTemp'] = self.df_month_data['MaxTemp'].replace('\u00b0','', regex=True)
        self.df_month_data['MaxTemp'] = pd.to_numeric(self.df_month_data['MaxTemp'])
        self.df_month_data['Precipitation'] = self.df_month_data['Precipitation'].replace('%','', regex=True)
        self.df_month_data['Precipitation'] = pd.to_numeric(self.df_month_data['Precipitation'])


        #
        # 2. Destination Data
        #
        # Rename is the columns.

        self.df_dest.rename(columns={'Outdoor Recreation':'OutdoorRecreation', 'National Parks':'NationalParks',
                     'Coral reef':'CoralReef', 'Winter sports':'WinterSports', 'Nature reserve':'NatureReserve', 'Scuba diving':'ScubaDiving',
                     'Whale watching':'WhaleWatching', 'Polar bear':'PolarBear', 'Hot spring':'HotSpring', 'Autumn leaf color':'AutumnLeafColor',
                     'Wine tasting':'WineTasting', 'Bungee jumping':'BungeeJumping', 'Whale shark':'WhaleShark', 'Alpine skiing':'AlpineSkiing',
                     'Historic site':'HistoricSite'}, inplace=True)

        # FIXME: Remove unwated space in the country columns.
        self.df_dest['Country'] = self.df_dest['Country'].astype(str)
        self.df_dest['Country'] = self.df_dest.Country.apply(lambda x: x.replace(' ',''))
        self.df_dest['Country'] = self.df_dest['Country'].astype('category')

        # Convert to booleans
        self.df_dest.Architecture = self.df_dest.Architecture == 'yes'
        self.df_dest.Nature = self.df_dest.Nature == 'yes'
        self.df_dest.Shopping = self.df_dest.Shopping == 'yes'
        self.df_dest.Fishing = self.df_dest.Fishing == 'yes'
        self.df_dest.Hiking = self.df_dest.Hiking == 'yes'
        self.df_dest.OutdoorRecreation = self.df_dest.OutdoorRecreation == 'yes'
        self.df_dest.Adventure = self.df_dest.Adventure == 'yes'
        self.df_dest.Beaches = self.df_dest.Beaches == 'yes'
        self.df_dest.Camping = self.df_dest.Camping == 'yes'
        self.df_dest.Caves = self.df_dest.Caves == 'yes'
        self.df_dest.Museums = self.df_dest.Museums == 'yes'
        self.df_dest.NationalParks = self.df_dest.NationalParks == 'yes'
        self.df_dest.Art = self.df_dest.Art == 'yes'
        self.df_dest.Desert = self.df_dest.Desert == 'yes'
        self.df_dest.CoralReef = self.df_dest.CoralReef == 'yes'
        self.df_dest.Skiing = self.df_dest.Skiing == 'yes'
        self.df_dest.Snowboarding = self.df_dest.Snowboarding == 'yes'
        self.df_dest.WinterSports = self.df_dest.WinterSports == 'yes'
        self.df_dest.Wildlife = self.df_dest.Wildlife == 'yes'
        self.df_dest.Penguin = self.df_dest.Penguin == 'yes'
        self.df_dest.Glacier = self.df_dest.Glacier == 'yes'
        self.df_dest.Ecotourism = self.df_dest.Ecotourism == 'yes'
        self.df_dest.Snorkeling = self.df_dest.Snorkeling == 'yes'
        self.df_dest.Koala = self.df_dest.Koala == 'yes'
        self.df_dest.Surfing = self.df_dest.Surfing == 'yes'
        self.df_dest.NatureReserve = self.df_dest.NatureReserve == 'yes'
        self.df_dest.Volcano = self.df_dest.Volcano == 'yes'
        self.df_dest.Sailing = self.df_dest.Sailing == 'yes'
        self.df_dest.ScubaDiving = self.df_dest.ScubaDiving == 'yes'
        self.df_dest.Theaters = self.df_dest.Theaters == 'yes'
        self.df_dest.Elephant = self.df_dest.Elephant == 'yes'
        self.df_dest.Safari = self.df_dest.Safari == 'yes'
        self.df_dest.Jaguar = self.df_dest.Jaguar == 'yes'
        self.df_dest.Casinos = self.df_dest.Casinos == 'yes'
        self.df_dest.Kitesurfing = self.df_dest.Kitesurfing == 'yes'
        self.df_dest.Windsurfing = self.df_dest.Windsurfing == 'yes'
        self.df_dest.Birdwatching = self.df_dest.Birdwatching == 'yes'
        self.df_dest.Rainforest = self.df_dest.Rainforest == 'yes'
        self.df_dest.Nightlife = self.df_dest.Nightlife == 'yes'
        self.df_dest.WhaleWatching = self.df_dest.WhaleWatching == 'yes'
        self.df_dest.Reindeer = self.df_dest.Reindeer == 'yes'
        self.df_dest.Gorilla = self.df_dest.Gorilla == 'yes'
        self.df_dest.Kayaking = self.df_dest.Kayaking == 'yes'
        self.df_dest.PolarBear = self.df_dest.PolarBear == 'yes'
        self.df_dest.HotSpring = self.df_dest.HotSpring == 'yes'
        self.df_dest.Tiger = self.df_dest.Tiger == 'yes'
        self.df_dest.Yoga = self.df_dest.Yoga == 'yes'
        self.df_dest.Orangutan = self.df_dest.Orangutan == 'yes'
        self.df_dest.Golf = self.df_dest.Golf == 'yes'
        self.df_dest.Rafting = self.df_dest.Rafting == 'yes'
        self.df_dest.AutumnLeafColor = self.df_dest.AutumnLeafColor == 'yes'
        self.df_dest.Dolphin = self.df_dest.Dolphin == 'yes'
        self.df_dest.WineTasting = self.df_dest.WineTasting == 'yes'
        self.df_dest.Climbing = self.df_dest.Climbing == 'yes'
        self.df_dest.Paragliding = self.df_dest.Paragliding == 'yes'
        self.df_dest.BungeeJumping = self.df_dest.BungeeJumping == 'yes'
        self.df_dest.WhaleShark = self.df_dest.WhaleShark == 'yes'
        self.df_dest.AlpineSkiing = self.df_dest.AlpineSkiing == 'yes'
        self.df_dest.HistoricSite = self.df_dest.HistoricSite == 'yes'

        # Drop constant columns.
        self.df_dest = self.hwb_drop_constant_value_column(self.df_dest)

        # Convert 'NaN' to empty string
        self.df_dest['Description'] = self.df_dest.Description.fillna('')

        #
        # 3. Top Sights Data
        #

        # FIXME: Remove unwated space in the country columns.
        self.df_tsights['Country'] = self.df_tsights['Country'].astype(str)
        self.df_tsights['Country'] = self.df_tsights.Country.apply(lambda x: x.replace(' ',''))
        self.df_tsights['Country'] = self.df_tsights['Country'].astype('category')

        # Convert all to mins.
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights['TypicalTimeSpent'].astype(str)
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.split('-').apply(self.hwb_split_and_pick_right, position=1)
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.split('to').apply(self.hwb_split_and_pick_right, position=1)
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.replace('hour', 'hours')
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.replace('hr', 'hours')
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.replace(' min', '')
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.replace('(', '')
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.replace(')', '')
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.str.split(' hours').apply(self.hwb_mul, position=0)
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights['TypicalTimeSpent'].astype(float)

        # Delete the rows where 'Rating' and 'Reviews' are not given.
        self.df_tsights = self.df_tsights[pd.notnull(self.df_tsights['Rating'])]
        self.df_tsights = self.df_tsights[pd.notnull(self.df_tsights['NumberOfReview'])]

        # Clean NumberOfReviews column
        self.df_tsights['NumberOfReview'] = self.df_tsights['NumberOfReview'].astype(str)
        self.df_tsights['NumberOfReview'] = self.df_tsights.NumberOfReview.apply(lambda x: x.replace(',',''))
        self.df_tsights['NumberOfReview'] = self.df_tsights.NumberOfReview.apply(lambda x: x.replace('-',''))
        self.df_tsights['NumberOfReview'] = self.df_tsights.NumberOfReview.apply(lambda x: x.replace('(',''))
        self.df_tsights['NumberOfReview'] = self.df_tsights.NumberOfReview.apply(lambda x: x.replace(')',''))
        self.df_tsights['NumberOfReview'] = self.df_tsights['NumberOfReview'].astype(float)

        # Drop 'zero' value columns
        self.df_tsights = self.hwb_drop_zero_value_column(self.df_tsights)

        # Convert 'NaN' to empty string
        self.df_tsights['Description'] = self.df_tsights.Description.fillna('')

        # FIXME: what should be the typical default time to set? for now its 30 mins.
        #self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.fillna(self.df_tsights.TypicalTimeSpent.mean())
        self.df_tsights['TypicalTimeSpent'] = self.df_tsights.TypicalTimeSpent.fillna(30)


        # Substitute features with 'OptionsX' from top sights data.
        tsights_flist = []

        tsights_flist = self.df_tsights.columns.unique().tolist()
        tsights_flist.remove('Country')
        tsights_flist.remove('Destination')
        tsights_flist.remove('TopSight')
        tsights_flist.remove('Description')
        tsights_flist.remove('Rating')
        tsights_flist.remove('NumberOfReview')
        tsights_flist.remove('Type')
        tsights_flist.remove('TypicalTimeSpent')
        tsights_flist.remove('Latitude')
        tsights_flist.remove('Longitude')

        for ops in tsights_flist:
          features = []
          self.df_tsights[ops] = self.df_tsights[ops].astype(str)
          features = self.df_tsights[ops].unique().tolist()
          features = [x for x in features if x != 'nan']
          self.ts_experiences.extend(list(set(features) - set(self.ts_experiences)))

        # Set all new columns to 'False'
        for ops in self.ts_experiences:
          self.df_tsights[ops] = False

        # Set respective columns.
        for ops in self.ts_experiences:
          for f in tsights_flist:
            self.df_tsights.loc[self.df_tsights[f] == ops, ops] = True

        # Drop all the 'OptionX' columns from DF.
        self.df_tsights.drop(tsights_flist, axis=1, inplace=True)


        logger.debug('Destination DF shape {0}'.format(self.df_dest.shape))
        logger.debug('TopSights DF Shape {0}'.format(self.df_tsights.shape))

        if HW_DEBUG:
            display(self.df_dest.head())
            display(DataFrameSummary(self.df_dest).summary())


    def hwb_all_experiences(self):
        """
        Return all the columns in destination.csv.
        """
        exp = list(self.df_dest.columns.values)
        exp.remove('Country')
        exp.remove('Destination')
        exp.remove('Description')
        return exp


    def hwb_all_experiences_for_a_country(self, country):
        """
        Return all the categories for a country.
        """

        df_country = self.df_dest[self.df_dest['Country'] == country]
        df_country = self.hwb_drop_constant_value_column(df_country)
        df_country = df_country.drop(['Destination', 'Destination'], axis=1)
        return list(df_country.columns.values)


    def hwb_all_countries(self, continent):
        """
        Return list of all the supported countries.
        """

        if continent == 'EUROPE':
            return self.EUROPE
        elif continent == 'ASIA':
            return self.ASIA


    def hwb_fetch_subexp_to_exp(self, experiences):
        """
        Return subcategories list wise categories list.
        """
        list_of_list = {}

        list_of_list['outdoors'] = list(set(experiences) & set(self.outdoors))
        list_of_list['adventures'] = list(set(experiences) & set(self.adventures))
        list_of_list['parks'] = list(set(experiences) & set(self.parks))
        list_of_list['beautiful_nature'] = list(set(experiences) & set(self.beautiful_nature))
        list_of_list['arts_culture'] = list(set(experiences) & set(self.arts_culture))
        list_of_list['social'] = list(set(experiences) & set(self.social))
        list_of_list['eco_torisum'] = list(set(experiences) & set(self.eco_torisum))

        return list_of_list


    def hwb_populate_information_data(self, country, destination):
        """
        Populate additional information
        Like: FileURL, Month, PopularTimes, etc.
        """
        df_tmp = self.df_month_data[(self.df_month_data['Country'] == country) & (self.df_month_data['Destination'] == destination)]
        df_tmp = df_tmp.drop(['Country', 'Destination'], axis=1)

        info_dict = {}
        for _, row in df_tmp.iterrows():
            info_dict[row['Month']] = {"Popularity" : json.dumps(row['Popularity']),
                                       "MinTemp": json.dumps(row['MinTemp']),
                                       "MaxTemp" : json.dumps(row['MaxTemp']),
                                       "Precipitation" : json.dumps(row['Precipitation'])}

        return info_dict


    def hwb_country_info_by_field(self, country, field):
        """
        Return value for a specific input field.
        """
        return self.df_country_info.loc[self.df_country_info['Country'] == country, field].iloc[0]


    def hwb_lonely_planet_urls(self, country, destination):
        """
        Return Lonely Planet URL for a input country and destination.
        """
        try:
            return self.df_lp_url.loc[(self.df_lp_url['Country'] == country) & (self.df_lp_url['Destination'] == destination), 'lp_URL'].iloc[0]
        except:
            return ''


    def hwb_experience_combinations(self, experience, exp_len):
        """
        When user experiences are not found in the dataset, in that case we can suggest possible combinations for a given
        list of experiences as suggestion to
        """
        top = []
        top3 = []

        for elen in range(exp_len, -1, -1):
            comb = combinations(experience, elen)
            elist = []
            elist = list(comb)
            for i in range(len(elist)):
                top.append(elist[i])

        for i in range(len(top)):
            if len(top[i]) and (len(top3) < 3):
                c_list = list(set(self.hwb_all_experiences()) - set(list(top[i])))
                df_tmp = self.df_dest[(self.df_dest[c_list] == False).all(axis=1) & (self.df_dest[list(top[i])] == True).all(axis=1)]
                if not df_tmp.empty:
                    top3.append(top[i])

        return top3


    def hwb_find_top_countries_for_experiences(self, experiences):
        """
        Find any countries for matching experience(s).
        The logic is as follows:
            1. Match Sub-experiences (All)
            2. Suggest the possible experiences to user (not matched 'all')
        """
        ret_data = []
        ret_suggestions = []
        err = 200

        # Sanity checks:
        if not (set(self.hwb_all_experiences()) & set(experiences)):
            return ret_suggestions, ret_data, 400

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences()) - set(subcat))
                df_local = self.df_dest[(self.df_dest[c_list] == False).all(axis=1) & (self.df_dest[subcat] == True).all(axis=1)]
                if HW_DEBUG:
                    display(df_local.head())

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_experience_combinations(subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top 3 expereinces suggestions to user {0} | {1} | {2}'.format(list(top_sugg[0]), list(top_sugg[1]), list(top_sugg[2])))
                    err = 204

                else:
                    payload = {}
                    # Find top countries but not ordered.
                    #df_local = df_local.sort_values(['Rank'], ascending=False)
                    top_countries = df_local.Country.unique().tolist()
                    logger.debug('Countries {0} experiences {1}'.format(top_countries, subcat))
                    payload['Countries'] = top_countries
                    payload['Experiences'] = subcat
                    ret_data.append(payload)

        return ret_suggestions, ret_data, err



    def hwb_find_destination_for_experiences(self, country, experiences):
        """
        Find any countries for matching experience(s).
        The logic is as follows:
            1. Match Sub-experiences (All)
            2. Suggest the possible experiences to user (not matched 'all')
        """
        ret_data = []
        ret_suggestions = []
        err = 200

        # Sanity checks:
        if not (set(self.hwb_all_experiences()) & set(experiences)):
            return ret_suggestions, ret_data, 400

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        logger.debug('Country {0} experience {1}'.format(country, experiences))
        df_local = self.df_dest[self.df_dest['Country'] == country]

        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences()) - set(subcat))
                df_local = df_local[(df_local[c_list] == False).all(axis=1) & (df_local[subcat] == True).all(axis=1)]

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_experience_combinations(subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top expereinces suggestions to user {0}'.format(list(top_sugg[0])))
                    err = 204

                else:
                    payload = {}
                    payload['Country'] = country
                    payload['Experiences'] = subcat
                    # Sort destination based on the ranking.
                    #df_local = df_local.sort_values(['Rank'], ascending=False)
                    dest_list = df_local.Destination.unique().tolist()
                    logger.debug('Destination list : {0}'.format(dest_list))
                    payload['Destination'] = dest_list[:(BATCH_SZ * 3)]
                    ret_data.append(payload)

        return ret_suggestions, ret_data, err


#hwbase = HWBase()
#exp = ['Nature', 'Beaches', 'Desert', 'Yoga']
#top_s, data, err = hwbase.hwb_find_top_countries_for_experiences(exp)
#logger.debug('Data {0}'.format(data))
#logger.debug('Suggestions {0}'.format(top_s))
#logger.debug('========================')
#top_s, data, err = hwbase.hwb_find_destination_for_experiences(data[0]['Countries'][0], data[0]['Experiences'])
#logger.debug('Destionation_for_exp {0}'.format(data))


#if __name__ == '__main__':
#
#    # Error serveiry
#     HWLogs(40)

#     hwbase = HWBase()
#     exp = ['Nature', 'Beaches', 'Desert', 'Yoga']
#     top_s, data, err = hwbase.hwb_find_top_countries_for_experiences(exp)
#     print('Data {0}'.format(data))
#     print('Suggestions {0}'.format(top_s))
#     print('========================')
#     top_s, data, err = hwbase.hwb_find_destination_for_experiences(data[0]['Countries'][0], data[0]['Experiences'])
#     print('Destionation_for_exp {0}'.format(data))


