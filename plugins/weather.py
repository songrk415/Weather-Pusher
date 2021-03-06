import nonebot, json, requests, re, html, cssselect
from nonebot.command.argfilter import extractors, validators
from datetime import datetime, timedelta, timezone
from lxml.html import fromstring


VERSION = '1.3.2'

@nonebot.on_command('天气', shell_like=True)
async def weather(session):
    """根据关键字返回可能的城市，并设置地区"""
    settings = await read_settings()
    if 'version' not in settings or settings['version'] != VERSION:
        await session.send('正在更新配置文件，请耐心等待\n\n（该情况仅会在更新插件后首次运行时出现）')
        settings = await update_version(settings)
        await session.send('配置文件更新完成')
    
    # 如果用户注册过，直接返回实时天气
    city_name = await member_in_list(settings, session.ctx['user_id'])
    if city_name:
        current_weather_data = await get_current_weather_data(settings['city_list'][city_name]['code'])
        await session.finish(await format_msg(current_weather_data, settings['city_list'][city_name], current=True))
    
    # 如果没有注册过，自动进入注册流程
    if session.is_first_run:
        await session.send('您还没有注册过推送地区，接下来将自动开始注册')
    key_word = session.get('key_word', prompt="您希望推送哪里的天气？（仅支持中文名）", arg_filters=[extractors.extract_text, str.strip, validators.not_empty('输入不能为空')])
    # 如果搜索的地区别人已经注册过了，直接添加至该列表
    if key_word in settings['city_list']:
        settings['city_list'][key_word]['members'].append([session.ctx['user_id'], 6])
        await update_settings(settings)
        await session.finish(f'“{key_word}”已经存在，已将您的推送地区设置为“{key_word}”\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】')
    
    search_results = await get_search_results(key_word)
    if search_results == []:
        session.finish('没有查到任何结果，请发送“天气”重新查询\n\n请确认您的输入为中文名，且仅为城市名，如：\n维多利亚(√)\n维多利亚哥伦比亚(×)\n维多利亚加拿大(×)')
    format_str = await format_results(search_results)
    if session.current_key != 'selection':
        await session.send(format_str)
    selection = session.get('selection', prompt="回复序号确认地区", arg_filters=[extractors.extract_text, str.strip, validators.not_empty('输入不能为空'), validators.match_regex(r'\d', message='序号必须为数字', fullmatch=True), int])
    code = search_results[selection]['code']
    city = search_results[selection]
    time_zone = await tz_calc(code)
    settings['city_list'][city['local']] = {'code': code, 'local': city['local'], 'admin': city['admin'], 'country': city['country'], 'time_zone': time_zone, 'members': [[session.ctx['user_id'], 6]]}
    await update_settings(settings)
    await session.send(f"已将您的天气推送地区设为：\n {format_str.splitlines()[selection]}\n天气会每天6点自动推送\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】")

@nonebot.on_command('更改地区', shell_like=True)
async def location(session):
    """更改推送地区"""
    settings = await read_settings()
    if 'version' not in settings or settings['version'] != VERSION:
        await session.send('正在更新配置文件，请耐心等待\n\n（该情况仅会在更新插件后首次运行时出现）')
        settings = await update_version(settings)
        await session.send('配置文件更新完成')

    for name, city in settings['city_list'].items():
        for member in city['members']:
            if session.ctx['user_id'] == member[0]:
                settings['city_list'][name]['members'].remove(member)
                await update_settings(settings)
                session.finish(f"已将您从“{name}”中移除，请发送【天气】重设地区")
    session.finish(f"您还没有注册过地区，请发送【天气】设置")

@nonebot.on_command('更改时间', shell_like=True)
async def push_time(session):
    """更改推送时间"""
    settings = await read_settings()
    if 'version' not in settings or settings['version'] != VERSION:
        await session.send('正在更新配置文件，请耐心等待\n\n（该情况仅会在更新插件后首次运行时出现）')
        settings = await update_version(settings)
        await session.send('配置文件更新完成')
    
    if session.is_first_run:
        for name, city in settings['city_list'].items():
            for member in city['members']:
                if session.ctx['user_id'] == member[0]:
                    session.state['name'] = name
                    session.state['index'] = city['members'].index(member)
                    session.get('time', prompt="您想在几点推送？（0~23）", arg_filters=[extractors.extract_text, str.strip, validators.not_empty('输入不能为空'), validators.match_regex(r'\d+', message='时间必须为0~23之间的数字', fullmatch=True), int])
        session.finish(f"您还没有注册过地区，请发送【天气】设置")
    settings['city_list'][session.state.get('name')]['members'][session.state.get('index')] = [session.ctx['user_id'], session.state.get('time')]
    await update_settings(settings)
    await session.send(f"已将您的推送时间设置为{session.state.get('time')}点")

async def member_in_list(settings, user_id):
    """检查QQ是否已经注册，并返回所在城市"""
    for city in settings['city_list']:
        for member in settings['city_list'][city]['members']:
            if member[0] == user_id:
                return city
    return False

async def get_search_results(city):
    """根据关键字，返回搜索结果"""
    url = 'https://m.weathercn.com/citysearchajax.do'
    r = requests.post(url, data={'q': city})
    results = json.loads(r.text)['listAccuCity']
    cities = []
    for city in results:
        new_city = {
            'code': city['key'], 
            'country': city['countryLocalizedName'], 
            'admin': city['administrativeAreaLocalizedName'], 
            'local': city['localizedName']
            }
        cities.append(new_city)
    return cities

async def format_results(results):
    """格式化打印搜索结果"""
    format_string = ''
    for i in range(len(results)):
        format_string += f"{i}. {results[i]['local']}（{results[i]['country']}，{results[i]['admin']}）\n"
    return format_string

# @nonebot.on_command('定时', shell_like=True)
# async def on_time(session):
@nonebot.scheduler.scheduled_job('cron', hour='*', minute=1)
async def _():
    """根据当地时区早上6点自动更新天气数据"""
    settings = await read_settings()
    for city in settings['city_list'].keys():
        settings['city_list'][city]['time_zone'] = await tz_calc(settings['city_list'][city]['code'])
        await update_settings(settings)
        for member in settings['city_list'][city]['members']:
            if await tz_check(settings['city_list'][city]['time_zone'], member[1]):
                weather_data = await get_weather_data(settings['city_list'][city]['code'])
                bot = nonebot.get_bot()
                weather_str = await format_msg(weather_data, settings['city_list'][city])
                await bot.send_private_msg(user_id=member[0], message=weather_str)

async def format_msg(w, city, current=False):
    """格式化打印天气数据处"""
    if current:
        current_time = await get_local_time(city['time_zone'])
        weather_str = f"{city['local']}（{city['country']}）\n{current_time}\n\n" \
            f"天气：{w['current_weather']}\n气温：{w['current_temp']}\n体感温度：{w['current_feel']}\n" \
                f"日出/日落：{w['sunrise']} / {w['sunset']}\n\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】"
    else:
        weather_str = f"{city['local']}（{city['country']}）\n{w['date']}\n\n" \
            f"白天：{w['day_weather']}\n气温：{w['day_temp']}\n体感温度：{w['day_feel']}\n" \
                f"夜晚：{w['night_weather']}\n气温：{w['night_temp']}\n体感温度：{w['night_feel']}\n" \
                    f"日出/日落：{w['sunrise']} / {w['sunset']}\n\n修改时间请发送【更改时间】\n修改地区请发送【更改地区】" 
    return weather_str

async def tz_calc(code):
    """由于华风天气网页太弱智，只能根据小时天气板块自行计算时区"""
    url = f'https://m.weathercn.com/hourly-weather-forecast.do?id={code}'
    r = requests.get(url)
    tree = fromstring(r.text)
    results = tree.cssselect('ul.scroller li')
    r_list = []
    for i in range(len(results)):
        r_list.append(results[i].text_content().split())
    # 从网页上抓取并推算当前小时
    if len(r_list[1]) == 3:
        local_day = int(r_list[1][0][:2])
        local_hour = int(r_list[1][1][:2]) - 2
    else:
        local_hour = int(r_list[1][0][:2]) - 2
        if local_hour < 0:
            local_hour = 24 + local_hour
        date_local = 8 - (local_hour+2)%8 + 1
        local_day = int(r_list[date_local][0][:2])
        if int(r_list[date_local][1][:2]) == 0 or local_hour == 23:
            local_day -= 1
    # 根据当前小时计算当前时区
    utc_time = datetime.utcnow()
    day_difference = local_day - utc_time.day
    if day_difference == -1 or day_difference >= 27:
        time_zone = local_hour -24 - utc_time.hour
    elif day_difference == 1 or day_difference <= -27:
        time_zone = 24 - utc_time.hour + local_hour
    else:
        time_zone = local_hour - utc_time.hour
    return time_zone

async def tz_check(time_zone, member_tz):
    """查看是否有时区到早上6点了"""
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    local_tz = utc_dt.astimezone(timezone(timedelta(hours=time_zone)))
    if local_tz.hour == member_tz:
        return True
    return False

async def get_local_time(time_zone):
    """获取当地时间"""
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    local_time = utc_dt.astimezone(timezone(timedelta(hours=time_zone)))
    return local_time.strftime('%m/%d %X')

async def read_settings():
    """读取用户注册信息"""
    try:
        with open('settings.json', encoding='utf8') as f:
            settings = json.loads(f.read())
    except FileNotFoundError:
        settings = {"city_list": {}, 'version': VERSION}
    return settings

async def get_weather_data(location):
    """爬取当天天气"""
    url = f'https://m.weathercn.com/daily-weather-forecast.do?day=1&id={location}'
    r = requests.get(url)
    tree = fromstring(r.text)
    date = tree.cssselect('section.date > div > ul > li')[0].text_content()
    weather = tree.cssselect('section.detail > section.weather > div.left > p')
    day_weather = weather[0].text_content()
    night_weather = weather[1].text_content()
    temp = tree.cssselect('ul.right li.top > p.left > strong')
    day_temp = temp[0].text_content()
    night_temp = temp[1].text_content()
    feel = tree.cssselect('ul.right li.top > p.right > strong')
    day_feel = feel[0].text_content()
    night_feel = feel[1].text_content()
    sunrise = tree.cssselect('section.cloud > p > strong')[0].text_content()
    sunset = tree.cssselect('section.cloud > p > strong')[1].text_content()

    weather_data = {
        'date': date,
        'day_weather': day_weather,
        'day_temp': day_temp,
        'day_feel': day_feel,
        'night_weather': night_weather,
        'night_temp': night_temp,
        'night_feel': night_feel,
        'sunrise': sunrise,
        'sunset': sunset
    }
    return weather_data

async def get_current_weather_data(code):
    """获取实时天气"""
    url = f'https://m.weathercn.com/current-weather.do?id={code}'
    r = requests.get(url)
    tree = fromstring(r.text)
    current_weather = tree.cssselect('a.head-right1 > p')[0].text_content().split()[0]
    current_temp = tree.cssselect('section.real_weather > section.weather > p ')[0].text_content()
    current_feel = tree.cssselect('ol.detail_01 li > p')[1].text_content()
    sun = tree.cssselect('section.sun_moon > p span')
    sunrise = sun[0].text_content()
    sunset = sun[1].text_content()

    current_weather_data = {
        'current_temp': current_temp,
        'current_feel': current_feel,
        'current_weather': current_weather,
        'sunrise': sunrise,
        'sunset': sunset
    }
    return current_weather_data

async def update_settings(settings):
    """更新注册信息"""
    with open('settings.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(settings, ensure_ascii=False, indent=4))

async def update_version(settings):
    """更新注册信息至最新版本"""
    new_settings = {'city_list': {}, 'version': VERSION}
    for name, city in settings['city_list'].items():
        new_settings['city_list'][name] = {}
        new_settings['city_list'][name]['code'] = city['code']
        new_settings['city_list'][name]['members'] = []
        for member in city['members']:
            if isinstance(member, list):
                new_settings['city_list'][name]['members'].append(member)
            else:
                new_settings['city_list'][name]['members'].append([member, 6])
        cities = await get_search_results(name)
        for city in cities:
            if city['code'] == new_settings['city_list'][name]['code']:
                new_settings['city_list'][name].update(city)
                break
        new_settings['city_list'][name]['time_zone'] = await tz_calc(new_settings['city_list'][name]['code'])
    await update_settings(new_settings)
    return new_settings