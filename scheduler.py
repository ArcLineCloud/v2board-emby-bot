import os
import json
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from v2board_api import V2BoardAPI
from emby_api import EmbyAPI
from telegram.ext import ContextTypes

# 配置日志
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# 加载环境变量
load_dotenv()

async def check_and_clean_invalid_emby_accounts(context: ContextTypes.DEFAULT_TYPE | None = None):
    """检查所有用户的订阅等级并清理不符合要求的Emby账号"""
    user_data_dir = Path("user_data")
    allowed_plan_ids = [int(x.strip()) for x in os.getenv(
        'ALLOWED_PLAN_IDS', '').split(',') if x.strip()]
    emby = EmbyAPI()

    # 遍历用户数据目录
    for file_path in user_data_dir.glob("*.json"):
        try:
            # 读取用户数据
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            user_id = file_path.stem
            user_email = user_data.get('email', 'unknown')
            user_identifier = f"{user_email}(tg:{user_id})"

            # 如果用户没有Emby账号，跳过检查
            if not user_data.get('emby'):
                continue

            # 如果没有登录信息，跳过检查
            if not user_data.get('email') or not user_data.get('password'):
                continue

            # 创建API实例并尝试登录
            api = V2BoardAPI()
            api.email = user_data['email']
            api.password = user_data['password']

            # 如果有auth_data，先尝试使用它
            if user_data.get('auth_data'):
                api.auth_data = user_data['auth_data']
                api.headers['Authorization'] = user_data['auth_data']

            # 获取用户信息
            user_info = api.get_user_info()

            # 如果获取失败，尝试重新登录
            if not user_info or 'data' not in user_info:
                if not api.login():
                    # 如果登录失败，删除用户的emby账号
                    emby_user_id = user_data['emby']['user_id']
                    result = emby.delete_user(emby_user_id)
                    if result["success"]:
                        user_data['emby'] = {}
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(user_data, f,
                                      ensure_ascii=False, indent=2)
                    # 向用户发送消息
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="登录失败，请使用 /login 命令重新登录"
                    )
                    logger.warning(
                        f"用户 {user_identifier} 登录失败，已删除Emby账号并向用户发送消息")
                    continue
                user_info = api.get_user_info()

            if user_info and 'data' in user_info:
                current_plan_id = user_info['data'].get('plan_id')
                expired_at = user_info['data'].get('expired_at')
                current_time = int(time.time())

                # 如果没有订阅、订阅等级不在允许列表中，或者订阅已过期
                if not current_plan_id or current_plan_id not in allowed_plan_ids or (expired_at and expired_at < current_time):
                    logger.info(f"用户 {user_identifier} 的订阅{'已过期' if expired_at and expired_at < current_time else '等级不满足要求'}，删除Emby账号")

                    # 删除Emby账号
                    emby_user_id = user_data['emby']['user_id']
                    result = emby.delete_user(emby_user_id)

                    if result["success"]:
                        # 从用户数据中删除Emby信息
                        del user_data['emby']
                        # 保存更新后的用户数据
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(user_data, f,
                                      ensure_ascii=False, indent=2)
                        logger.info(f"已删除用户 {user_identifier} 的Emby账号")
                    else:
                        logger.error(
                            f"删除用户 {user_identifier} 的Emby账号失败: {result.get('error')}")

        except Exception as e:
            logger.error(f"处理用户 {user_identifier} 时出错: {str(e)}")
            continue

    logger.info("完成订阅等级检查和Emby账号清理")

if __name__ == "__main__":
    # 测试代码
    import asyncio
    asyncio.run(check_and_clean_invalid_emby_accounts())
