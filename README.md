# SK天气推送插件

# 目录
- [插件简介](#插件简介)
- [环境要求](#环境要求)
- [配置教程](#配置教程)
  - [安装 Python](#安装-Python)
  - [下载插件源码](#下载插件源码)
  - [运行插件](#运行插件)
  - [安装 CoolQ HTTP API 插件](#安装-CoolQ-HTTP-API-插件)
  - [更新插件](#更新插件)
- [安装完成！](#安装完成！)
- [更新日志](#更新日志)
- [已知问题与更新计划](#已知问题与更新计划)

# 插件简介
这是一个基于 Python nonebot 开发的酷Q机器人插件。因为是基于 CQHTTP 4 接口，所以很遗憾无法打包成cpk文件，需要进行一些相对复杂的配置，因此**不建议不熟悉酷Q或电脑小白用户使用**。

# 环境要求
* Python 3.6.1+
* nonebot[scheduler]
* requests
* lxml
* cssselect
* 酷Q Air/Pro
* CoolQ HTTP API 插件 v4.7+
* ~~一颗肯折腾的心~~

# 配置教程

## 安装 Python
从 <a href="https://www.python.org/" target="_blank">Python 官网</a> 下载 Python 安装包并安装，**安装时注意勾选“Add to PATH”**，如果不知道如何勾选可以参考 [廖雪峰的 Python 教程](https://www.liaoxuefeng.com/wiki/1016959663602400/1016959856222624)

## 下载插件源码
酷Q的帖子底下和QQ群文件里都能下


也可以从 [Github 的 release页面](https://github.com/songrk415/Weather-Pusher/releases) 下载插件的最新源码压缩包（在“Assests”下的“Souce code(zip)”


下载完后找个地方解压

## 运行插件
1. 解压压缩包后，**打开插件的根目录文件夹**（能看到 `bot.py`、`requirements.txt` 等文件），按住 SHIFT 并对空白处单击右键，选择 “在此处打开 Powershell 窗口”
2. 在 Poweshell 里先输入 `pip install -r requirements.txt`
3. 然后再输入 `python bot.py`，如果看到类似以下的字段则代表运行成功。

>如果出现报错，请检查是否是在插件根目录运行的 Powershell

```
ujson module not found, using json
msgpack not installed, MsgPackSerializer unavailable
[2020-01-04 17:11:06,938 nonebot] INFO: Succeeded to import "plugins.weather"
[2020-01-04 17:11:06,940 nonebot] INFO: Running on 0.0.0.0:8080
Running on https://0.0.0.0:8080 (CTRL + C to quit)
[2020-01-04 17:11:06,944] ASGI Framework Lifespan error, continuing without Lifespan support
[2020-01-04 17:11:06,952 nonebot] INFO: Scheduler started
```

>之后每次启动插件，只需重复1,3两步即可

## 安装 CoolQ HTTP API 插件
这里直接引用 nonebot 文档原文：
>前往 [CoolQ HTTP API 插件官方文档](https://cqhttp.cc/docs/)，按照其教程的「使用方法」安装插件。安装后，请先使用默认配置运行，并查看 酷Q 日志窗口的输出，以确定插件的加载、配置的生成和读取、插件版本等符合预期。
>>注意  
请确保你安装的插件版本 >= 4.7，通常建议插件在大版本内尽量及时升级至最新版本。

如果不知道怎么设置配置文件，请直接复制以下设置至 "<user_id>.json" 文件（直接替换全部内容）：
```
{
    "host": "",
    "port": 5700,
    "use_http": true,
    "ws_host": "[::]",
    "ws_port": 6700,
    "use_ws": false,
    "ws_reverse_url": "",
    "ws_reverse_api_url": "ws://127.0.0.1:8080/ws/api/",
    "ws_reverse_event_url": "ws://127.0.0.1:8080/ws/event/",
    "ws_reverse_reconnect_interval": 3000,
    "ws_reverse_reconnect_on_code_1000": true,
    "use_ws_reverse": true,
    "post_url": "",
    "access_token": "",
    "secret": "",
    "post_message_format": "string",
    "serve_data_files": false,
    "update_source": "china",
    "update_channel": "stable",
    "auto_check_update": false,
    "auto_perform_update": false,
    "show_log_console": true,
    "log_level": "info"
}
```

## 更新插件
如果需要更新机器人至更高版本，只需将压缩包中 Plugins 目录下的内容覆盖至您正在使用的插件文件夹中同名目录下即可，如果出现错误可以尝试删除 settings.json 或 weather_data.json 重新尝试录入

# 安装完成！
如果不出意外，此时私聊机器人 “天气” 即可开始设置推送地区了。如果报错或未响应，请重新阅读步骤是否有遗漏。使用过程中遇到问题或者bug，欢迎QQ群反馈：153409375
>感谢使用本插件，支持作者不妨去原贴下面留条言或者点个感谢。您的支持就是我最大的动力

# 更新日志
- 2020.3.6（v1.3.1）
  - 新增【更改时间】功能
  - 新增【更改地区】功能
- 2020.1.26（v1.2.0）
  - 设置天气时，如果搜索结果为空会返回提示
  - 设置天气时，会检查序号是否为数字
  - 现在会自动更新配置文件至相同版本，不在需要删除重新录入城市
- 2020.1.23（v1.1.0）
  - 彻底重写所有api，修复国内无法使用的问题
  - 天气信息增加：日落日出，体感温度
  - 发送“天气”返回实时天气
- 2020.1.18（v1.0.0）
  - 去除爬取次数限制，直接从网页爬取数据，不再依赖api接口
- 2020.1.4（v0.1.1）
  - 重写说明手册

# 已知问题与更新计划
- 地区设定可以中途退出
- 限制用户查询频率
- 设置天气时，如果该关键字已经存在，询问是否重名并继续查询
- 可以修改已经设定的地区
- 自动检测新版本并提醒更新/自动更新
- 自定义推送时间
- 使用 C++/C# 重写应用，可以直接打包为cpk插件，不再需要配置环境（在学了在学了，但愿有生之年能写完……）
- ~~重写说明手册~~
- ~~搜索城市名返回结果为空没有任何提示~~
- ~~选择搜索结果时如果输入不为数字会直接退出，需添加提示~~
- ~~搜索城市处提示用户正确格式（只能中文城市，且不包括省份国家等）~~
- ~~已经设定天气的情况下，发送“天气”返回为实时天气~~
- ~~直接从网页端爬取数据，不在需要APIKey，不再有调用次数限制~~
