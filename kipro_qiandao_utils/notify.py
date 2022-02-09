
import aiohttp
import asyncio
import json
import re

async def send(tongzhi_method,tongzhi_param,title,msg):
    await eval(f'{tongzhi_method}("{tongzhi_param}","{title}","{msg}")')
    
async def bark(BARK, title, content):
    if BARK.startswith('http'):
      url = f"""{BARK}/{title}/{content}"""
    else:
      url = f"""https://api.day.app/{BARK}/{title}/{content}"""
    async with aiohttp.request('GET',url) as resp:
        response = await resp.json()
    if response['code'] == 200:
        print('推送成功！')
    else:
        print('推送失败！')

async def qywx(QYWX_AM, title, content):
    """
    通过 企业微信 APP 推送消息。
    """
    QYWX_AM_AY = re.split(',', QYWX_AM)
    if 4 < len(QYWX_AM_AY) > 5:
        print("QYWX_AM_AY 设置错误!!\n取消推送")
        return
    print("企业微信 APP 服务启动")

    corpid = QYWX_AM_AY[0]
    corpsecret = QYWX_AM_AY[1]
    touser = QYWX_AM_AY[2]
    agentid = QYWX_AM_AY[3]
    try:
        media_id = QYWX_AM_AY[4]
    except IndexError:
        media_id = ""
    wx = await WeCom(corpid, corpsecret, agentid)
    # 如果没有配置 media_id 默认就以 text 方式发送
    if not media_id:
        message = title + "\n\n" + content
        datas = await wx.send_text(message, touser)
    else:
        datas = await wx.send_mpnews(title, content, media_id, touser)
    if datas == "ok":
        print("企业微信推送成功！")
    else:
        print(f"企业微信推送失败！错误信息：{datas}")
        
class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid        
    
    def __await__(self):
        # see: http://stackoverflow.com/a/33420721/1113207
        return self._async_init().__await__()
        
    async def _async_init(self):
        return self

    async def get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        async with aiohttp.request('POST',url=url,params=values) as resp:
            datas = json.loads(await resp.text())
        return datas.get("access_token")

    async def send_text(self, message, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + await self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        async with aiohttp.request('POST',url=send_url,data=send_msges) as resp:
            datas = await resp.json()
        return datas.get("errmsg")

    async def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + await self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        async with aiohttp.request('POST',url=send_url,data=send_msges) as resp:
            datas = await resp.json()
        return datas.get("errmsg")
