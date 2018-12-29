#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import datetime

class MyDb:
    def __init__(self, table):
        self.db = MySQLdb.connect("10.56.78.54","tvd","tvd1234","postreview",charset="utf8")
        self.cursor = self.db.cursor()
        self.table = table
        
    def my_create_table(self, table):
        sql = "CREATE TABLE IF NOT EXISTS %s (                 \
                `id` INT UNSIGNED AUTO_INCREMENT,              \
                `name` VARCHAR(100) NOT NULL,                  \
                `sex` VARCHAR(10) NOT NULL,                    \
                `age` INT UNSIGNED NOT NULL,                   \
                PRIMARY KEY (`id`)                             \
               )ENGINE=InnoDB DEFAULT CHARSET=utf8" % table
        self.cursor.execute(sql)
        self.db.commit()
        self.table = table
        
    def my_drop_table(self, table):
        sql = "DROP TABLE %s" % table
        self.cursor.execute(sql)
        self.db.commit()

    def my_query_key_one(self, field, key, value):
        sql = "SELECT %s from %s where `%s` = '%s'" % (field, self.table, key, value)
        res = self.cursor.execute(sql)
        return res, self.cursor.fetchone()
        #return res, list(self.cursor.fetchone())

    def my_query_key_all(self, field, key, value):
        sql = "SELECT %s from %s where `%s` = '%s'" % (field, self.table, key, value)
        res = self.cursor.execute(sql)
        return res, self.cursor.fetchall()

    def my_query_all(self, field):
        sql = "SELECT %s from %s" % (field, self.table)
        res = self.cursor.execute(sql)
        return res, list(self.cursor.fetchall())

    def my_insert(self, keys, values):
        keys_string = ""
        value_string = ""
        for key in keys:
            keys_string += key + ","
        for value in values:
            if isinstance(value, str):
                value_string += "'" + value + "'" + ","
            else:
                value_string += str(value) + ","
            
        keys_string = str(keys_string).strip(",")
        value_string = str(value_string).strip(",")
        sql = "INSERT INTO " + self.table + " (" + keys_string + ") VALUES (" + value_string + ")"
        print sql
        self.cursor.execute(sql)
        self.db.commit()
        
    def my_insert_employee(self, name, sex, age):
        keys = ("name", "sex", "age")
        values = (name, sex, age)
        self.my_insert(keys, values)
        
    def my_delete(self, field, content):
        sql = "DELETE FROM " + self.table + " where " + field + " = '%s'" % (content)
        self.cursor.execute(sql)
        self.db.commit()
        
    def __del__(self):
        self.db.close()
        self.cursor.close()
        
def delete_comments_when_no_note():
    comments = MyDb("comments")
    notes = MyDb("notes")
    count, tuple_refs = comments.my_query_all("ref")
    notmatch_count = 0
    for tuple_ref in tuple_refs:
        ref = tuple_ref[0]
        count, record = notes.my_query_key_all("*", "ref", ref)
        if not count:
            notmatch_count += 1
            comments.my_delete("ref", ref)
            print "In comments, Delete: %s" % ref
    print "Total %d not matched." % notmatch_count

def delete_notes_by_date(author, date):
    notes = MyDb("notes")
    count, rows = notes.my_query_all("*")
    for row in rows:
        record_author = row[0]
        record_time = row[2].strftime("%Y-%m-%d")
        if date == record_time and author == record_author:
            notes.my_delete("ref", row[4])
            print "Delete: %s" % row[4]
    
def insert_note_before_date(author, dateline):
    comments = MyDb("comments")
    notes = MyDb("notes")
    notes.my_delete("author", "Tommy")
    curr_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment_count, comment_rows = comments.my_query_all("*")
    for comment_row in comment_rows:
        ref = comment_row[0]
        count, tuple_dates = notes.my_query_key_one("date", "ref", ref)
        record_date = tuple_dates[0].strftime("%Y-%m-%d")
        if record_date > dateline:
            continue  
        hashid = comment_row[5]
        if 1 == count:
            keys = ("author", "id", "date", "note", "ref")
            note = "Done:" + hashid
            values = (author, "-", curr_date, str(note), str(ref))
            notes.my_insert(keys, values)

def delete_comments(ref):
    comments = MyDb("comments")
    count, tuple_refs = comments.my_query_key_one("ref", "ref", ref)
    if not count:
        print "In comments, record: %s not exits." % ref
        return
    comments.my_delete("ref", ref)
    print "Delete comments: %s" % ref
    
def delete_notes(ref):
    notes = MyDb("notes")
    count, tuple_refs = notes.my_query_key_all("*", "ref", ref)
    if not count:
        print "In notes, record : %s not exits." % ref
        return
    notes.my_delete("ref", ref)
    print "Delete notes: %s" % ref
    
def delete_comments_notes_togethor(ref):
    delete_comments(ref)
    delete_notes(ref)
    
if __name__ == "__main__":
    #db = MyDb("notes")
    #print db.my_query_key_all("author", "ref", "7b1cf0833cfe764829bec93b753acfe7b5a0e55b#24f76e8c3d92194b9034b362c359daf3c5067ad9_118_154")
    #delete_notes_by_date("sweng", "2017-02-17")
    #delete_comments_when_no_note();
    #insert_note_before_date("Tommy", "2017-09-01")
    delete_comments_notes_togethor("e378e3f9694dbd06b09425723b4dcac36c3e6253#fe4079098676d15b83668f2b56da42f00c43baaa_80_107")
