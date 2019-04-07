import requests
import MySQLdb
from scrapy.selector import Selector

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="scrapy", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺的免费ip
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
    }
    for i in range(3643):
        re = requests.get("https://www.xicidaili.com/nn/{0}".format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            else:
                speed = float(0)
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = all_texts[1]
            ip_list.append((ip, port, speed))

        for ip_info in ip_list:
            print(1)
            cursor.execute(
                "insert proxy_ip(ip,port,speed,proxy_type) VALUES('{0}','{1}',{2},'HTTP') ON DUPLICATE KEY UPDATE port = VALUES(port)".format(
                    ip_info[0], ip_info[1], ip_info[2]
                )
            )
            print(2)
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效ip
        delete_sql = """
            delete from proxy_ip where ip = '{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # 判断ip是否可用
        http_url = "https://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            print(proxy_url)
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port in Exception")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            print(code)
            if code >= 200 and code < 300:
                print("effective ip")
            else:
                print("invalid ip and port in else")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机取出一个ip和port
        random_sql = """
            select ip,port from proxy_ip
            order by rand()
            limit 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip, port)
            print(judge_re)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


get_ip = GetIP()
get_ip.get_random_ip()
