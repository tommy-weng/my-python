import datetime
import pytest

from FindCommiter import parse_item
from FindCommiter import fetch_webpage
from FindCommiter import get_trs_from_whole_webpage
from FindCommiter import get_all_commits
from FindCommiter import load_html_file

def test_parse_item():
    html = '''
<tr bgcolor="#ffbcbc" )"="">
<td></td>
<td>2017-02-16</td>
<td><a href="https://ullteb09.emea.nsn-net.net:8092/9078">LTE3701: Prepare for SPMQAPProfile expansion Replace TSerializedPMQAPProfile with the PMQAPProfile struct MatchProfile now uses PMQAPProfile</a></td>
</tr>'''
    date, id = parse_item(html)
    assert date == datetime.datetime(2017, 2, 16)
    assert id == '9078'

@pytest.mark.skip(reason="no way of currently testing this")
def test_fetch_webpage():
    html = fetch_webpage('http://ullteb09.emea.nsn-net.net:8080/view/All/job/Gerrit_new_hanging_Reviews/lastSuccessfulBuild/artifact/index.html')
    assert len(html) > 1000

def test_load_html_file():
    assert len(load_html_file("Gerrit_new_hanging_Reviews.html")) > 1000

def test_get_trs_from_whole_webpage():
    html = load_html_file("Gerrit_new_hanging_Reviews.html")
    trs = get_trs_from_whole_webpage(html)
    assert len(trs) > 20

def test_get_all_commits():
    html = load_html_file("Gerrit_new_hanging_Reviews.html")
    commits = get_all_commits(html)
    assert len(commits) > 100
