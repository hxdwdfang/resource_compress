# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author :dfwang
# email:249581930@qq.com

'''
运行环境请选择python3，主要碰到的以下几个问题
主要问题：
1. pyhthon2 执行file.write(str)时，如果str有汉字的话会报错，要把str endcode一下，
   但在python3上encode后write会报错，python3无法写直进制
2. shutil.copytree()在python2上一些隐藏文件可能会引发报错，但python3上不会
'''


import os
import shutil

# 默认的备份文件夹名称，做到只要指定源目录就能做压缩，默认输出目录就是在原目录最后文件夹前加after
backup_dir_name = "GYLImageCompressBackUp"
backup_cached_file_name = "compressedPaths.txt"


def copy_file(source_path, target_path):
    # 这个方法只能复制文件
    if len(source_path) == 0 or len(target_path) == 0:
        print("copyfile 失败了！source_path or target_path一个为空~")
        return
    shutil.copyfile(source_path, target_path)


def move_dir(old_path, new_path):
    # 移动文件夹到目标文件夹，这里是为了项目的，所以移动时先把目标的文件夹删除，以免自动做了合并
    if len(old_path) == 0 or len(new_path) == 0:
        print("移动的文件夹路径为空，请检查~")
        return

    remove_dir(new_path)
    shutil.move(old_path, new_path)


def copy_dir(old_path, new_path):
    # 复制文件夹到目标文件夹，这里是为了项目的，所以复制前先把目标的文件夹删除，调用的api如果存在那么api会报错
    if len(old_path) == 0 or len(new_path) == 0:
        print("复制的的文件夹路径为空，请检查~")
        return

    remove_dir(new_path)
    shutil.copytree(old_path, new_path)


def remove_dir(path):
    # 删除文件夹
    if os.path.exists(path):
        shutil.rmtree(path)


def to_file(data_list):
    # 写文件
    path = cached_file_path()
    if len(path) == 0:
        print("文件路径为空, 请检查一下文件路径")
        return
    with open(path, 'a+') as file_handler:
        for name in data_list:
            # python2 时写文件的时候可以编码一下，python3的时候就不能
            # file_handler.write(name.encode("utf-8"))
            file_handler.write(name)
            file_handler.write('\n')


def from_file():
    # 读取文件
    path = cached_file_path()
    if len(path) == 0:
        # print("要读取的文件路径为空")
        return []

    name_list = []
    if not os.path.exists(path):
        # print('没有历史缓存')
        return name_list

    contents = []
    with open(path, 'r') as file_handler:
        contents = file_handler.readlines()

    for msg in contents:
        msg = msg.strip('\n')
        name_list.append(msg)

    return name_list


def backup_dir_path():
    # os.getcwd()是获取当前目录
    # 创建备份文件夹目录 /Users/username/GYLImageCompressBackUp
    backup_dir = os.path.join(os.environ['HOME'], backup_dir_name)
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)
    return backup_dir


def cached_file_path():
    # 已经压缩过的文件路径缓存文件地址
    return os.path.join(backup_dir_path(), backup_cached_file_name)


def compress_target_path(source_path):
    # 获取压缩目标文件夹, 一般不会为空，为空在前面就过掉了
    if len(source_path) == 0:
        # print("source_path为空")
        return ""
    backup_dir = backup_dir_path()
    # 通过source_path生成target_path,就算是""，通过split也会得到一个2个空元素的数组，所以角标为1的肯定有值
    source_file_name = os.path.split(source_path)[1]
    target_file_name = "After{0}".format(source_file_name)
    return os.path.join(backup_dir, target_file_name)


def backup_source_path(source_path):
    # 获取压缩目标文件夹, 一般不会为空，为空在前面就过掉了
    if len(source_path) == 0:
        # print("source_path为空")
        return ""
    backup_dir = backup_dir_path()
    # 通过source_path生成backup_source_path,就算是""，通过split也会得到一个2个空元素的数组，所以角标为1的肯定有值
    source_file_name = os.path.split(source_path)[1]
    return os.path.join(backup_dir, source_file_name)


