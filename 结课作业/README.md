# Web渗透测试

## 实验介绍

在如今的软件越来越多的情况下，人工进行漏洞测试逐渐变成一种费时间、测试面又窄的方法，所以逐渐出现了全自动的测试工具，例如sqlmap、wfuzz等等。
原本项目是打算结合模糊测试去进行渗透测试的，经过多次试验后选择了sully。但由于时间有限，最后实现的效果并不如预期那么好，所以这里先提交效果更好的版本，后续会根据缺陷再进行改进，让其实现模糊测试去进行渗透的效果。
最后实现的效果为支持目录扫描、端口扫描、SQL注入等常见漏洞的渗透测试，并实现支持输出结果过滤、携带payload、携带cookie等细节。

## 试验环境

- Windows 10

- Python 3.7

- DVWA 1.10

- nmap 7.70

## 实验实现

能够使用命令行的方式去进行渗透测试

实现了以下功能点：

- 输入网址进行渗透测试

- 多线程测试

- Web资源探测

- 端口扫描

- 文件泄露扫描

- HTTP认证、表单认证破解

- 用户名以及密码暴力破解

- SQL注入检测

- XSS注入检测

- 支持get、post方法

- 支持输入cookie

- 支持将感兴趣的网页自动截图保存

- 可选择字典文件

- 支持PHP变量混淆

## 实验的思路

- 接受命令行输入参数，将输入数据转化为字典

- 根据输入的参数决定调用的函数

分解输入参数

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

## 目录结构

    |--src
        |-- fuzzdb（一些写好的常用字典或者数据，可直接调用）
        |-- screenshot（截图后所保存的文件夹）
        |-- main.py（主文件，实现分析输入参数、SQL注入、资源探索等功能）
        |-- port_scan.py（基于nmap实现端口扫描功能）
        |-- source_leak.py（实现源码扫描功能）
        |-- php_confusion.py（实现php变量混淆功能）
        |-- 其他.txt文件皆为测试用字典文件

## 使用说明

- 打开命令行

- 使用`-h`查看帮助信息，或者不输入参数也能查看

- 根据情况输入参数

- 参数说明：

    - `-w` : 选择进行测试的网址
    
    - `-t` : 选择测试时使用的线程数
    
    - `-f` : 选择使用的字典文件

    - `-c` : 过滤特定的返回状态码

    - `-s` : 将符合结果的页面自动进行截图保存

    - `-m` : 选择破解的认证方式，支持HTTP基本认证和HTTP表单认证

    - `-u` : 用户名，一般与`-m`一起使用

    - `-p` : 破解表单认证方式，支持get和post两种常用方式

    - `-i` : sql注入，支持输入payload

    - `-x` : xss注入，支持输入payload

    - `-a` : 设置cookie

    - `-o` : 端口扫描

    - `-f` : 源码泄露扫描

    - `-b` : PHP变量混淆

## 实验结果

以DVWA为对象，尝试进行渗透

- 网站资源进行探测

        python main.py -w http://127.0.0.1/dvwa/ -t 4 -f common.txt

    ![](img/2.png)

- 对网站资源进行探测，过滤404情况

        python main.py -w http://127.0.0.1/dvwa/ -t 4 -f common.txt -c 404

    ![](img/1.png)

- 对网站资源进行探测，将非404结果以截图的形式保存

        python main.py -w http://127.0.0.1/dvwa/ -t 4 -f common.txt -c 404 -s

    ![](img/3.png)

- 带cookie的sql注入检测

        python main.py -w "http://127.0.0.1/dvwa/vulnerabilities/sqli/?id=FUZZ&Submit=Submit#" -t 4 -f MySQL.txt  -i "" -a "PHPSESSID=8atmsl8rhf7hqac39dgn2g8ilm&security=low"

    ![](img/4.png)

- 带cookie的xss检测

        python main.py -w http://127.0.0.1/dvwa/vulnerabilities/xss_r/?name=FUZZ# -t 4 -f xss-rsnake.txt -x "" -a "PHPSESSID=qnvh2vgteojn5ppiaigra9pa6j&security=low"

    ![](img/5.png)

- 源码泄露检测，DVWA没有检测到泄露

        python main.py -l http://127.0.0.1/dvwa -t 4 -f source_leak_scan.txt

    ![](img/6.png)

## 总结

本次实验学习了常见的Web渗透测试的方法和相关常见的web漏洞并完成了自动化工具的构建，虽然还有很多细节没有考虑到的地方，后面会进行完善并结合模糊测试进去

实现部分的代码已经给出了详细的注释