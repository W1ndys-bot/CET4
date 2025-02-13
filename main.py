# script/CET4/main.py

import logging
import os
import sys
import requests

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import *
from app.api import *
from app.switch import load_switch, save_switch


# 数据存储路径，实际开发时，请将CET4替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "CET4",
)


# 查看功能开关状态
def load_function_status(group_id):
    return load_switch(group_id, "CET4")


# 保存功能开关状态
def save_function_status(group_id, status):
    save_switch(group_id, "CET4", status)


# 处理元事件，用于启动时确保数据目录存在
async def handle_CET4_meta_event(websocket, msg):
    os.makedirs(DATA_DIR, exist_ok=True)


# 处理开关状态
async def toggle_function_status(websocket, group_id, message_id, authorized):
    if not authorized:
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]❌❌❌你没有权限对CET4功能进行操作,请联系管理员。",
        )
        return

    if load_function_status(group_id):
        save_function_status(group_id, False)
        await send_group_msg(
            websocket,
            group_id,
            f"[CQ:reply,id={message_id}]🚫🚫🚫CET4功能已关闭",
        )
    else:
        save_function_status(group_id, True)
        await send_group_msg(
            websocket, group_id, f"[CQ:reply,id={message_id}]✅✅✅CET4功能已开启"
        )


# 获取CET4单词
def get_cet4_word():
    url = "http://47.120.68.44:999/cihui"
    response = requests.get(url)
    # 去掉空行
    return response.text.replace("\n", "")


# 群消息处理函数
async def handle_CET4_group_message(websocket, msg):
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))
        authorized = user_id in owner_id

        # 是否是开启命令
        if raw_message == "cet4":
            await toggle_function_status(websocket, group_id, message_id, authorized)
            return

        # 检查是否开启
        if not load_function_status(group_id):
            return
        else:
            if raw_message == "四级单词":
                message = f"[CQ:reply,id={message_id}]" + get_cet4_word()
                await send_group_msg(websocket, group_id, message)

    except Exception as e:
        logging.error(f"处理CET4群消息失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理CET4群消息失败，错误信息：" + str(e),
        )
        return


# 群通知处理函数
async def handle_CET4_group_notice(websocket, msg):
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

    except Exception as e:
        logging.error(f"处理CET4群通知失败: {e}")
        await send_group_msg(
            websocket,
            group_id,
            "处理CET4群通知失败，错误信息：" + str(e),
        )
        return


# 回应事件处理函数
async def handle_CET4_response_message(websocket, message):
    try:
        msg = json.loads(message)

        if msg.get("status") == "ok":
            echo = msg.get("echo")

            if echo and echo.startswith("xxx"):
                pass
    except Exception as e:
        logging.error(f"处理CET4回应事件时发生错误: {e}")
