#!/usr/bin/python

import urllib
import re
from HTMLParser import HTMLParser


class ProxyInfo:
    def __init__(self, ip = "0.0.0.0", port = 0, speed = 0.0, level = "none"):
        self.ip_ = ip
        self.port_ = port
        self.speed_ = speed
        self.level_ = level
        self.inChina_ = False

    def __str__(self):
        output = self.ip_ + " " + str(self.port_) + " " + \
                 str(self.speed_) + " " + self.level_

        return output

class ProxyParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.title_list = []
        self.proxy_list = [ProxyInfo()]
        self.in_table_ = False
        self.in_thead_ = False
        self.in_tbody_ = False
        self.in_td_ = False
        self.in_th_ = False
        self.in_tr_ = False
        self.speed_ = 0.0
        HTMLParser.__init__(self, *args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if self.in_table_:
            if self.in_td_ and tag == 'div':
                hasProgressBar = False
                speed = 0.0
                for attr in attrs:
                    if attr[0] == 'class' and attr[1] == 'progress-bar':
                        hasProgressBar = True
                    if attr[0] == 'data-value':
                        speed = float(attr[1])

                if hasProgressBar:
                    self.speed_ = speed

            if tag == 'thead':
                self.in_thead_ = True
            if tag == 'tbody':
                self.in_tbody_ = True

            if tag == 'td':
                self.in_td_ = True
            if tag == 'th':
                self.in_th_ = True
            if tag == 'tr':
                self.in_tr_ = True

        elif tag == 'table':
            for attr in attrs:
                if attr[0] == 'id' and attr[1] == 'tbl_proxy_list':
                    self.in_table_ = True

    def handle_data(self, data):
        if self.in_table_ and self.in_thead_ and self.in_th_:
            self.title_list.append(data.strip())
            #print "thead: ", data.strip()
        if self.in_table_ and self.in_tbody_ and self.in_td_:
            if data.strip() != "":
                try:
                    port = int(data.strip())
                    self.proxy_list[-1].port_ = port
                    #print "port: ", port
                except:
                    pass
                result = re.match('\d+\.\d+\.\d+\.\d+', data.strip())
                if result:
                    self.proxy_list[-1].ip_ = result.group(0)
                    #print "ip: ", result.group(0)
                result = re.match('(Transparent|Anonymous|Elite)',data.strip())
                if result:
                    self.proxy_list[-1].level_ = result.group(0)
                    #print "anonymity: ", result.group(0)

                result = re.match('China',data.strip())
                if result:
                    self.proxy_list[-1].inChina_ = True
                    #print "In China "


            if self.speed_ != 0.0:
                self.proxy_list[-1].speed_ = self.speed_
                #print "speed: ", self.speed_
                self.speed_ = 0.0

    def handle_endtag(self, tag):
        if tag == 'thead':
            self.in_thead_ = False
        if tag == 'tbody':
            self.in_tbody_ = False

        if tag == 'td':
            self.in_td_ = False
        if tag == 'th':
            self.in_th_ = False
        if tag == 'tr':
            self.in_tr_ = False
            if self.proxy_list[-1].inChina_:
                self.proxy_list.append(ProxyInfo())

        if tag == 'table':
            self.in_table_ = False
            self.proxy_list.pop()

    def __str__(self):
        output = ""
        for title in self.title_list:
            output += title + " "

        output += "\n"

        for proxy in self.proxy_list:
            output += str(proxy) + "\n"

        return output

    def toProxyList(self):
        return self.proxy_list




proxy_list = urllib.urlopen('http://www.proxynova.com/proxy-server-list/country-cn/')

#print proxy_list.read()

#proxy_list = open('web.html', 'r')

pParser = ProxyParser()

pParser.feed(proxy_list.read())

print pParser