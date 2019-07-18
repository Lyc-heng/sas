import random


def random_keys(len):
    # 生成随机len长的字符串
    str = '`~-=!@#$%^&*_/+?<>{}|:[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.sample(str, len))


def random_var(len):
    # 生成随机变量名
    str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.sample(str, len))


def xor(c1, c2):
    # 字符亦或，返回16进制
    return hex(ord(c1) ^ ord(c2)).replace('0x', r"\x")


def generate(input_str):
    key = random_keys(len(input_str))
    output_str = "$result="
    process = ""
    for i in range(0, len(input_str)):
        enc = xor(input_str[i], key[i])
        var = random_var(3)
        process += f'$_{var}="{key[i]}"^"{enc}";'
        process += '\n'
        output_str += '$_%s.' % var
    output_str = output_str.rstrip('.') + ';'
    print(process)
    print(output_str)


def php_confusion():
    input_str = input('请输入要混淆的变量:\r\n')
    generate(input_str)
