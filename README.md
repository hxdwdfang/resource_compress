图片压缩使用指南
===========
功能简介
-----
* 多key自动切换（tinify key）
* 压缩记录缓存，可避免重复压缩（手动删除缓存文件可全部再传tinify看是否要压缩）
* 主动、被动中断添加监听，也做好缓存工作
* 压缩完后主动替换原资源目录


准备工作
-----
* python环境 图片压缩使用python脚本进行压缩，所以运行电脑需要安装python3(脚本用的部份api在python2是有问题，所以要使用python3)
* tinypng sdk安装
	
	```
	执行下面语句安装tinidy sdk(加上sudo免得没有权限)
	sudo pip3 install --upgrade tinify
	
	```
* 申请tinypng api key(供应链项目我已经申请了4个key供使用，每个key有500张/每月的压缩限额，因测试使用过如果在使用过程中有报帐号达到limit后可以自行到**[tinypng官网](https://tinypng.com/developers)**申请key)
* 修改config.json文件配置api key（多个key请使用json list，单key可用字符串或者list）、待压缩资源目录


执行
-------
脚本默认读取config.json中的配置，也可以有配置执行时也可加参数，在配置与加参数同时存在时，相同项以命令参数为最后参数，缺省项以配置中参数为默认参数。有source\_path时 api\_key不可缺省！

```
切换到resource_compress.py目录或者给resource_compress.py的全路径
python3 resource_compress.py [api_key] [source_path]
```

其它
-------
tinypng其它功能可参照开发文档**[Developer API](https://tinypng.com/developers/reference/python)**
