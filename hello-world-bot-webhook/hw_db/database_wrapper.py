# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright (C) HelloWorld - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Milind Deore <tomdeore@gmail.com>, May 2019

import psycopg2
import logging

logger = logging.getLogger()


class HWDB:
    """
    Hello World Database : All access API are defined in this class.
    """

    def __init__(self):
        self.hwdb_conn = None
        self.hwdb_cur = None
        self.hwdb_conn_open()
        logger.info('Database version {0}'.format(self.hwdb_version()[0]))


    def __del__(self):
        """
        Clean up and Release all the resources.
        """
        self.hwdb_conn_close()


    def hwdb_conn_open(self):
        """
        User session, is where all the running session data is kept.
        This DB also maintains user bucket list data.
        Open database connection to backend postgresql 11.
        """
        try:
            self.hwdb_conn = psycopg2.connect(user = "doadmin", password = "r25obaddb39km116",
                    host = "db-postgresql-columbus-telebot-do-user-6132892-0.db.ondigitalocean.com",
                    port = 25060 , database = "Columbus")
            logger.info('DB connection successful!')
            self.hwdb_cur = self.hwdb_conn.cursor()
        except psycopg2.Error as e:
            logger.error('DB connection failed with error {0}'.format(e.pgerror))


    def hwdb_version(self):
        """
        Version of DB used in Hello World.
        """
        try:
            version = []
            self.hwdb_cur.execute("SELECT version();")
            version = self.hwdb_cur.fetchall()

            return version

        except psycopg2.Error as e:
            logger.error('Fetch DB version failed with error {0}'.format(e.pgerror))


    def hwdb_conn_close(self):
        """
        Close database connection.
        """
        try:
            self.hwdb_cur.close()
            self.hwdb_conn.close()
            logger.info('DB connection closed successfully!')
        except psycopg2.Error as e:
            logger.error('DB connection failed with error {0}'.format(e.pgerror))


    def hwdb_conn_restart(self):
        """
        Restart database connection.
        """
        try:
            self.hwdb_cur.close()
            self.hwdb_conn.close()
            self.hwdb_conn()
            logger.info('DB connection restarted successfully!')
        except psycopg2.Error as e:
            logger.error('DB connection restart failed with error {0}'.format(e.pgerror))


    def hwdb_user_connection_conn_commit(self):
        """
        Commit to database
        """
        try:
            self.hwdb_conn.commit()
            logger.info('DB commit successfully!')
        except psycopg2.Error as e:
            logger.error('DB commit failed with error {0}'.format(e.pgerror))


    def hwdb_user_session_upsert(self, uid, country, destination, cat, op):
        """
        User session Inser/update/Delete can be done using this API.
        Input: user_id, country. destination, category, operation.
        """
        try:
            if not self.hwdb_conn.closed:
                uid = int(uid if uid else 0)
                country = country if country else 'NULL'
                destination = destination if destination else 'NULL'
                cat = cat if cat else 'NULL'

                self.hwdb_cur.execute("CALL UpsertSession(%s, %s, %s, %s, %s)", (uid, country, destination, cat, op))
                self.hwdb_conn.commit()
                logger.info('Successfully performed operation {0} in user session id {1}'.format(op, uid))
            else:
                self.hwdb_conn_open()
        except psycopg2.Error as e:
            logger.error('DB commit failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()


    def hwdb_user_session_select(self, uid):
        """
        Select the session for a user_id
        """
        result = []
        rec = {}
        rec['category'] = []
        rec['country'] = 'NULL'
        select_str = ''
        try:
            if not self.hwdb_conn.closed:
                select_str = 'Select * from SelectSession(%s)' % uid
                logger.debug(select_str)
                self.hwdb_cur.execute(select_str)
                result = self.hwdb_cur.fetchall()
                for idx in range(len(result)):
                    if result[idx][0] == 'category':
                        if result[idx][1] != 'NULL':
                            rec[result[idx][0]].append(result[idx][1])
                    else:
                        rec[result[idx][0]] = result[idx][1]
            else:
                self.hwdb_conn_open()
            return rec

        except psycopg2.Error as e:
            logger.error('DB select session failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()



    def hwdb_user_session_delete(self, uid):
        """
        Delete user session completely.
        """
        select_str = ''
        try:
            if not self.hwdb_conn.closed:
                select_str = 'Call DeleteSession(%s)' % uid
                logger.debug(select_str)
                self.hwdb_cur.execute(select_str)
                self.hwdb_conn.commit()
            else:
                self.hwdb_conn_open()

        except psycopg2.Error as e:
            logger.error('DB select session failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()


    ##
    # User Bucket list
    ##
    def hwdb_columbus_user_bucketlist_upsert(self, uid, f_name, l_name, email, country, username):
        """
        Columbus user Insert / Update.
        Input: user_id, first_name, last_name, email, country, username.
        """
        try:
            if not self.hwdb_conn.closed:
                uid = int(uid if uid else 0)
                f_name = f_name if f_name else 'NULL'
                l_name = l_name if l_name else 'NULL'
                email = email if email else 'NULL'
                country = country if country else 'NULL'
                username = username if username else 'NULL'

                self.hwdb_cur.execute("CALL UpsertColumbusUser(%s, %s, %s, %s, %s, %s)", (uid, f_name, l_name, email, country, username))
                self.hwdb_conn.commit()
                logger.info('Successfully bucketlist upsert for user id {0}'.format(uid))
            else:
                self.hwdb_conn_open()
        except psycopg2.Error as e:
            logger.error('DB commit bucketlist upsert failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()


    def hwdb_bucketlist_insert(self, uid, country, destination, cat, ttd):
        """
        Insert bucket list item.
        Input: user_id, country, destination, cat, ttd.
        """
        try:
            if not self.hwdb_conn.closed:
                exec_str = ''
                uid = int(uid if uid else 0)
                country = country if country else 'NULL'
                destination = destination if destination else 'NULL'
                cat = cat if cat else 'NULL'
                ttd = ttd if ttd else 'NULL'

                logger.debug('uid {0} country {1} destination {2} cat {3} ttd {4}'.format(uid, country, destination, cat, ttd))

                self.hwdb_cur.execute("CALL InsertBucketList(%s, %s, %s, %s, %s)", (uid, country, destination, cat, ttd))
                self.hwdb_conn.commit()
                logger.info('Successfully insert user bucket list for user id {0}'.format(uid))
            else:
                self.hwdb_conn_open()
        except psycopg2.Error as e:
            logger.error('DB commit bucketlist insert failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()


    def hwdb_bucketlist_select(self, uid):
        """
        Select the bucketlist for a user_id
        """
        result = []
        data = []
        select_str = ''
        try:
            if not self.hwdb_conn.closed:
                select_str = 'Select * from SelectBucketList(%s)' % int(uid)
                logger.debug(select_str)
                self.hwdb_cur.execute(select_str)
                result = self.hwdb_cur.fetchall()
                for idx in range(len(result)):
                    rec = {}
                    rec['name'] = result[idx][0]
                    rec['country'] = result[idx][1]
                    rec['destination'] = result[idx][2]
                    rec['category'] = result[idx][3]
                    rec['ttd'] = result[idx][4]
                    rec['email'] = result[idx][5]
                    rec['native_country'] = result[idx][6]
                    data.append(rec)
            else:
                self.hwdb_conn_open()
            return data

        except psycopg2.Error as e:
            logger.error('DB select bucketlist failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()


    def hwdb_columbus_user_bucketlist_delete(self, uid, country, destination):
        """
        Columbus user bucketlist item (SOFT) delete.
        Input: user_id, country, destination.
        """
        try:
            if not self.hwdb_conn.closed:
                uid = int(uid if uid else 0)
                country = country if country else 'NULL'
                destination = destination if destination else 'NULL'

                self.hwdb_cur.execute("CALL DeleteBucketList(%s, %s, %s)", (uid, country, destination))
                self.hwdb_conn.commit()
                logger.info('Successfully deleted item from bucketlist for user id {0}'.format(uid))
            else:
                self.hwdb_conn_open()
        except psycopg2.Error as e:
            logger.error('DB commit failed with error {0}'.format(e.pgerror))
            self.hwdb_conn_restart()



