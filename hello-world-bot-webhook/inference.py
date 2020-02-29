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

        # EUROPE Dataframes
        self.df_dest_europe = pd.read_csv('data/europe/Destination_1_1.csv', low_memory=False, encoding='utf-8')
        self.df_tsights_europe = pd.read_csv('data/europe/TopSights_1_1.csv', low_memory=False, encoding='utf-8')

        # ASIA Dataframes
        self.df_dest_asia = pd.read_csv('data/asia/Destination_1_0.csv', low_memory=False, encoding='utf-8')
        self.df_tsights_asia = pd.read_csv('data/asia/TopSights_1_0.csv', low_memory=False, encoding='utf-8')

        # Months, PopularTimes, LonelyPlanet
        self.df_month_data = pd.read_csv(self.home + 'data/Months_1_0.csv', low_memory=False, encoding='utf-8')
        self.df_country_info = pd.read_csv(self.home + 'data/country_info_v1.0.csv', low_memory=False, encoding='utf-8')
        self.df_lp_url = pd.read_csv(self.home + 'data/LP_urls_v1.0.csv', low_memory=False, encoding='utf-8')

        # Init functions.
        self.hwb_month_data_preprocessing()
        self.df_dest_europe, self.df_tsights_europe = self.hwb_dataframe_processing(self.df_dest_europe, self.df_tsights_europe)
        self.df_dest_asia, self.df_tsights_asia = self.hwb_dataframe_processing(self.df_dest_asia, self.df_tsights_asia)

        # List of countries
        self.EUROPE_COUNTRIES = self.df_dest_europe.Country.unique().tolist() 
        self.AISA_COUNTRIES = self.df_dest_asia.Country.unique().tolist()


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


    def hwb_month_data_preprocessing(self):
        # Clean 'degree' and 'Precipitation' special characters.

        self.df_month_data['MinTemp'] = self.df_month_data['MinTemp'].replace('\u00b0','', regex=True)
        self.df_month_data['MinTemp'] = pd.to_numeric(self.df_month_data['MinTemp'])
        self.df_month_data['MaxTemp'] = self.df_month_data['MaxTemp'].replace('\u00b0','', regex=True)
        self.df_month_data['MaxTemp'] = pd.to_numeric(self.df_month_data['MaxTemp'])
        self.df_month_data['Precipitation'] = self.df_month_data['Precipitation'].replace('%','', regex=True)
        self.df_month_data['Precipitation'] = pd.to_numeric(self.df_month_data['Precipitation'])


    def hwb_dataframe_processing(self, df_dest, df_tsights):
        #
        # 1. Destination Data
        #

        # Rename is the columns.

        df_dest.rename(columns={'Outdoor Recreation':'OutdoorRecreation', 'National Parks':'NationalParks',
                     'Coral reef':'CoralReef', 'Winter sports':'WinterSports', 'Nature reserve':'NatureReserve', 'Scuba diving':'ScubaDiving',
                     'Whale watching':'WhaleWatching', 'Polar bear':'PolarBear', 'Hot spring':'HotSpring', 'Autumn leaf color':'AutumnLeafColor',
                     'Wine tasting':'WineTasting', 'Bungee jumping':'BungeeJumping', 'Whale shark':'WhaleShark', 'Alpine skiing':'AlpineSkiing',
                     'Historic site':'HistoricSite'}, inplace=True)

        # FIXME: Remove unwated space in the country columns.
        df_dest['Country'] = df_dest['Country'].astype(str)
        df_dest['Country'] = df_dest.Country.apply(lambda x: x.replace(' ',''))
        df_dest['Country'] = df_dest['Country'].astype('category')

        # Convert to booleans
        df_dest.Architecture = df_dest.Architecture == 'yes'
        df_dest.Nature = df_dest.Nature == 'yes'
        df_dest.Shopping = df_dest.Shopping == 'yes'
        df_dest.Fishing = df_dest.Fishing == 'yes'
        df_dest.Hiking = df_dest.Hiking == 'yes'
        df_dest.OutdoorRecreation = df_dest.OutdoorRecreation == 'yes'
        df_dest.Adventure = df_dest.Adventure == 'yes'
        df_dest.Beaches = df_dest.Beaches == 'yes'
        df_dest.Camping = df_dest.Camping == 'yes'
        df_dest.Caves = df_dest.Caves == 'yes'
        df_dest.Museums = df_dest.Museums == 'yes'
        df_dest.NationalParks = df_dest.NationalParks == 'yes'
        df_dest.Art = df_dest.Art == 'yes'
        df_dest.Desert = df_dest.Desert == 'yes'
        df_dest.CoralReef = df_dest.CoralReef == 'yes'
        df_dest.Skiing = df_dest.Skiing == 'yes'
        df_dest.Snowboarding = df_dest.Snowboarding == 'yes'
        df_dest.WinterSports = df_dest.WinterSports == 'yes'
        df_dest.Wildlife = df_dest.Wildlife == 'yes'
        df_dest.Penguin = df_dest.Penguin == 'yes'
        df_dest.Glacier = df_dest.Glacier == 'yes'
        df_dest.Ecotourism = df_dest.Ecotourism == 'yes'
        df_dest.Snorkeling = df_dest.Snorkeling == 'yes'
        df_dest.Koala = df_dest.Koala == 'yes'
        df_dest.Surfing = df_dest.Surfing == 'yes'
        df_dest.NatureReserve = df_dest.NatureReserve == 'yes'
        df_dest.Volcano = df_dest.Volcano == 'yes'
        df_dest.Sailing = df_dest.Sailing == 'yes'
        df_dest.ScubaDiving = df_dest.ScubaDiving == 'yes'
        df_dest.Theaters = df_dest.Theaters == 'yes'
        df_dest.Elephant = df_dest.Elephant == 'yes'
        df_dest.Safari = df_dest.Safari == 'yes'
        df_dest.Jaguar = df_dest.Jaguar == 'yes'
        df_dest.Casinos = df_dest.Casinos == 'yes'
        df_dest.Kitesurfing = df_dest.Kitesurfing == 'yes'
        df_dest.Windsurfing = df_dest.Windsurfing == 'yes'
        df_dest.Birdwatching = df_dest.Birdwatching == 'yes'
        df_dest.Rainforest = df_dest.Rainforest == 'yes'
        df_dest.Nightlife = df_dest.Nightlife == 'yes'
        df_dest.WhaleWatching = df_dest.WhaleWatching == 'yes'
        df_dest.Reindeer = df_dest.Reindeer == 'yes'
        df_dest.Gorilla = df_dest.Gorilla == 'yes'
        df_dest.Kayaking = df_dest.Kayaking == 'yes'
        df_dest.PolarBear = df_dest.PolarBear == 'yes'
        df_dest.HotSpring = df_dest.HotSpring == 'yes'
        df_dest.Tiger = df_dest.Tiger == 'yes'
        df_dest.Yoga = df_dest.Yoga == 'yes'
        df_dest.Orangutan = df_dest.Orangutan == 'yes'
        df_dest.Golf = df_dest.Golf == 'yes'
        df_dest.Rafting = df_dest.Rafting == 'yes'
        df_dest.AutumnLeafColor = df_dest.AutumnLeafColor == 'yes'
        df_dest.Dolphin = df_dest.Dolphin == 'yes'
        df_dest.WineTasting = df_dest.WineTasting == 'yes'
        df_dest.Climbing = df_dest.Climbing == 'yes'
        df_dest.Paragliding = df_dest.Paragliding == 'yes'
        df_dest.BungeeJumping = df_dest.BungeeJumping == 'yes'
        df_dest.WhaleShark = df_dest.WhaleShark == 'yes'
        df_dest.AlpineSkiing = df_dest.AlpineSkiing == 'yes'
        df_dest.HistoricSite = df_dest.HistoricSite == 'yes'

        # Drop constant columns.
        df_dest = self.hwb_drop_constant_value_column(df_dest)

        # Convert 'NaN' to empty string
        #df_dest['Description'] = df_dest.Description.fillna('')


        #
        # 2. Top Sights Data
        #

        # FIXME: Remove unwated space in the country columns.
        df_tsights['Country'] = df_tsights['Country'].astype(str)
        df_tsights['Country'] = df_tsights.Country.apply(lambda x: x.replace(' ',''))
        df_tsights['Country'] = df_tsights['Country'].astype('category')

        # Convert all to mins.
        df_tsights['TypicalTimeSpent'] = df_tsights['TypicalTimeSpent'].astype(str)
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.split('-').apply(self.hwb_split_and_pick_right, position=1)
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.split('to').apply(self.hwb_split_and_pick_right, position=1)
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.replace('hour', 'hours')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.replace('hr', 'hours')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.replace(' min', '')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.replace('(', '')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.replace(')', '')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.str.split(' hours').apply(self.hwb_mul, position=0)
        df_tsights['TypicalTimeSpent'] = df_tsights['TypicalTimeSpent'].astype(float)

        # Delete the rows where 'Rating' and 'Reviews' are not given.
        df_tsights = df_tsights[pd.notnull(df_tsights['Rating'])]
        df_tsights = df_tsights[pd.notnull(df_tsights['NumberOfReview'])]

        # Clean NumberOfReviews column
        df_tsights['NumberOfReview'] = df_tsights['NumberOfReview'].astype(str)
        df_tsights['NumberOfReview'] = df_tsights.NumberOfReview.apply(lambda x: x.replace(',',''))
        df_tsights['NumberOfReview'] = df_tsights.NumberOfReview.apply(lambda x: x.replace('-',''))
        df_tsights['NumberOfReview'] = df_tsights.NumberOfReview.apply(lambda x: x.replace('(',''))
        df_tsights['NumberOfReview'] = df_tsights.NumberOfReview.apply(lambda x: x.replace(')',''))
        df_tsights['NumberOfReview'] = df_tsights['NumberOfReview'].astype(float)

        # Drop 'zero' value columns
        df_tsights = self.hwb_drop_zero_value_column(df_tsights)

        # Convert 'NaN' to empty string
        df_tsights['Description'] = df_tsights.Description.fillna('')

        # FIXME: what should be the typical default time to set? for now its 30 mins.
        #df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.fillna(df_tsights.TypicalTimeSpent.mean())
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.fillna(30)


        # Substitute features with 'OptionsX' from top sights data.
        tsights_flist = []

        tsights_flist = df_tsights.columns.unique().tolist()
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
          df_tsights[ops] = df_tsights[ops].astype(str)
          features = df_tsights[ops].unique().tolist()
          features = [x for x in features if x != 'nan']
          self.ts_experiences.extend(list(set(features) - set(self.ts_experiences)))

        # Set all new columns to 'False'
        for ops in self.ts_experiences:
          df_tsights[ops] = False

        # Set respective columns.
        for ops in self.ts_experiences:
          for f in tsights_flist:
            df_tsights.loc[df_tsights[f] == ops, ops] = True

        # Drop all the 'OptionX' columns from DF.
        df_tsights.drop(tsights_flist, axis=1, inplace=True)

        logger.debug('Destination DF shape {0}'.format(df_dest.shape))
        logger.debug('TopSights DF Shape {0}'.format(df_tsights.shape))

        if HW_DEBUG:
            display(df_dest.head())
            display(DataFrameSummary(df_dest).summary())

        return df_dest, df_tsights


    def hwb_all_countries(self, continent):
        """
        Return list of all the supported countries.
        """

        if continent == 'Europe':
            return self.EUROPE_COUNTRIES
        elif continent == 'Asia':
            return self.AISA_COUNTRIES


    def hwb_get_continent_for_countries(self, country):
        """
        Return list of all the supported countries.
        """

        if country in self.EUROPE_COUNTRIES:
            return 'Europe'
        elif country in self.AISA_COUNTRIES:
            return 'Asia'
        else:
            logger.error('Invalid country name!')



    def hwb_all_experiences(self, continent):
        """
        Return all the columns in destination.csv.
        """
       
        exp = list(eval('self.df_dest_' + continent.lower() + '.columns.values'))
        exp.remove('Country')
        exp.remove('Destination')
        exp.remove('Description')
        exp.remove('Rank')
        return exp


    def hwb_all_experiences_for_a_country(self, country):
        """
        Return all the categories for a country.
        """
        continent = self.hwb_get_continent_for_countries(country)
        df_var = eval('self.df_dest_' + continent.lower())
        df_country = df_var[df_var['Country'] == country]
        df_country = self.hwb_drop_constant_value_column(df_country)
        df_country = df_country.drop(['Destination', 'Description', 'Rank'], axis=1)
        return list(df_country.columns.values)


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


    def hwb_experience_combinations(self, continent, experience, exp_len):
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

        df_var = eval('self.df_dest_' + continent.lower())
        for i in range(len(top)):
            if len(top[i]) and (len(top3) < 3):
                c_list = list(set(self.hwb_all_experiences(continent)) - set(list(top[i])))
                df_tmp = df_var[(df_var[c_list] == False).all(axis=1) & (df_var[list(top[i])] == True).all(axis=1)]
                if not df_tmp.empty:
                    top3.append(top[i])

        return top3


    def hwb_find_top_countries_for_experiences(self, continent, experiences):
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
        if not (set(self.hwb_all_experiences(continent)) & set(experiences)):
            return ret_suggestions, ret_data, 400

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        df_var = eval('self.df_dest_' + continent.lower())
        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences(continent)) - set(subcat))
                df_local = df_var[(df_var[c_list] == False).all(axis=1) & (df_var[subcat] == True).all(axis=1)]
                if HW_DEBUG:
                    display(df_local.head())

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_experience_combinations(continent, subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top 3 expereinces suggestions to user {0} | {1} | {2}'.format(list(top_sugg[0]), list(top_sugg[1]), list(top_sugg[2])))
                    err = 204

                else:
                    payload = {}
                    # Find top countries but not ordered.
                    df_local = df_local.sort_values(['Rank'], ascending=False)
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
        continent = self.hwb_get_continent_for_countries(country)
        if not (set(self.hwb_all_experiences(continent)) & set(experiences)):
            return ret_suggestions, ret_data, 400

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        logger.debug('Continent {0} Country {1} experience {2}'.format(continent, country, experiences))
        df_var = eval('self.df_dest_' + continent.lower())
        df_local = df_var[df_var['Country'] == country]

        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences(continent)) - set(subcat))
                df_local = df_local[(df_local[c_list] == False).all(axis=1) & (df_local[subcat] == True).all(axis=1)]

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_experience_combinations(continent, subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top expereinces suggestions to user {0}'.format(list(top_sugg[0])))
                    err = 204

                else:
                    payload = {}
                    payload['Country'] = country
                    payload['Experiences'] = subcat
                    # Sort destination based on the ranking.
                    df_local = df_local.sort_values(['Rank'], ascending=False)
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


