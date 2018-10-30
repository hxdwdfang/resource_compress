# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author :dfwang
# email:249581930@qq.com
# 主要是针对iOS资源文件夹进行遍历压缩，暂没尝试过android对整个目录去压缩的时间估计
# 执行方式（运行环境请选择python3，python2因为一些api问题可能会报错）
# 1.terminal中 python3 resource_compress.py tinyPNG_key  source_path
# 2.通过配置tinyPNG_key、source_path
#   2.1 在config.json中填入相关信息
#   2.2 terminal中执行python3 resource_compress.py

import sys
import json
import os
import signal
import tinify
import resource_file_operation

# ##默认参数key,用来读取config中的配置的
source_path_key = "source_path"
backup_key = "need_backup"
tinypng_key = "tinypng_key"
# 主要是为中断保存,正常任务执行完时都能保存缓存文件
compressed_path = []


def load_configs():
    # ##加载配置文件里的json信息
    with open('./config.json', 'r') as config:
        return json.load(config)


def make_empty_dir(_dir):
    # 创建空文件夹
    if not os.path.exists(_dir):
        os.makedirs(_dir)


def get_all_paths(source_dir, target_dir):
    # ###创建目标跟目录，并且获取所有子目录信息
    # ###传入的sourceDir为原路径，targetDir为目标路径

    # 收集所有文件的后缀，方便查看是否有漏网之鱼
    all_suffix = []
    # 读取已经缓存的文件
    cached_path_list = resource_file_operation.from_file()

    # 确保目标文件夹存在，不存在文件夹，创建文件夹
    make_empty_dir(target_dir)

    # 获取所有待压缩文件目录路径数组与目标路径数组（二者是一一对应的）
    (source_paths, target_paths) = get_sub_paths(all_suffix, cached_path_list, source_dir, target_dir)
    print("all_file_suffix = ", all_suffix)
    return source_paths, target_paths


def get_sub_paths(all_suffix, cached_path_list, root_source_dir, root_target_dir):
    # 递归比较生成目标子路径

    source_paths = []
    target_paths = []

    # 当前查找目录
    # print("--------- begin find dir {0} ---------".format(root_source_dir.encode("utf-8")))
    # 排序一下每次压缩都安这顺序
    root_source_sub_dirs = os.listdir(root_source_dir)
    root_source_sub_dirs.sort()
    for filename in root_source_sub_dirs:
        # print("fileName = ", filename)
        #是否是文件夹，是文件夹那么就递归往下找
        if os.path.isdir(os.path.join(root_source_dir, filename)):
            # 路径
            sub_source_dir = os.path.join(root_source_dir, filename)
            sub_target_dir = os.path.join(root_target_dir, filename)

            # 创建空文件夹
            make_empty_dir(sub_target_dir)
            # 递归文件夹下的文件
            (sub_path, target_path) = get_sub_paths(all_suffix, cached_path_list, sub_source_dir, sub_target_dir)
            source_paths.extend(sub_path)
            target_paths.extend(target_path)
        else:
            # ##文件是图片资源的时候用tinypng的sdk去压缩，不是图片的时候copy到目标目录，要不然images.xcassets里默认加的json就要手动去copy一份
            # 文件的情况判断是否为可压缩图片,获取文件后缀
            source_file_path = os.path.join(root_source_dir, filename)
            target_file_path = os.path.join(root_target_dir, filename)
            f_name, suffix = os.path.splitext(filename)
            # 只取后缀，去掉.
            lower_suffix = suffix.lower()[1:]
            # 收集后缀
            if lower_suffix.__len__() > 0 and not all_suffix.__contains__(lower_suffix):
                all_suffix.append(lower_suffix)

            if lower_suffix == "png" or lower_suffix == "jpg" or lower_suffix == "jpeg":
                # 是要压缩的图片的时候，把路径加入待压缩数组中
                # 如果缓存路径里有这个路径，那么直接跳过（因为默认缓存路径是固定的，所以target_file_path为标记）
                if cached_path_list.__contains__(target_file_path):
                    # print("{0} had compressed! copy direct~~~".format(target_file_path.encode("utf-8")))
                    resource_file_operation.copy_file(source_file_path, target_file_path)
                else:
                    source_paths.append(source_file_path)
                    target_paths.append(target_file_path)
            else:
                # 这里处理非png、jpg的文件，现在只是简单copy到目标目录中去,像xcassets中的config.json文件等,让直接压缩后的图片
                # print("copy file {0} to {1}".format(source_file_path.encode("utf-8"),
                #  target_file_path.encode("utf-8")))
                resource_file_operation.copy_file(source_file_path, target_file_path)
    # print("--------- end find dir {0} ---------".format(root_source_dir.encode("utf-8")))
    return source_paths, target_paths


def empty_params(param):
    return len(param) == 0


###解析加载参数
def parse_params():
    """
    创建备份目录，所有的操作都是在备份目录做的
    获取参数
    1.命令行执行时后面跟的参数
    2.读取config.json里配置的参数
    """

    # 默认读配置，如果config中有配置项就当默认值，没有的时候就默认空
    _result = load_configs()
    tinify_api_keys = _result[tinypng_key] if tinypng_key in _result else ""
    source_path = _result[source_path_key] if source_path_key in _result else ""
    need_backup = _result[backup_key] if backup_key in _result else True

    print(sys.argv)
    # 如果命令行里有跟参数，那么读命令行的参数，没有就读配置的参数 第一个参数是文件名
    tinify_api_keys = sys.argv[1] if len(sys.argv) > 1 else tinify_api_keys
    source_path = sys.argv[2] if len(sys.argv) > 2 else source_path
    need_backup = sys.argv[3] if len(sys.argv) > 3 else need_backup

    # 判断一下所有key是否为空
    if empty_params(tinify_api_keys) or empty_params(source_path):
        print("请检查输入参数,请确保输入tinyPNG_key、 source_path")
        exit()

    # 如果tinify_api_keys不是一个list,就创建一个list把它放进去，方便后续查找替换，免得一直去判断是否是list
    if not type(tinify_api_keys) is list:
        new_list = list()
        new_list.append(tinify_api_keys)
        tinify_api_keys = new_list

    # list去重
    tinify_api_keys = list(set(tinify_api_keys))

    print("tinify_api_key = {0}, source_path = {1}".format(tinify_api_keys, source_path.encode("utf-8")))
    return tinify_api_keys, source_path, need_backup


def choose_tinify_key(keys):
    # 从配置的array中选择下一个key,默认从第一个开始选择，当key的压缩限额为0后，选择下一个key再去执行
    old_key = tinify.key
    # print("current key = {}".format(old_key))

    # 没有设置过key时，取第一个
    # 如果不是数组，那么直接取值用，是数组那么这个不可用时可以切换下一个
    if old_key is None:
        api_key = keys[0]
    else:
        # 取下一个key
        index = keys.index(old_key)
        if 0 <= index < len(keys) - 1:
            api_key = keys[index + 1]
        else:
            api_key = old_key

    # print("api_key = ", api_key)
    if old_key == api_key or len(api_key) == 0:
        return -1

    tinify.key = api_key
    # 校验一下key是否能用 只要有网都会效其它错误在压缩时也会报，免得走一次网络接口
    # try:
    #     tinify.key = api_key
    #     tinify.validate()
    # except Exception as e:
    #     # 出错有很多情况，这里就不做区分了
    #     # print("出错了，e ={0}, message = {1}".format(type(e), e.message))
    #     # 继续查找下一个key
    #     if keys_is_list:
    #         choose_tinify_key(keys)
    #     else:
    #         print("tinypng不可用，检查网络或API Key是否可用~")
    #         return -1
    return 1


def do_compress(keys, source_path, target_path):
    # 执行tinypng的压缩
    try:
        source = tinify.from_file(source_path)
        source.to_file(target_path)
    except Exception as e:
        # 如果是帐号错误就换key,换key后继续执行当前操作,给下换key的机会
        if type(e) is tinify.errors.AccountError:
            print("当前key={0}出错，尝试切换key再压缩 message = {1}".format(tinify.key, e.message))
            if choose_tinify_key(keys) > 0:
                print("切换后的key={0} 继续压缩~~~~~".format(tinify.key))
                do_compress(keys, source_path, target_path)
            else:
                print("所有帐号错误（API key无效或者当月已经无剩余压缩余额) message = ", e.message)
                exit_with_save_data()
        else:
            print("有其它错误！退出 message = ", e.message)
            exit_with_save_data()


def image_compress(*params):
    # ##默认传入路径指针
    # 1.遍历文件夹下所有图片
    # 2.输出当前目录所有的后缀数组，看是否有新的后缀可以压缩

    # 配置tinypng sdk 的key
    keys = params[0]
    if choose_tinify_key(keys) <= 0:
        print("请设置有效的API key")
        exit()
    # 文件路径与是否备份
    source_dir = params[1]
    need_backup = params[2]

    if not os.path.exists(source_dir):
        print("{0}文件不存在，不需要做压缩任务，退出操作~~~~".format(source_dir.encode("utf-8")))
        exit()

    # === 1.根据传入的参数生成要使用的相关参数 ===
    # 把源文件夹里所有文件copy的备份文件夹下,所有的操作都是在备份文件夹做
    backup_source_path = resource_file_operation.backup_source_path(source_dir)
    # 通过源目标文件生成目标文件夹名
    target_dir = resource_file_operation.compress_target_path(source_dir)

    # ==== 2.把原图片文件夹copy到backup路径下 ===========
    resource_file_operation.copy_dir(source_dir, backup_source_path)

    # ==== 3.针对backup下的图片进行遍历，找出要压缩图片的路径，已经copy非图片的文件 ===========
    # 获取所有要压缩的图片路径
    source_paths, target_paths = get_all_paths(backup_source_path, target_dir)

    # 计数，当前已经压缩的图片张数
    count = 0

    #注册中断事件回掉
    register_interrupt()

    # 压缩所有待压缩的图片
    for s_path in source_paths:
        target_file_path = target_paths[count]
        print("准备压缩{0}，目标地址{1}".format(s_path.encode("utf-8"), target_file_path.encode("utf-8")))
        # 判断是否已经出错（计数有个缺陷就是1个月内500张计数就有问题，只有压缩时间在不同月份的才没问题）
        do_compress(keys, s_path, target_file_path)
        count += 1
        # 加到全局变量中，方便中断处理, 正常执行完compressed_path与target_paths是一样的
        compressed_path.append(target_file_path)
        print("一共:" + str(len(target_paths)) + "张图片; 已完成:" + str(count) + "张图片~")

    #压缩完成后保存一下缓存的路径
    save_caches(target_paths)

    # 把压缩后的文件目录以原名称copy到原目录
    print("还原压缩后的文件到原来路径下~~~~~~")
    resource_file_operation.copy_dir(target_dir, source_dir)
    # 如果不需要备份，那么删除整个备份文件夹下
    if not need_backup:
        print("不需要备份文件，删除文件~~~~~~")
        resource_file_operation.remove_dir(resource_file_operation.backup_dir_path())
    print("压缩任务执行完毕，请记得上传git~~~~~~")


def save_caches(cache_paths):
    #存储已经压缩的文件路径
    if len(cache_paths) > 0:
        print("把当前压缩图片的路径写入缓存文件~~~~~~")
        resource_file_operation.to_file(cache_paths)


def exit_with_save_data(code=0):
    # 非任务完成的退出时，都先保存一下缓存目录
    save_caches(compressed_path)
    exit(code)


def register_interrupt():
    # 添加几个主动退出任务的监听，用户主动退出任务时，也能记录下缓存
    # kill
    signal.signal(signal.SIGTERM, interrupt_handler)
    # ctrl + c
    signal.signal(signal.SIGINT, interrupt_handler)
    # ctrl + z
    signal.signal(signal.SIGTSTP, interrupt_handler)
    # ctrl + \
    signal.signal(signal.SIGQUIT, interrupt_handler)


def interrupt_handler(single_type, b):
    print("stopped by single {0}, b = {1} ".format(single_type, b))
    # 保存文件
    exit_with_save_data(single_type)


if __name__ == '__main__':
    result = parse_params()
    # print("result = {0}".format(result))
    image_compress(*result)
