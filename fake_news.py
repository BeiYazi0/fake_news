import hoshino
from hoshino import Service
from hoshino.typing import CQEvent

import re
import json
import os
import asyncio


_dir = os.path.dirname(__file__)
group_news_file = os.path.join(_dir,"group_news.json")

lmt = 5
ONE_TURN_TIME = 60
mark_dic = {}
with open(group_news_file, 'r', encoding='gbk') as f:
    group_news = json.loads(f.read())

sv = Service(
name="fake_news",  # 功能名
visible=True,  # 可见性
enable_on_default=True,  # 默认启用
bundle="娱乐",  # 分组归类
help_=f'''[伪造消息] +@xx+文字/图片/#标记xx
示例：
伪造消息
@张三 哈哈哈+图片1
@李四 嘿嘿嘿+图片2
@王五 #标记xx
[标记消息xx(数字，1-{lmt})] 使用必须回复某条消息，主要针对文字图片消息
[标记特殊消息xx(数字，1-{lmt})] 标记一些特殊消息，如小程序、视频、一起听
[测试标记消息xx(数字，1-{lmt})] 测试标记消息能否发送
[查看标记消息] 查看全部标记消息
[消息伪造帮助] 一些伪造示例''', 
)


def render_forward_msg(msg_list: list, uid_list: list, name_list: list):
    forward_msg = []
    for i, msg in enumerate(msg_list):
        forward_msg.append({
            "type": "node",
            "data": {
                "name": str(name_list[i]),
                "uin": str(uid_list[i]),
                "content": msg
            }
        })
    return forward_msg


def note_process(msg_list: list, uid: str):
    process_list = []
    pattern = "#标记([0-9]+)"
    for msg in msg_list:
        res = re.finditer(pattern, msg)
        for match in res:
            tag = match.group(1)
            if int(tag) > lmt or group_news.get(uid) == None or group_news[uid].get(tag) == None:
                continue
            new_msg = group_news[uid][tag]
            if type(new_msg) != str:
                msg = new_msg
                break
            else:
               msg = msg.replace(match.group(), group_news[uid][tag])
        process_list.append(msg)
    return process_list


@sv.on_prefix('伪造消息')
async def fake_create(bot, ev: CQEvent):
    msg = str(ev.message)
    groupid = ev.group_id
    uid = ev.user_id
    msg_list, uid_list, name_list = [], [], []
    pattern = "\[CQ:at,qq=([0-9]*)\] (.*(?!\[CQ:at,qq=([0-9]*)\]))"
    res = re.finditer(pattern, msg)
    for match in res:
        qq_id = match.group(1)
        uid_list.append(qq_id)
        member_info = await bot.get_group_member_info(group_id=groupid,user_id=qq_id)
        name_list.append(member_info["nickname"])
        msg_list.append(match.group(2).strip())

    if len(msg_list) == 0:
        return
    msg_list = note_process(msg_list, str(uid))
    forward_msg = render_forward_msg(msg_list, uid_list, name_list)
    try:
        await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)
    except:
        await bot.send(ev, "部分消息发送失败", at_sender = True)


@sv.on_prefix('测试标记消息')
async def fake_note(bot, ev: CQEvent):
    global lmt, group_news
    content = ev.message.extract_plain_text().replace("标记消息","").strip()
    if content == '' or not content.isdigit():
        await bot.send(ev, f"请输入测试标记消息xx(数字，1-{lmt})")
        return
    tag = int(content)
    if tag < 1 or tag > lmt:
        await bot.send(ev, f"请输入测试标记消息xx(数字，1-{lmt})")
        return

    uid = str(ev.user_id)
    if group_news.get(uid) == None or  group_news[uid].get(str(tag)) == None:
        await bot.send(ev, f"不存在标记消息{tag}", at_sender = True)
        return

    msg = group_news[uid][str(tag)]
    try:
        await bot.send(ev, msg)
    except:
        await bot.send(ev, f"标记消息{tag}发送失败", at_sender = True)


async def group_news_update():
    with open(group_news_file, 'w', encoding='gbk') as f:
        f.write(json.dumps(group_news, indent=4, ensure_ascii=False))


@sv.on_keyword('标记消息')
async def news_mark(bot, ev: CQEvent):
    if ev.message[0].type != "reply":
        await bot.send(ev, "请回复某条消息")
        return

    global lmt, group_news
    content = ev.message.extract_plain_text().replace("标记消息","").strip()
    if content == '' or not content.isdigit():
        await bot.send(ev, f"请输入标记特殊消息xx(数字，1-{lmt})")
        return
    tag = int(content)
    if tag < 1 or tag > lmt:
        await bot.send(ev, f"请输入标记特殊消息xx(数字，1-{lmt})")
        return

    try:
        tmsg = await bot.get_msg(message_id=int(ev.message[0].data['id']))
        msg = str(tmsg["message"])
    except:
        await bot.send(ev, "获取消息时出现错误")
        return

    uid = str(ev.user_id)
    if group_news.get(uid) == None:
        group_news[uid] = {}
    group_news[uid][str(tag)] = msg
    await group_news_update()
    await bot.send(ev, "标记消息成功", at_sender = True)


@sv.on_prefix('标记特殊消息')
async def sp_news_mark(bot, ev: CQEvent):
    uid = str(ev.user_id)

    global lmt, mark_dic, ONE_TURN_TIME

    old_tag = mark_dic.get(uid, False)
    if old_tag != False:
        await bot.send(ev, f"标记特殊消息冷却中，请稍等", at_sender = True)
        return

    content = ev.message.extract_plain_text().strip()
    if content == '' or not content.isdigit():
        await bot.send(ev, f"请输入标记特殊消息xx(数字，1-{lmt})")
        return
    tag = int(content)
    if tag < 1 or tag > lmt:
        await bot.send(ev, f"请输入标记特殊消息xx(数字，1-{lmt})")
        return

    mark_dic[uid] = content
    await bot.send(ev, f"开始标记特殊消息，请在{ONE_TURN_TIME}s内发送该消息")
    await asyncio.sleep(ONE_TURN_TIME)

    cur_tag = mark_dic[uid]
    if cur_tag != True:
        await bot.send(ev, "未检测到需要标记的消息", at_sender = True)
    mark_dic[uid] = False


@sv.on_message()
async def sp_news_get(bot, ev: CQEvent):
    uid = str(ev.user_id)

    global group_news, mark_dic

    tag = mark_dic.get(uid, False)
    if tag == False or tag == True:
        return

    if group_news.get(uid) == None:
        group_news[uid] = {}
    group_news[uid][tag] = ev.message
    await group_news_update()
    mark_dic[uid] = True
    await bot.send(ev, "标记消息成功", at_sender = True)


@sv.on_fullmatch('查看标记消息')
async def mark_news_get(bot, ev: CQEvent):
    gid = str(ev.group_id)
    uid = str(ev.user_id)
    news = group_news.get(uid)
    if news == None:
        await bot.send(ev, "尚无标记消息", at_sender = True)
        return

    msg_list = ["你的标记消息如下"]
    for tag, msg in news.items():
        msg_list.append(f"标记消息{tag}")
        msg_list.append(msg)

    uid_list, name_list = [2854196306]*len(msg_list), ["小冰"]*len(msg_list)
    forward_msg = render_forward_msg(msg_list, uid_list, name_list)
    try:
        await bot.send_group_forward_msg(group_id=gid, messages=forward_msg)
    except:
        await bot.send(ev, "部分标记消息发送失败", at_sender = True)


@sv.on_fullmatch("消息伪造帮助")
async def help_get(bot, ev: CQEvent):
    gid = str(ev.group_id)

    folder = os.path.join(_dir,"test")
    msg_list = [f"[CQ:image,file=file:///{os.path.join(folder, img)}]" for img in os.listdir(folder)]

    uid_list, name_list = [2854196306]*len(msg_list), ["小冰"]*len(msg_list)
    forward_msg = render_forward_msg(msg_list, uid_list, name_list)
    await bot.send_group_forward_msg(group_id=gid, messages=forward_msg)
