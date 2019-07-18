import sys
import time
import requests
from threading import Thread
import termcolor


class request_leak_source(Thread):
    def __init__(self, word, url):
        Thread.__init__(self)
        try:
            self.word = word.split("\n")[0]
            self.url = url
        except Exception as e:
            print(e)

    def run(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
            testurl = self.url + self.word.replace("\n", "")
            flag = 0
            print('testing: ' + testurl + '                   \r', end='', flush=True)
            print('\033[1;33m[*]test:  %s\033[0m' % testurl)
            if 'zip' in self.word or 'rar' in self.word or 'gz' in self.word or 'sql' in self.word or 'tore' in testurl:
                req = requests.head(testurl, headers=headers, timeout=3, allow_redirects=False)
                if req.status_code == 200:
                    if 'html' not in req.headers['Content-Type'] and 'image' not in req.headers['Content-Type']:
                        flag = 1
            else:
                req = requests.get(testurl, headers=headers, timeout=3, allow_redirects=False)
                if req.status_code == 200:
                    if 'svn' in self.word:
                        if 'dir' in req.content and 'svn' in req.content:
                            flag = 1
                    elif 'git' in self.word:
                        if 'repository' in req.content:
                            flag = 1
                    elif 'hg' in self.word:
                        if 'hg' in req.content:
                            flag = 1
                    elif '/WEB-INF/web.xml' in self.word:
                        if 'web-app' in req.content:
                            flag = 1
            if flag == 1:
                print(termcolor.colored("\033[1;31m[+]信息泄露\tpayload: %s\033[0m" % testurl, 'red'))
            i[0] = i[0] - 1
        except Exception as e:
            print(e)

        print('                                 \r', end='', flush=True)


def launcher_source_leak_thred(words, th, url):
    global i
    i = []
    i.append(0)
    while len(words):
        try:
            if i[0] < int(th):
                n = words.pop(0)
                i[0] = i[0] + 1
                thread = request_leak_source(n, url)
                thread.start()
        except KeyboardInterrupt:
            print("用户停止了程序运行。完成探测")
            sys.exit()
    return True


def scan_leak(opts):
    start_time = time.time()
    # 默认线程数为4
    threads = 4
    for opt, arg in opts:
        if opt == '-l':
            url = arg
            if '//' not in url:
                url = 'http://' + url
        elif opt == '-f':
            dicts = arg
        elif opt == '-t':
            threads = arg
        else:
            print("错误的参数")

    try:
        f = open(dicts, 'r')
        words = f.readlines()
    except:
        print("打开文件错误：", dicts, "\n")
        sys.exit()

    print("检测开始")

    launcher_source_leak_thred(words, threads, url)

    end_time = time.time()
    print("本次扫描共消耗 %0.6f 秒" % (end_time - start_time))
