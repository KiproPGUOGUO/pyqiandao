# -*- coding:utf-8 -*-
"""
cron: 22 11 * * *
"""

import aiohttp
import asyncio
import json
import os

from kipro_qiandao_utils.notify import send
from kipro_qiandao_utils.util import get_data, disable_account

### 已有反馈参数fb0,fb1，待添加账户禁用模块和脚本禁用模块

# 初始化
app = '慢慢买'
if os.listdir(tomls_folder:='kipro_tomls'):
    tomls_data = get_data(tomls_folder=tomls_folder)  # 合并tomls_folder下所有文件 读取为 {'app':[conf1,conf2]}
    confs = tomls_data.get(app) # 获取当前app的confs [conf1,conf2]  conf格式{'cookie':'xxx','xxx':'xxxx'}
    if_conc = env_if_conc if (env_if_conc:=os.environ.get(f'{app}_CONC')) else tomls_data.get(f'{app}_CONC')

async def main(conf,app=app):
    '''
        个人初始化，两种反馈类型，fb0账户过期，fb1脚本失效
    '''
    fb0,fb1 = 0,0
    user = conf.get('_user')
    status = conf.get('_status')
    tongzhi_method = conf.get('_tongzhi_method')
    tongzhi_param = conf.get('_tongzhi_param')
    if status:
        # task
        msg,fb0,fb1 = await task(conf,fb0,fb1)
        # 禁用该账户该app
        if any((fb0,fb1)):
            disable_account(user,app)
        # 通知
        if tongzhi_method:
            if tongzhi_param:
                await send(tongzhi_method,tongzhi_param,app,msg)
        
##############################################主任务，需要修改的地方#######################################################        
async def task(conf,f0,f1):
    '''
        a complete mission
    '''
    login_options = {
        'url': 'https://apph5.manmanbuy.com/taolijin/login.aspx',
        'headers': {
            'Host':	'apph5.manmanbuy.com',
            'f-refer':	'wv_h5',
            'Accept':	'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':	'XMLHttpRequest',
            'Accept-Language':	'zh-cn',
            'Accept-Encoding':	'gzip, deflate, br',
            'Content-Type':	'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':	'https://apph5.manmanbuy.com',
            'User-Agent':	conf['user-agent'],
            'Referer':	'https://apph5.manmanbuy.com/renwu/index.aspx',
            'Connection':	'keep-alive',
            'Cookie':	conf['cookie']
        },
        'body': conf['login_body']
    }
    checkin_options = {
        'url': 'https://apph5.manmanbuy.com/renwu/index.aspx',
        'headers': {
            'Host':	'apph5.manmanbuy.com',
            'f-refer':	'wv_h5',
            'Accept':	'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':	'XMLHttpRequest',
            'Accept-Language':	'zh-cn',
            'Accept-Encoding':	'gzip, deflate, br',
            'Content-Type':	'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':	'https://apph5.manmanbuy.com',
            'User-Agent':	conf['user-agent'],
            'Referer':	'https://apph5.manmanbuy.com/renwu/index.aspx',
            'Connection':	'keep-alive',
            'Cookie': conf['cookie']
        },
        'body': conf['checkin_body']
    }
    content = []
    async with aiohttp.ClientSession() as session:
        login_msg,fb0,fb1 = await login(session,login_options)
        content.append(login_msg)
        if not any((fb0,fb1)):
            checkin_msg,fb0,fb1 = await checkin(session,checkin_options)
            content.append(checkin_msg)
    msg = content[-1]
    return msg,f0,f1

async def login(session,login_options):
    '''
        log in part
    '''
    fb0,fb1 = 0,0
    async with session.post(login_options['url'],headers=login_options['headers'],data=login_options['body']) as r:
        resp = await r.text()
    # "code"=1 is login
    # login message
    try:
        resp_dict = json.loads(resp)
        msg = 'login success!!!'
        if not resp_dict['code']==1:
            msg,fb0 = f'login failed: {resp}',1 
    except EOFError:
        msg,fb1 = f'Script out of date: {resp}',1
    return msg, fb0, fb1

async def checkin(session,checkin_options):
    '''
        check in part
    '''
    fb0,fb1 = 0,0
    async with session.post(checkin_options['url'],headers=checkin_options['headers'],data=checkin_options['body']) as r:
        resp = await r.text()
    try:
        resp_dict = json.loads(resp)
        msg = f"checkin success!!!，获得积分{resp_dict['data']['addJifen']}，当前积分{resp_dict['data']['jifen']}，已连续签到{resp_dict['data']['continueCheckinCount']}天"
        if not resp_dict['code']==1:
            msg,fb0 = f'checkin failed: {resp}',1
    except:
        msg,fb1 = f'Script out of date: {resp}',1
    return msg, fb0, fb1

#################################################################################################################         
async def normal_tasks(confs):
    '''
        when if_conc == false
    '''
    for item in confs:
        await main(item)
        
async def conc_tasks(confs):
    '''
        when if_conc == true
    '''
    for item in confs:
        await asyncio.create_task(main(item))
    
if __name__ == '__main__':
    if confs:
        loop = asyncio.get_event_loop()
        if if_conc:
            loop.run_until_complete(conc_tasks(confs))
        else:
            loop.run_until_complete(normal_tasks(confs))

