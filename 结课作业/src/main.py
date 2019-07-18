import requests
from threading import Thread
import sys
import getopt
import termcolor
import re
from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options
from requests.auth import HTTPDigestAuth
import port_scan
import source_leak
import php_confusion

global valid
valid = '1'


# 暴力探测器
class request_resources(Thread):
    def __init__(self, word, url, hidecode, savescreenshot):
        Thread.__init__(self)
        try:
            self.word = word.split("\n")[0]
            self.url = url + word.replace("\n", "")
            self.hidecode = hidecode
            self.savescreenshot = savescreenshot
        except Exception as e:
            print(e)

    def run(self):
        try:
            r = requests.get(self.url)
            # 获得网页行数
            lines = r.text.count("\n")
            # 获得网页字符数
            charts = len(r._content)
            # 获得网页词数
            words = len((re.findall(r"\S+", r.text)))
            # 获得状态码
            scode = r.status_code
            if scode != self.hidecode:
                result = '\t\t' + " " + str(charts) + '\t' + " " + str(lines) + '\t' + " " + str(
                    words) + '\t\t' + " " + self.url
                if scode < 300 and scode >= 200:
                    print(termcolor.colored(scode, 'green'), end="")
                elif scode >= 300 and scode < 400:
                    print(termcolor.colored(scode, 'blue'), end="")
                elif scode >= 400:
                    print(termcolor.colored(scode, 'red'), end="")
                else:
                    print(termcolor.colored(scode, 'yellow'), end="")
                print(result)
                self.screenshot()
            i[0] = i[0] - 1
        except Exception as e:
            print(e)

    def screenshot(self):
        if (self.savescreenshot):
            path = os.path.abspath(os.path.dirname(sys.argv[0])) + '\\screenshot\\'
            prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': path}

            # 设置浏览器的相关配置
            chrome_options = Options()
            chrome_options.add_experimental_option('prefs', prefs)
            chrome_options.add_argument("--headless")

            browser = webdriver.Chrome(options=chrome_options)

            try:
                browser.get(self.url)
            except TimeoutError:
                print("Time Out，try again")
                browser.get(self.url)

            browser.set_window_size(1024, 768)
            browser.save_screenshot(path + self.word + ".png")

            return True


# 常规登录
class request_auth_password(Thread):
    def __init__(self, name, user, url, method):
        Thread.__init__(self)
        try:
            self.password = name.split("\n")[0]
            self.username = user
            self.url = url
            self.method = method
        except Exception as e:
            print(e)

    def run(self):
        global valid
        if valid == '1':
            try:
                if self.method == 'basic':
                    r = requests.session()
                    r = r.get(self.url, auth=(self.username, self.password))
                elif self.method == 'digest':
                    r = requests.session()
                    r = r.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
                if r.status_code == 200:
                    valid = '0'
                    print("[+]发现密码：" + termcolor.colored(self.password, 'green'))
                    sys.exit()
                else:
                    print("无效的密码：" + self.password)
                i[0] = i[0] - 1
            except Exception as e:
                print(e)


# 表单登录
class request_form_password(Thread):
    def __init__(self, word, url, hidecode, payload):
        Thread.__init__(self)
        try:
            self.word = word.split("\n")[0]
            self.url = url
            self.hidecode = hidecode
            self.payload = payload
            if payload == "":
                self.url = (self.url).relace("Fuzz", word.replace("\n", ""))
            else:
                self.url = url
        except Exception as e:
            print(e)

    def run(self):
        try:
            # 判断是否指定payload
            if self.payload != "":
                lists = self.payload.replace("FUZZ", self.word).replace("=", " ").replace("&", " ").split(" ")
                payload = dict([(k, v) for k, v in zip(lists[::2], lists[1::2])])
                r = requests.session()
                r = r.post(self.url, data=payload)
            else:
                r = requests.session()
                r = r.get(self.url)
            # 统计网页行数
            lines = str(r.text.count("\n"))
            # 统计网页字符数
            charts = str(len(r.text))
            # 统计网页词数
            words = str(len(re.findall(r"\S+", r.text)))
            # 状态码
            scode = str(r.status_code)
            # 判断是否重定向
            if r.history != []:
                first = r.history[0]
                scode = str(first.status_code)
            else:
                pass
            if scode != str(self.hidecode):
                if int(scode) >= 200 and int(scode) < 300:
                    print(termcolor.colored(scode, 'green') + "\t" + charts + "  \t" + lines + "   \t" + words + "\t" +
                          r.headers[
                              'server'] + "\t" + self.word)
                elif int(scode) >= 400 and int(scode) < 500:
                    print(termcolor.colored(scode, 'red') + "\t" + charts + "  \t" + lines + "   \t" + words + "\t" +
                          r.headers[
                              'server'] + "\t" + self.word)
                elif int(scode) >= 300 and int(scode) < 400:
                    print(termcolor.colored(scode, 'blue') + "\t" + charts + " \t" + lines + "   \t" + words + "\t" +
                          r.headers[
                              'server'] + "\t" + self.word)
                else:
                    print(
                        termcolor.colored(scode, 'yellow') + "\t" + charts + "   \t" + lines + "   \t" + words + "\t" +
                        r.headers[
                            'server'] + "\t" + self.word)
            i[0] = i[0] - 1
        except Exception as e:
            print(e)


# sql注入
class request_sql(Thread):
    def __init__(self, word, url, payload, webcookie):
        Thread.__init__(self)
        try:
            self.word = word.split("\n")[0]
            self.url = url
            self.payload = payload
            if payload == "":
                self.origin = len(re.findall(r"\S+", requests.post(self.url).text))
                self.url = (self.url).replace("FUZZ", word.replace("\n", ""))
            else:
                self.origin = len(re.findall(r"\S+", requests.get(self.url).text))
                self.url = url
            if webcookie != "":
                lists = webcookie.replace("=", " ").replace("&", " ").split(" ")
                self.cookies = dict([(k, v) for k, v in zip(lists[::2], lists[1::2])])
            else:
                self.cookies = ""
        except Exception as e:
            print(e)

    def run(self):
        try:
            if self.payload != "":
                lists = self.payload.replace("=", " ").replace("&", " ").split(" ")
                payload = dict([(k, v) for k, v in zip(lists[::2], lists[1::2])])
                r = requests.session()
                r = r.post(self.url, data=payload, cookies=self.cookies)
            else:
                r = requests.session()
                r = r.get(self.url, cookies=self.cookies)
            # 统计网页行数
            lines = str(r.text.count("\n"))
            # 统计网页字符数
            charts = str(len(r.text))
            # 统计网页词数
            words = str(len(re.findall(r"\S+", r.text)))
            # 状态码
            scode = str(r.status_code)
            # 判断是否重定向
            if r.history != []:
                first = r.history[0]
                scode = str(first.status_code)
            else:
                pass
            if self.payload != "":
                print(payload)
                if words != self.origin:
                    print("sql注入成功：" + termcolor.colored(payload, 'red'))
            else:
                print(self.url)
                if words != self.origin:
                    print("sql注入成功：" + termcolor.colored(self.url, 'red'))
            i[0] = i[0] - 1
        except Exception as e:
            print(e)


# xss注入
class request_xss(Thread):
    def __init__(self, word, url, payload, webcookie):
        Thread.__init__(self)
        try:
            self.word = word.split("\n")[0]
            self.url = url
            self.payload = payload
            if payload == "":
                self.url = (self.url).replace("FUZZ", word.replace("\n", ""))
            else:
                self.url = url
            if webcookie != "":
                lists = webcookie.replace("=", " ").replace("&", " ").split(" ")
                self.cookies = dict([(k, v) for k, v in zip(lists[::2], lists[1::2])])
            else:
                self.cookies = ""
        except Exception as e:
            print(e)

    def run(self):
        try:
            if self.payload != "":
                lists = self.payload.replace("=", " ").replace("&", " ").split(" ")
                payload = dict([(k, v) for k, v in zip(lists[::2], lists[1::2])])
                r = requests.session()
                r = r.post(self.url, data=payload, cookies=self.cookies)
            else:
                r = requests.session()
                r = r.get(self.url, cookies=self.cookies)
            # 统计网页词数
            words = str(len(re.findall(r"\S+", r.text)))
            # 状态码
            scode = str(r.status_code)
            # 判断是否重定向
            if r.history != []:
                first = r.history[0]
                scode = str(first.status_code)
            else:
                pass
            if self.payload != "":
                print(payload)
                if self.word in r.text:
                    print(termcolor.colored(payload, 'red'))
            else:
                print(self.url)
                if self.word in r.text:
                    print(termcolor.colored(self.url, 'red'))
            i[0] = i[0] - 1
        except Exception as e:
            print(e)


# 程序标识
def banner():
    print("\n********************")
    name = "2019年软件与系统安全大作业"
    print(name, end="\n\n")
    print("201611123021 2016信息安全 李沅城", end="\n\n")
    print("***********************")


# 程序用法
def usage():
    print("用法：")
    # 设置网址
    print("     -w:网址 (http://127.0.0.1/dvwa/)")
    # 设置线程数
    print("     -t:线程数")
    # 当为basci、digest认证时，输入用户名
    print("     -u:用户名")
    # 设置字典文件
    print("     -f:字典文件")
    # 设置过滤的状态结果
    print("     -c: 隐藏的状态码")
    # 将感兴趣的页面自动保存下来
    print("     -s")
    # 打印帮助信息
    print("     -h")
    # 认证主要分为基本认证、摘要认证
    print("     -m:认证方式(basic、digest)")
    # 表单认证时需指定用户名和密码参数
    print("     -p:用户名和密码")
    # SQL注入，无payload默认通过get方法去进行访问，如果有则post方法
    print("     -i:payload")
    # XSS注入，无payload默认通过get方法去进行访问，如果有则post方法
    print("     -x:payload")
    # 设置cookie
    print("     -a:cookir")
    # 设置扫描的端口
    print("     -o:端口号（支持单个、多个端口以及一组范围内所有端口）")
    # 源码泄露扫描
    print("     -f:字典文件")
    # PHP变量混淆
    print("     -b")
    print("例子：python main.py -w http://127.0.0.1/dvwa/ -t 4 -f common.txt -c 404 -s")
    print("例子：python main.py -w http://127.0.0.1/dvwa/ -u admin -t 5 -f pass.txt -m basic")
    print(
        "例子：python main.py -w http://127.0.0.1/dvwa/login.php -t 4 -f john.txt -p \"username=121212&password=FUZZ&Login=Login&user_token=24a0e27b293c5c0d75b871607df02a67\"")
    print(
        "例子：python main.py -w \"http://127.0.0.1/dvwa/vulnerabilities/sqli/?id=FUZZ&Submit=Submit#\" -t 4 -f MySQL.txt  -i \"\" ")
    print(
        "例子：python main.py -w \"http://127.0.0.1/dvwa/vulnerabilities/sqli/?id=FUZZ&Submit=Submit#\" -t 4 -f MySQL.txt  -i \"\" -a \"PHPSESSID=qnvh2vgteojn5ppiaigra9pa6j&security=low\"")
    print(
        "例子：python main.py -w http://127.0.0.1/dvwa/vulnerabilities/xss_r/?name=FUZZ# -t 4 -f xss-rsnake.txt -x \"\" ")
    print(
        "例子：python main.py -w http://127.0.0.1/dvwa/vulnerabilities/xss_r/?name=FUZZ# -t 4 -f xss-rsnake.txt -x "" -a \"PHPSESSID=qnvh2vgteojn5ppiaigra9pa6j&security=low\" ")
    print("例子：python main.py -w 127.0.0.1 -o 80-1000")
    print("例子：python main.py -l http://127.0.0.1/dvwa -t 4 -f source_leak_scan.txt")
    print("例子：python main.py -b")

# 初始化线程进行探测
def launcher_resources_thread(names, th, url, hidecode, savescreenshot):
    global i
    i = []
    i.append(0)
    print("Start probe resources")
    print("=======================================================================================")
    print("状态码" + '\t\t' + "字符数" + '\t' + "行数" + '\t' + "词数" + "\t\t" + "url")
    print("=======================================================================================")
    while len(names):
        try:
            if i[0] < th:
                n = names.pop(0)
                i[0] = i[0] + 1
                thread = request_resources(n, url, hidecode, savescreenshot)
                thread.start()
        except KeyboardInterrupt:
            print("用户停止了程序运行。完成探测")
            sys.exit()
    return True


# 探测资源
def probe_resources(opts):
    hidecode = 0
    savescreenshot = False
    for opt, arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-f':
            dicts = arg
        elif opt == '-t':
            threads = int(arg)
        elif opt == '-c':
            hidecode = int(arg)
        elif opt == '-s':
            savescreenshot = True

    try:
        f = open(dicts, 'r')
        words = f.readlines()
    except Exception as e:
        print("打开文件错误：", dicts, "\n")
        print(e)
        sys.exit()

    launcher_resources_thread(words, threads, url, hidecode, savescreenshot)


# 初始化线程进行auth密码爆破
def launcher_auth_password_thread(passwords, th, username, url, method):
    global i
    i = []
    print("==============================================")
    i.append(0)
    while len(passwords):
        if valid == '1':
            try:
                if i[0] < int(th):
                    passwd = passwords.pop(0)
                    i[0] = i[0] + 1
                    thread = request_auth_password(passwd, username, url, method)
                    thread.start()
            except KeyboardInterrupt:
                print("用户停止了程序运行。完成探测")
                sys.exit()
            thread.join()
    return True


# 常规登录密码
def blast_password(opts):
    for opt, args in opts:
        if opt == '-u':
            user = args
        elif opt == '-w':
            url = args
        elif opt == '-f':
            dicts = args
        elif opt == '-t':
            threads = args
        elif opt == '-m':
            method = args
    try:
        f = open(dicts, 'r')
        passwords = f.readlines()
    except:
        print("打开文件错误：", dicts, "\n")
        sys.exit()
    launcher_auth_password_thread(passwords, threads, user, url, method)


# 表单密码
def launcher_form_password_thread(names, th, url, hidecode, payload):
    global i
    i = []
    print("==============================================")
    print("状态码" + "\t" + "字符数" + "\t" + "行数" + "\t" + "词数" + "\t" + "服务器" + "\t" + "数据")
    print("==============================================")
    i.append(0)
    while len(names):
        try:
            if i[0] < int(th):
                n = names.pop(0)
                i[0] = i[0] + 1
                thread = request_form_password(n, url, hidecode, payload)
                thread.start()
        except KeyboardInterrupt:
            print("用户停止了程序运行。完成探测")
            sys.exit()
    return True


# 表单密码
def form_blast_password(opts):
    hidecode = 000
    payload = ""
    for opt, arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-f':
            dicts = arg
        elif opt == '-t':
            threads = arg
        elif opt == '-c':
            hidecode = arg
        elif opt == '-p':
            payload = arg

    try:
        f = open(dicts, 'r')
        words = f.readlines()
    except:
        print("打开文件错误：", dicts, "\n")
        sys.exit()

    launcher_form_password_thread(words, threads, url, hidecode, payload)


# sql注入
def launcher_sql_thread(words, th, url, payload, webcookie):
    global i
    i = []
    i.append(0)
    while len(words):
        try:
            if i[0] < int(th):
                n = words.pop(0)
                i[0] = i[0] + 1
                thread = request_sql(n, url, payload, webcookie)
                thread.start()
        except KeyboardInterrupt:
            print("用户停止了程序运行。完成探测")
            sys.exit()
    return True


# sql注入
def sql_inject(opts):
    payload = ""
    webcookie = ""
    for opt, arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-f':
            dicts = arg
        elif opt == '-t':
            threads = arg
        elif opt == '-i':
            payload = arg
        elif opt == '-a':
            webcookie = arg

    try:
        f = open(dicts, 'r')
        words = f.readlines()
    except:
        print("打开文件错误：", dicts, "\n")
        sys.exit()

    launcher_sql_thread(words, threads, url, payload, webcookie)


# xss检测
def launcher_xss_thred(words, th, url, payload, webcookie):
    global i
    i = []
    i.append(0)
    while len(words):
        try:
            if i[0] < int(th):
                n = words.pop(0)
                i[0] = i[0] + 1
                thread = request_xss(n, url, payload, webcookie)
                thread.start()
        except KeyboardInterrupt:
            print("用户停止了程序运行。完成探测")
            sys.exit()
    return True


# xss检测
def xss_inject(opts):
    payload = ""
    webcookie = ""
    for opt, arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-f':
            dicts = arg
        elif opt == '-t':
            threads = arg
        elif opt == '-x':
            payload = arg
        elif opt == '-a':
            webcookie = arg

    try:
        f = open(dicts, 'r')
        words = f.readlines()
    except:
        print("打开文件错误：", dicts, "\n")
        sys.exit()

    launcher_xss_thred(words, threads, url, payload, webcookie)


# 分析参数执行动作
def start():
    banner()
    if len(sys.argv) < 2:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w:t:u:f:l:m:p:c:i:x:a:o:bhs")
        if check(opts, "-u"):
            # HTTP基本认证和HTTP摘要认证
            blast_password(opts)
        elif check(opts,"-h"):
            # 帮助信息打印
            usage()
        elif check(opts, "-p"):
            # 表单认证
            form_blast_password(opts)
        elif check(opts, "-i"):
            # sql注入
            sql_inject(opts)
        elif check(opts, "-x"):
            # xss检测
            xss_inject(opts)
        elif check(opts,"-o"):
            # 端口检测
            port_scan.scan(opts)
        elif check(opts,"-l"):
            # 源码泄露检测
            source_leak.scan_leak(opts)
        elif check(opts,"-b"):
            # php混淆
            php_confusion.php_confusion()
        else:
            # 目录探测
            probe_resources(opts)
    except getopt.GetoptError:
        print("错误的参数")
        sys.exit()


# 检查输入参数
def check(opts, cchar):
    for opt, arg in opts:
        if opt == cchar:
            return True
    return False


if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        print("用户停止了程序运行。完成探测")
