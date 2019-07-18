import time
import nmap
import termcolor


def scanner(url, ports):
    nm = nmap.PortScanner()
    try:
        print('Scanner report for %s\n' % url)
        if len(ports) == 0:
            result = nm.scan(url)
        else:
            result = nm.scan(url, ports)
        if result['nmap']['scanstats']['uphosts'] == '0':
            print(termcolor.colored('Host seems down', 'red'))
        else:
            print('Host is up')
            print("{:<7}\t{:<7}\t{:<7}\t{:<7}".format('PORT', 'STATE', 'SERVICE', 'VERSION'))
            for k, v in result['scan'][url]['tcp'].items():
                if v['state'] == 'open':
                    print(termcolor.colored("{:<7}\t{:<7}\t{:<7}\t{:<7}".format(str(k), v['state'], v['name'],
                                                                                v['product'] + v['version']), 'yellow'))
                else:
                    print(termcolor.colored("{:<7}\t{:<7}".format(str(k), v['state']), 'yellow'))
    except Exception as e:
        print(termcolor.colored("unhandled Option", 'red'))


def scan(opts):
    start_time = time.time()
    # 读参数
    for opt, arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-o':
            ports = arg
    print("扫描开始...")

    scanner(url, ports)

    print("扫描结束...")
    end_time = time.time()
    print("\n\n本次扫描共花费 %0.6f 秒" % (end_time - start_time))


if __name__ == '__main__':
    nm = nmap.PortScanner()
    nm.scan('192.168.10.10-100', '22,21', '-sV')
    a = nm.scaninfo()
    print(a)
