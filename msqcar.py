import requests,re,time,random,pymysql,sys
from hashlib import md5



class CarSpider():
    def __init__(self):
        self.url = 'https://www.che168.com/beijing/a0_0msdgscncgpi1lto1csp{}exx0/'
        self.headers = {'Accept-Encoding':'gzip, deflate, br','Upgrade-Insecure-Requests': '1','User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        self.db = pymysql.connect('localhost','root','123456','cardb',charset='utf8')
        self.cursor = self.db.cursor()

    def md5_html(self,url):
        """对url地址进行md5的加密"""
        s = md5()
        s.update(url.encode())

        return s.hexdigest()

    def get_html(self,url):
        html = requests.get(url=url,headers=self.headers).text
        return html

    def re_func(self,regex,html):
        pattern=re.compile(regex,re.S)
        r_list=pattern.findall(html)

        return r_list

    def parse_html(self,one_url):
        one_html = self.get_html(one_url)
        one_regex = ' <li class="cards-li list-photo-li".*?<a href="(.*?)" .*?</li>'
        href_list = self.re_func(one_regex,one_html)
        for href in href_list:
            two_url = 'https://www.che168.com' + href
            finger = self.md5_html(two_url)
            sel = 'select * from request_finger where finger=%s'
            self.cursor.execute(sel,[finger])
            result = self.cursor.fetchall()
            if not result:
                #抓取一辆汽车的信息
                self.get_car_info(two_url)
                time.sleep(random.uniform(1, 2))
                add = 'insert into request_finger value(%s)'
                self.cursor.execute(add,[finger])
                self.db.commit()
            else:
                sys.exit('抓取结束')

    def get_car_info(self,two_url):
        two_html = self.get_html(two_url)
        two_regex = '<div class="car-box">.*?<h3 class="car-brand-name">(.*?)</h3>.*?<ul class="brand-unit-item fn-clear">.*?<li>.*?<h4>(.*?)</h4>.*?<h4>(.*?)</h4>.*?<h4>(.*?)</h4>.*?<h4>(.*?)</h4>.*?<span class="price" id="overlayPrice">￥(.*?)<b>'
        r_list = self.re_func(two_regex,two_html)
        item={}
        item['name'] = r_list[0][0].strip()
        item['km'] = r_list[0][1].strip()
        item['time'] = r_list[0][2].strip()
        item['type'] = r_list[0][3].split('/')[0].strip()
        item['displace'] = r_list[0][3].split('/')[1].strip()
        item['address'] = r_list[0][4].strip()
        item['price'] = r_list[0][5].strip()

        li = [
            item['name'],
            item['km'],
            item['time'],
            item['type'],
            item['displace'],
            item['address'],
            item['price'],
        ]
        ins = 'insert into cartab values(%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(ins,li)
        self.db.commit()
        print(item)

    def run(self):
        for i in range(1,59):
            url = self.url.format(i)
            self.parse_html(url)
        self.cursor.close()
        self.db.close()


if __name__ == '__main__':
    spider = CarSpider()
    spider.run()
