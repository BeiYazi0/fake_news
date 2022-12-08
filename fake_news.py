import hoshino
from hoshino import Service
from hoshino.typing import CQEvent


sv = Service(
    name="fake_news",  # 功能名
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_='''[伪造消息] +@xx+文字(+多张图片) （可以继续加）
示例：
伪造消息
@张三 哈哈哈+图片1
@李四 嘿嘿嘿+图片2''',  # 帮助说明

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


@sv.on_prefix('伪造消息')
async def fake_create(bot, ev: CQEvent):
	msg = ev.message
	groupid = ev.group_id
	msg_list, uid_list, name_list = [], [], []
	i=0
	if msg[i]["data"].get("qq") == None:
		return
	while i < len(msg):
		qq_id = msg[i]["data"].get("qq")
		uid_list.append(qq_id)
		cur_msg=''
		j = i+1
		while j < len(msg) and msg[j]["data"].get("qq") == None :
			cur_msg += str(msg[j])
			j +=1 
		i=j
		msg_list.append(cur_msg.strip())
		member_info = await bot.get_group_member_info(group_id=groupid,user_id=qq_id)
		name_list.append(member_info["nickname"])
	forward_msg = render_forward_msg(msg_list, uid_list, name_list)
	await bot.send_group_forward_msg(group_id=groupid, messages=forward_msg)
