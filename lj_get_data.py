#!/bin/python
#coding=utf-8
from bs4 import BeautifulSoup as bs
from multiprocessing import Process, Queue, Pool, Manager
from threading import Thread
import urllib2,MySQLdb,time,re

# put url_data to queue
def put_data(plate_id,plate_name,tmp_queue):
    for i in xrange(1,111):
        url = '%s/%s/d%s' % (lj_ershou_url,plate_name,i)
        try:
            url_data = urllib2.urlopen(url).read()
            tmp_queue.put((plate_id,plate_name,url_data))
        except:
            pass
    return "ok1"

# write house_id,value,price to /tmp/tmp_house.txt;
def get_data(tmp_queue):
    while q1.empty():
        time.sleep(1)
    page_data = tmp_queue.get()
    plate_id = page_data[0]
    url_data = page_data[2]
    house_div = bs(url_data,'lxml').find_all('div',attrs={'class':'info'})
    for i in house_div:
        house_id = i.find_all('a',attrs={'class':'text link-hover-green'})[0]['key']
        value = i.find('span',attrs={'class':'total-price strong-num'}).string
        price = re.findall(r'\d+',i.find('span',attrs={'class':'info-col price-item minor'}).string)[0]
        with open('/tmp/tmp_house.txt','a') as f:
            f.write('%s,%s,%s\n' % (house_id,value,price))
    return 'ok2'

if __name__ == '__main__':
    with open('/tmp/tmp_house.txt','w') as f:
        f.write('start\n' )
    lj_ershou_url = 'http://sh.lianjia.com/ershoufang'
    mysql_conn = MySQLdb.connect(host="10.10.30.209",user="root",passwd="0401@Rzc",db="lianjia",charset="utf8")
    cursor = mysql_conn.cursor()
    
    query_plate = 'select id,plate_name from plate'
    cursor.execute(query_plate)
    
    plate_all = cursor.fetchall()
    
    manager = Manager()
    q1 = manager.Queue()
    pool1 = Pool(2)
    for i in plate_all:
        res1 = pool1.apply_async(put_data,(i[0],i[1],q1))
    
    time.sleep(10)
    
    while not q1.empty():
        t = Thread(target=get_data,args=(q1,))
        t.start()
        t.join()
        if q1.empty():
            time.sleep(10)

    pool1.close()
    pool1.join()
    
    with open('/tmp/tmp_house.txt','a') as f:
        f.write('end')
