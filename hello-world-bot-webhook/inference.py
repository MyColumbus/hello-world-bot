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
from fuzzywuzzy import process

from logs import HWLogs
HWLogs(logging.DEBUG)
logger = logging.getLogger()


HW_DEBUG = 1
BATCH_SZ = 1

if HW_DEBUG:
    from IPython.display import display
    from pandas_summary import DataFrameSummary
    pd.set_option('display.max_columns', 70)



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

        # Note: update this list for any new continent addition.
        self.ALL_CONTINENTS = ['Europe', 'Asia']

        # EUROPE Dataframes
        self.df_dest_europe = pd.read_csv('data/europe/Destination_2_0.csv', low_memory=False, encoding='utf-8')
        self.df_tsights_europe = pd.read_csv('data/europe/TopSights_2_0.csv', low_memory=False, encoding='utf-8')

        # ASIA Dataframes
        self.df_dest_asia = pd.read_csv('data/asia/Destination_2_0.csv', low_memory=False, encoding='utf-8')
        self.df_tsights_asia = pd.read_csv('data/asia/TopSights_2_0.csv', low_memory=False, encoding='utf-8')

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
        #df_dest['Country'] = df_dest.Country.apply(lambda x: x.replace(' ',''))
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


        #
        # 2. Top Sights Data
        #

        # FIXME: Remove unwated space in the country columns.
        df_tsights['Country'] = df_tsights['Country'].astype(str)
        #df_tsights['Country'] = df_tsights.Country.apply(lambda x: x.replace(' ',''))
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
        df_tsights['NumberOfReview'] = df_tsights.NumberOfReview.apply(lambda x: x.replace('avis',''))
        df_tsights['NumberOfReview'] = df_tsights['NumberOfReview'].astype(float)

        # Drop 'zero' value columns
        df_tsights = self.hwb_drop_zero_value_column(df_tsights)

        # Convert 'NaN' to empty string
        df_tsights['Description'] = df_tsights.Description.fillna('')
        df_tsights['Type'] = df_tsights.Type.fillna('')
        df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.fillna('')

        # FIXME: what should be the typical default time to set? for now its 30 mins.
        #df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.fillna(df_tsights.TypicalTimeSpent.mean())
        #df_tsights['TypicalTimeSpent'] = df_tsights.TypicalTimeSpent.fillna(30)


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
        logger.debug('Rx: Country {0}'.format(country))
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
        df_country = df_country.drop(['Destination', 'Rank'], axis=1)
        return list(df_country.columns.values)


    def hwb_all_experiences_for_by_destination(self, continent, destination):
        """
        Return all the categories for a destination and the country it belongs to. 
        """
        dst_exp_list = []

        df_var = eval('self.df_dest_' + continent.lower())
        if not df_var.empty:
            df_dst = df_var[(df_var['Destination'] == destination) | 
                            (df_var['Destination'].str.contains(destination + ':'))]
            country = df_dst.Country.unique().tolist()[0]

            df_dst = df_dst.drop(['Rank', 'Destination', 'Country'], axis=1)
            df_dst = self.hwb_drop_constant_value_column(df_dst)
            dst_exp_list = list(df_dst.columns.values)
            return dst_exp_list, country



    def hwb_all_experiences_for_a_destination(self, continent, destination):
        """
        Return all the categories for a destination and the country it belongs to. 
        """
        dst_exp_list = []

        df_var = eval('self.df_dest_' + continent.lower())
        if not df_var.empty:
            df_dst = df_var[df_var['Destination'] == destination]
            country = df_dst.Country.unique().tolist()[0]
            df_dst = df_dst.drop(['Rank'], axis=1)
            df_dst = self.hwb_drop_constant_value_column(df_dst)
            dst_exp_list = list(df_dst.columns.values)
            return dst_exp_list, country


    def hwb_all_destinations_per_continent(self, continent):
        """
        Return all the destinations per continent.
        """
        all_dest = []
        all_cleaned_dest = []

        df_var = eval('self.df_dest_' + continent.lower())
        all_dest = df_var.Destination.unique().tolist()

        for d in all_dest:
            if ':' in d:
                all_cleaned_dest.append(d.split(':')[0])
            else:
                all_cleaned_dest.append(d)

        all_cleaned_dest = list(set(all_cleaned_dest))

        return all_cleaned_dest 


    def hwb_fuzz_extract(self, continent, match_string, match_with):
        """
        Using fuzzywuzzy find the matched destionations.
        """
        suggest_destinations = []
        found_dest = ''
        df_status = False

        matched_destinations = process.extract(match_string, match_with)
        df_var = eval('self.df_dest_' + continent.lower())

        if matched_destinations[0][1] == 100:
            found_dest = matched_destinations[0][0]
            if not df_var[(df_var['Destination'] == found_dest) | (df_var['Destination'].str.contains(found_dest + ':'))].empty:
                df_status = True
            return found_dest, df_status, suggest_destinations

        logger.debug('Suggested destination {0}'.format(matched_destinations))

        for i in range(len(matched_destinations)):
            if not df_var[(df_var['Destination'] == matched_destinations[i][0]) | (df_var['Destination'].str.contains(matched_destinations[i][0] + ':'))].empty:
                suggest_destinations.append(matched_destinations[i][0])

        logger.debug('Matched place {0}'.format(suggest_destinations))
        
        return found_dest, df_status, suggest_destinations


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
        try:
            return self.df_country_info.loc[self.df_country_info['Country'] == country, field].iloc[0]
        except:
            return ''


    def hwb_lonely_planet_urls(self, country, destination):
        """
        Return Lonely Planet URL for a input country and destination.
        """
        try:
            return self.df_lp_url.loc[(self.df_lp_url['Country'] == country) & (self.df_lp_url['Destination'] == destination), 'lp_URL'].iloc[0]
        except:
            return ''


    def hwb_continent_experience_combinations(self, continent, experience, exp_len):
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


    def hwb_country_experience_combinations(self, continent, country, experience, exp_len):
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
        df_cnt = df_var[df_var['Country'] == country]
        for i in range(len(top)):
            if len(top[i]) and (len(top3) < 3):
                c_list = list(set(self.hwb_all_experiences_for_a_country(country)) - set(list(top[i])))
                df_tmp = df_cnt[(df_cnt[c_list] == False).all(axis=1) & (df_cnt[list(top[i])] == True).all(axis=1)]
                if not df_tmp.empty:
                    top3.append(top[i])

        return top3


    def hwd_map_dest_to_tsights_experineces(self, cat, subcat):
        """
        Mapping main experiences with the options(expereinces) on TopSights.
        """
        if cat == 'adventures':
          if set(subcat) & set(['Skiing']):
            return ['Skiing']
        elif cat == 'outdoors':
          return ['Outdoors']
        elif cat == 'social':
          if (set(subcat) & set(['Shopping'])) and (set(subcat) & set(['Casinos'])):
            return ['Markets', 'Casinos']
          elif set(subcat) & set(['Shopping']):
            return ['Markets']
          elif set(subcat) & set(['Casinos']):
            return ['Casinos']
        elif cat == 'beautiful_nature':
          if set(subcat) & set(['Beaches']):
            return ['Beaches']
        elif cat == 'arts_culture':
          if (set(subcat) & set(['Museums'])) and (set(subcat) & set(['Architecture'])) and (set(subcat) & set(['Art'])) and (set(subcat) & set(['Casinos'])):
            return ['Museums', 'Architecture','Art','Casinos']
          elif set(subcat) & set(['Museums']):
            return ['Museums']
          elif set(subcat) & set(['Architecture']):
            return ['History']
          elif set(subcat) & set(['Art']):
            return ['Art & Culture']
          elif set(subcat) & set(['Casinos']):
            return ['Casinos']

        return []


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
        df_dest_var = eval('self.df_dest_' + continent.lower())
        df_tsights_var = eval('self.df_tsights_' + continent.lower())

        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences(continent)) - set(subcat))
                df_local = df_dest_var[(df_dest_var[c_list] == False).all(axis=1) & (df_dest_var[subcat] == True).all(axis=1)]

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_continent_experience_combinations(continent, subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top expereinces suggestions to user {0}'.format(top_sugg[0]))
                    err = 204

                else:
                    # Find top rank '1' countries, they are not ordered yet.
                    df_local = df_local[df_local['Rank'] == 1]
                    df_local = df_local.sort_values(['Rank'], ascending=True)
                    top_countries = df_local.Country.unique().tolist()
                    top_destionations = df_local.Destination.unique().tolist()

                    # Find top places
                    df_local = df_tsights_var[df_tsights_var['Destination'].isin(top_destionations)]
                    if df_local.empty:
                        logger.debug('TopSights are missing for this destination, which is unusual')
                        continue

                    ts_list = self.hwd_map_dest_to_tsights_experineces(cat, subcat)
                    if ts_list:
                        df_local = df_local[(df_local[ts_list] == True).any(axis=1)]

                    df_local = df_local.sort_values(['Rating'], ascending=False)
                    df_local = df_local.sort_values(['NumberOfReview'], ascending=False)
                    df_local = df_local[:BATCH_SZ*20]

                    for i in range(len(df_local.Country.unique().tolist())):
                        if i > 3:
                            break
                        payload = {}
                        # Populate the data
                        payload['Country'] = df_local.Country.unique()[i]
                        df_tmp = df_local[df_local['Country'] == payload['Country']]
                        payload['Destinations'] = df_tmp.Destination.unique().tolist()
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
        df_dest_var = eval('self.df_dest_' + continent.lower())
        df_tsights_var = eval('self.df_tsights_' + continent.lower())

        df_local_country = df_dest_var[df_dest_var['Country'] == country]

        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences_for_a_country(country)) - set(subcat))
                df_local = df_local_country[(df_local_country[c_list] == False).all(axis=1) & (df_local_country[subcat] == True).all(axis=1)]
                df_local = self.hwb_drop_constant_value_column(df_local)

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_country_experience_combinations(continent, country, subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top expereinces suggestions to user {0}'.format(list(top_sugg[0])))
                    err = 204

                else:
                    payload = {}
                    
                    # Destionation for a country might not be rank '1', hence sort the stop most. 
                    df_local = df_local[df_local['Rank'] == 1]
                    df_local = df_local.sort_values(['Rank'], ascending=True)
                    top_destionations = df_local.Destination.unique().tolist()
                    logger.debug('This is the correct top destinations {0}'.format(df_local.Destination.unique().tolist()))
                    
                    # Find top places
                    df_ts = df_tsights_var[df_tsights_var['Country'] == country]
                    df_ts = df_ts[df_ts['Destination'].isin(top_destionations)]
                    if df_ts.empty:
                        logger.debug('TopSights are missing for this destination, which is unusual')
                        continue

                    ts_list = self.hwd_map_dest_to_tsights_experineces(cat, subcat)
                    if ts_list:
                        df_tss = df_ts[(df_ts[ts_list] == True).any(axis=1)]
                        if not df_tss.empty:
                            print('NOT GOOD : Nothing to show in TopSights')
                            df_ts = df_tss

                    df_ts = df_ts.sort_values(['Rating'], ascending=False)
                    df_ts = df_ts.sort_values(['NumberOfReview'], ascending=False)
                    
                    dest_list = df_ts.Destination.unique().tolist()
                    logger.debug('Top Destinations : {0}'.format(dest_list))

                    payload['Experiences'] = subcat
                    for dst in dest_list: 
                        df = df_ts[df_ts['Destination'] == dst]
                        df = df[:3]
                        payload['Destinations'] = df[:(BATCH_SZ * 3)]



                    logger.debug('Destination list : {0}'.format(dest_list))
                    payload['Destinations'] = dest_list[:(BATCH_SZ * 3)]
                    ret_data.append(payload)


        return ret_suggestions, ret_data, err


    def hwb_a_destination_itinerary_data(self, payload):
        """
        Populate the itinerary data based on the payload request and return it to 
        itinerary documents for rendering.
        """
        ret_data = []
        ret_suggestions = []
        err = 200

        country = payload['Country']
        destination = payload['Destination']
        experiences = payload['Experiences']
        continent = self.hwb_get_continent_for_countries(country)

        num_days = int(payload['NumDays'])
        num_adults = payload['NumAdults']
        num_kids = payload['NumKids']

        num_days = 15 if num_days > 15 else num_days

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        logger.debug('Continent {0} Country {1} experience {2}'.format(continent, country, experiences))
        df_dest_var = eval('self.df_dest_' + continent.lower())
        df_tsights_var = eval('self.df_tsights_' + continent.lower())

        df_a_destination = df_dest_var[(df_dest_var['Country'] == country) & ((df_dest_var['Destination'] == destination) |
                                                                              (df_dest_var['Destination'].str.contains(destination + ':')))]

        num_exp = len(subexp_list)
        days_per_exp = int(num_days/num_exp) + 1
        logger.debug('Days per destination : {0}'.format(days_per_exp))

        for cat,subcat in subexp_list.items():
            if len(subcat):
                dest_exp_list, _ = self.hwb_all_experiences_for_by_destination(continent, destination)
                c_list = list(set(dest_exp_list) - set(subcat))
                df_local = df_a_destination[(df_a_destination[c_list] == False).all(axis=1) & 
                                            (df_a_destination[subcat] == True).all(axis=1)]
                if df_local.empty:
                    df_local = df_a_destination[(df_a_destination[c_list] == False).all(axis=1) & 
                                                (df_a_destination[subcat] == True).any(axis=1)]


                if df_local.empty:
                    logger.error("We shouldn't be here")
                    err = 204

                else:
                    # Destionation for a country might not be rank '1', hence sort the stop most. 
                    df_tmp = df_local.sort_values(['Rank'], ascending=True)
                    top_destionations = df_tmp.Destination.unique().tolist()
                    logger.debug('Top Destinations from df_local: {0}'.format(top_destionations))
                    
                    # Find top places
                    df_ts = df_tsights_var[df_tsights_var['Country'] == country]
                    df_ts = df_ts[df_ts['Destination'].isin(top_destionations)]
                    if df_ts.empty:
                        logger.debug('TopSights are missing for this destination, which is unusual')
                        continue

                    ts_list = self.hwd_map_dest_to_tsights_experineces(cat, subcat)
                    if ts_list:
                        df_tss = df_ts[(df_ts[ts_list] == True).any(axis=1)]
                        if not df_tss.empty:
                            print('NOT GOOD : Nothing to show in TopSights')
                            df_ts = df_tss


                    df_ts = df_ts.sort_values(['Rating'], ascending=False)
                    df_ts = df_ts.sort_values(['NumberOfReview'], ascending=False)

                    dest_list = df_ts.Destination.unique().tolist()[:2]
                    logger.debug('Top Destinations : {0}'.format(dest_list))

                    # Populate the data.
                    for dst in dest_list:
                        df_dst = df_ts[df_ts['Destination'] == dst]
                        df_dst = df_dst[:3]
                        
                        for index, row in df_dst.iterrows():
                            ts_data = {}
                            ts_data['Experiences'] = subcat
                            ts_data['Destination'] = dst
                            ts_data['TopSights'] = row['TopSight']
                            ts_data['Description'] = row['Description']
                            ts_data['Type'] = row['Type']
                            ts_data['TypicalTimeSpent'] = row['TypicalTimeSpent']
                            ts_data['Kid-friendly'] = 'Yes' if row['Kid-friendly'] else ''
                            ts_data['Amusement-Parks'] = 'Yes' if row['Amusement Parks'] else ''
                            
                            if row['Latitude'] and row['Longitude']:
                                ts_data['Latitude'] = row['Latitude']
                                ts_data['Longitude'] = row['Longitude']

                            ret_data.append(ts_data)

        return ret_suggestions, ret_data, err



    def hwb_destinations_itinerary_data(self, payload):
        """
        Populate the itinerary data based on the payload request and return it to 
        itinerary documents for rendering.
        """
        ret_data = []
        ret_suggestions = []
        err = 200

        country = payload['Country']
        experiences = payload['Experiences']
        continent = self.hwb_get_continent_for_countries(country)

        num_days = int(payload['NumDays'])
        num_adults = payload['NumAdults']
        num_kids = payload['NumKids']

        num_days = 15 if num_days > 15 else num_days

        subexp_list = self.hwb_fetch_subexp_to_exp(experiences)

        # Destination.csv has all the possible combination of the filters. Hence always match 'all'.
        # When 'all' is not matched in that case 'any' will be the suggestions to user.
        logger.debug('Continent {0} Country {1} experience {2} num_days {3}'.format(continent, country, experiences, num_days))
        df_dest_var = eval('self.df_dest_' + continent.lower())
        df_tsights_var = eval('self.df_tsights_' + continent.lower())

        df_local_country = df_dest_var[df_dest_var['Country'] == country]

        num_exp = len(subexp_list)
        days_per_exp = int(num_days/num_exp) + 1
        logger.debug('Days per destination : {0}'.format(days_per_exp))

        for cat,subcat in subexp_list.items():
            if len(subcat):
                c_list = list(set(self.hwb_all_experiences_for_a_country(country)) - set(subcat))
                df_local = df_local_country[(df_local_country[c_list] == False).all(axis=1) & (df_local_country[subcat] == True).all(axis=1)]
                df_local = self.hwb_drop_constant_value_column(df_local)

                if df_local.empty:
                    sugg = {}
                    top_sugg = self.hwb_country_experience_combinations(continent, country, subcat, len(subcat))
                    sugg['Suggestion'] = top_sugg
                    ret_suggestions.append(sugg)
                    logger.info('Top expereinces suggestions to user {0}'.format(list(top_sugg[0])))
                    err = 204

                else:
                    # Destionation for a country might not be rank '1', hence sort the stop most. 
                    df_local = df_local[df_local['Rank'] == 1]
                    df_local = df_local.sort_values(['Rank'], ascending=True)
                    top_destionations = df_local.Destination.unique().tolist()
                    logger.debug('Top Destinations from df_local: {0}'.format(top_destionations))
                    
                    # Find top places
                    df_ts = df_tsights_var[df_tsights_var['Country'] == country]
                    df_ts = df_ts[df_ts['Destination'].isin(top_destionations)]
                    if df_ts.empty:
                        logger.debug('TopSights are missing for this destination, which is unusual')
                        continue

                    ts_list = self.hwd_map_dest_to_tsights_experineces(cat, subcat)
                    if ts_list:
                        df_tss = df_ts[(df_ts[ts_list] == True).any(axis=1)]
                        if not df_tss.empty:
                            print('NOT GOOD : Nothing to show in TopSights')
                            df_ts = df_tss


                    df_ts = df_ts.sort_values(['Rating'], ascending=False)
                    df_ts = df_ts.sort_values(['NumberOfReview'], ascending=False)

                    dest_list = df_ts.Destination.unique().tolist()[:2]
                    logger.debug('Top Destinations : {0}'.format(dest_list))

                    # Populate the data.
                    for dst in dest_list:
                        df_dst = df_ts[df_ts['Destination'] == dst]
                        df_dst = df_dst[:3]
                        
                        for index, row in df_dst.iterrows():
                            ts_data = {}
                            ts_data['Experiences'] = subcat
                            ts_data['Destination'] = dst
                            ts_data['TopSights'] = row['TopSight']
                            ts_data['Description'] = row['Description']
                            ts_data['Type'] = row['Type']
                            ts_data['TypicalTimeSpent'] = row['TypicalTimeSpent']
                            ts_data['Kid-friendly'] = 'Yes' if row['Kid-friendly'] else ''
                            ts_data['Amusement-Parks'] = 'Yes' if row['Amusement Parks'] else ''
                            
                            if row['Latitude'] and row['Longitude']:
                                ts_data['Latitude'] = row['Latitude']
                                ts_data['Longitude'] = row['Longitude']

                            ret_data.append(ts_data)

        return ret_suggestions, ret_data, err


