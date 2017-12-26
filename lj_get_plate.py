#!/bin/python
#coding=utf-8
from bs4 import BeautifulSoup as bs
#from Queue import Queue
from multiprocessing import Process, Queue
import urllib2,MySQLdb
#import threading

lj_ershou_url = 'http://sh.lianjia.com/ershoufang'
lj_ershou_page = urllib2.urlopen(lj_ershou_url).read()
mysql_conn = MySQLdb.connect(host="10.10.30.209",user="root",passwd="0401@Rzc",db="lianjia",charset="utf8")
cursor = mysql_conn.cursor()

lj_page_soup = bs(lj_ershou_page,'lxml')

level1 = lj_page_soup.find('div',attrs={'class':'level1'})
level1_a = level1.find_all('a')

district = []
for i in level1_a:
    district.append(i['gahref'])

district = district[1:]
district_id = {}
n = 1
district_sql = 'insert into district(id,district_name) value(%s,%s)'
for i in district:
    district_id[i] = n
    cursor.execute(district_sql,(n,i))
    n += 1
    mysql_conn.commit()
    
q1 = Queue()

def get_plates(district_name):
    plates = []
    dir_tmp = {}
    plates_url = lj_ershou_url + '/' + district_name
    plates_page = urllib2.urlopen(plates_url).read()
    plates_soup = bs(plates_page,'lxml')
    level2 = plates_soup.find('div',attrs={'class':'level2 gio_plate'})
    level2_a = level2.find_all('a')
    for i in level2_a:
        plates.append(i['gahref'])
    plates = plates[1:]
    dir_tmp[district_name]=plates
    q1.put(dir_tmp)

district_dir = {}
thread_list = []

for i in district:
    #thread_list.append(threading.Thread(target=get_plates,args=(i,)))
    thread_list.append(Process(target=get_plates,args=(i,)))

for i in thread_list:
    i.start()
    i.join()

while not q1.empty():
    district_dir = dict(district_dir, **q1.get())

plate_sql = 'insert into plate(id,plate_name,district_id) value(%s,%s,%s)'
n = 1
for k,v in district_dir.items():
    for i in v:
        cursor.execute(plate_sql,(n,i,district_id[k]))
        n += 1
    mysql_conn.commit()

cursor.close()
mysql_conn.close()
#print district_id
