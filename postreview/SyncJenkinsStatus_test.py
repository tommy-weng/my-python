from SyncJenkinsStatus import HtmlParser
from SyncJenkinsStatus import MyDB
from SyncJenkinsStatus import Jenkins
import datetime
import pytest

class TestHtmlParser:
	def test__parse_patchset_line(self):
		html = '<th id="event456850691" colspan="7" scope="colgroup" align="left">patchset-created 16282/2 @ 2017-03-09 15:09:06+0800</th>'
		parser = HtmlParser()
		patchset_info = {}
		assert parser._parse_patchset_line(html, patchset_info) == True
		assert patchset_info == {'created': datetime.datetime(2017, 3, 9, 15, 9, 6), 'number': '16282', 'patchset': '2'}
	def test__parse_one_row(self):
		html = '<td headers="hJob event1793666061"><a href="/jenkins/job/gerrit-fdd-ut-sm4_arm/">gerrit-fdd-ut-sm4_arm</a></td><td headers="hRun event1793666061"><a href="/jenkins/job/gerrit-fdd-ut-sm4_arm/1110/">#1110</a></td><td headers="hCompleted event1793666061"><strong>Y</strong></td><td headers="hResult event1793666061"><strong>SUCCESS</strong></td><td headers="hTriggeredTs event1793666061">3/9/17 3:08:45 PM</td><td headers="hStartedTs event1793666061">3/9/17 3:08:53 PM</td><td headers="hCompletedTs event1793666061">3/9/17 3:16:17 PM</td>'
		parser = HtmlParser()
		job = parser._parse_one_row(html)
		assert job == {'build': '#1110',
              'build_url': '/jenkins/job/gerrit-fdd-ut-sm4_arm/1110/',
              'completed': datetime.datetime(2017, 3, 9, 15, 16, 17),
              'iscompleted': 'Y',
              'job': 'gerrit-fdd-ut-sm4_arm',
              'job_url': '/jenkins/job/gerrit-fdd-ut-sm4_arm/',
              'result': 'SUCCESS',
              'started': datetime.datetime(2017, 3, 9, 15, 8, 53),
              'triggered': datetime.datetime(2017, 3, 9, 15, 8, 45)}
	def test_parser(self):
		f = open("output2.txt")
		html = f.read()
		parser = HtmlParser()
		allJobs = parser.do(html)
		#print allJobs
		assert len(allJobs) == 18

class TestMyDb:
	def test_format_insert_sentence_with_one_param(self):
		db = MyDB("gerritci", "jobs")
		sql, values = db._format_insert_sentence({'svn':'1234'})
		assert sql == 'INSERT INTO jobs (svn) VALUES (%s)'
		assert values == ('1234',)

	def test_format_insert_sentence_with_two_param(self):
		db = MyDB("gerritci", "jobs")
		sql, values = db._format_insert_sentence({'svn':'1234', 'build':'ut'})
		assert sql == 'INSERT INTO jobs (svn,build) VALUES (%s,%s)'
		assert values == ('1234', 'ut',)

	def test_insert(self, mocker):
		db = MyDB("gerritci", "jobs")
		m = mocker.patch.object(MyDB, '_excute_sql_sentence')
		db._insert({'svn':'1234', 'build':'ut'})
		m.assert_called_once_with('INSERT INTO jobs (svn,build) VALUES (%s,%s)', ('1234', 'ut'))

	def test_format_select_sentence_with_two_param(self):
		db = MyDB("gerritci", "jobs")
		sql, values = db._format_select_sentence({'svn':'1234', 'build':'ut'})
		assert sql == 'SELECT * FROM jobs WHERE svn=%s AND build=%s'
		assert values == ('1234', 'ut',)

	def test_is_existed(self, mocker):
		db = MyDB("gerritci", "jobs")
		db._excute_sql_sentence('INSERT INTO jobs (number, patchset) VALUES (%s, %s)', ('1234', '2'))
		assert db._is_existed({'number':'1234', 'patchset':'2'}) == True
		db._remove_record({'number':'1234', 'patchset':'2'})

	def test__split_contents_by_keys(self):
		db = MyDB("gerritci", "jobs")
		origin_contents = {'number':'1234', 'patchset':'2'}
		contents, conditions = db._split_contents_by_keys(origin_contents, ['number'])
		assert contents == {'patchset':'2'}
		assert conditions == {'number':'1234'}
		assert origin_contents == {'number':'1234', 'patchset':'2'}

	def test__format_update_sentence(self):
		db = MyDB("gerritci", "jobs")
		sql, values = db._format_update_sentence({'patchset':'2'}, {'number':'1234'})
		assert sql == 'UPDATE jobs SET patchset=%s WHERE number=%s'
		assert values == ('2', '1234')

	def test__update(self, mocker):
		db = MyDB("gerritci", "jobs")
		m = mocker.patch.object(MyDB, '_excute_sql_sentence')
		db._update({'patchset':'2', 'job':'ut'}, {'number':'1234'})
		m.assert_called_once_with('UPDATE jobs SET patchset=%s,job=%s WHERE number=%s', ('2', 'ut', '1234'))

	def test_write(self, mocker):
		db = MyDB("gerritci", "jobs")
		mocker.patch.object(db, '_is_existed')
		db._is_existed.return_value = False
		m = mocker.patch.object(MyDB, '_excute_sql_sentence')
		db.write({'iscompleted': 'Y', 'triggered': datetime.date(2017, 3, 9), 'created': datetime.date(2017, 3, 9), 'job_url': '/jenkins/job/gerrit-fdd-htenv-kep/', 
			'completed': datetime.date(2017, 3, 9), 'build_url': '/jenkins/job/gerrit-fdd-htenv-kep/1016/', 'number': '16277', 'started': datetime.date(2017, 3, 9), 
			'job': 'gerrit-fdd-htenv-kep', 'build': '#1016', 'patchset': '2', 'result': 'SUCCESS'}, ['build_url'])
		m.assert_called_once_with('INSERT INTO jobs (triggered,started,completed,build_url,number,job,result,iscompleted,created,job_url,build,patchset) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
			(datetime.date(2017, 3, 9), datetime.date(2017, 3, 9), datetime.date(2017, 3, 9), '/jenkins/job/gerrit-fdd-htenv-kep/1016/', '16277', 'gerrit-fdd-htenv-kep', 'SUCCESS', 'Y', datetime.date(2017, 3, 9), '/jenkins/job/gerrit-fdd-htenv-kep/', '#1016', '2'))

class TestAll:
	@pytest.mark.skip(reason="no way of currently testing this")
	def test_all(self):
		f = open("output2.txt")
		html = f.read()
		parser = HtmlParser()
		allJobs = parser.do(html)
		db = MyDB("gerritci", "jobs")
		for job in allJobs:
			#print job
			db.write(job, ['build_url'])
		
