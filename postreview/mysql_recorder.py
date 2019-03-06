#!/usr/bin/python

import MySQLdb

class Recorder:

	def __init__(self, table):
		self.db = MySQLdb.connect("10.56.78.54","tvd","tvd1234","postreview",charset="utf8")
		self.cursor = self.db.cursor()
		self.table = table
	def write(self, contents):
		query = ("SELECT project,branch,commit,date,rollbacked FROM %s WHERE commit='%s'" % (self.table, contents[3]))
		count = self.cursor.execute(query)
		if count == 0:
			sql = "INSERT INTO " + self.table + " (project, branch, svn, commit, author, date, title, fullname, team, rollbacked) \
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			self.cursor.execute(sql, (contents[0], contents[1], contents[2], contents[3], contents[4], \
				contents[5], contents[6], contents[7], contents[8], contents[9]))
			self.db.commit()
		else:
			for (project,branch,commit,date, rollbacked) in self.cursor:
				if rollbacked == None and contents[9] != None:
					sql = "UPDATE " + self.table + " SET rollbacked=%s WHERE commit=%s"
					self.cursor.execute(sql, (contents[9], contents[3]))
					self.db.commit()
					print "%s has been updated as rollbacked by %s" % (contents[3], contents[9])
				else:
					print "%s has existd at %s, %s, %s" % (commit, project, branch, date)

	def update(self, contents, primary_key):
		keys_list = ""
		values_list = ""
		keys_tuple = ()
		values_tuple = ()
		update_list = ""
		for (k, v) in contents.items():
			if len(keys_list) == 0:
				keys_list += k
				values_list += "%s"
				update_list += k + "=%s"
			else:
				keys_list += "," + k
				values_list += ", %s"
				update_list += "," + k + "=%s"
			keys_tuple += (k,)
			values_tuple += (contents[k],)

		query = ("SELECT %s FROM %s WHERE %s='%s'" % (keys_list, self.table, primary_key, contents[primary_key]))
		count = self.cursor.execute(query)
		if count == 0:
			sql = "INSERT INTO " + self.table + " (" + keys_list + ") VALUES (" + values_list + ")"
			self.cursor.execute(sql, values_tuple)
			self.db.commit()
		else:
			for current_values in self.cursor:
				if current_values != values_tuple:
					sql = "UPDATE " + self.table + " SET " + update_list + " WHERE " + primary_key + "=%s"
					self.cursor.execute(sql, values_tuple + (contents[primary_key], ))
					self.db.commit()
					print "%s has been updated." % (contents[primary_key])
				else:
					print "%s has existd." % (contents[primary_key])

	def query(self, conditions):
		query = "SELECT * FROM %s WHERE %s" % (self.table, conditions)
		self.cursor.execute(query)
		return list(self.cursor.fetchall())

	def test(self, a, b):
		sql = "UPDATE " + self.table + " SET rollbacked=%s WHERE commit=%s"
		self.cursor.execute(sql, (a, b))
		self.db.commit()
		
	def __del__(self):
		self.db.close()

if __name__ == "__main__":
	rec = Recorder("comments")
	#rec.test('d91fedbb513ed980a596798f8c8bb0f598cc9a1c', '65d13906322536a78a212498b74315bcb3293a5e')

