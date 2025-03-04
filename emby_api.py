import os
import random
import string
from venv import logger
import requests
import re
from dotenv import load_dotenv


class EmbyAPI:
    def __init__(self):
        # 加载.env文件
        load_dotenv()

        # 获取配置
        self.base_url = os.getenv('EMBY_URL').rstrip('/')
        self.api_key = os.getenv('EMBY_API_KEY')

        # 设置请求头
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # API请求参数
        self.params = {
            'api_key': self.api_key
        }

    def generate_random_username(self, length=None):
        """生成5-8位随机用户名"""
        if length is None:
            length = random.randint(5, 8)
        letters = string.ascii_lowercase
        digits = string.digits
        # 确保至少包含一个字母
        username = random.choice(letters)
        # 剩余位数可以是字母或数字
        username += ''.join(random.choices(letters + digits, k=length-1))
        return username

    def generate_random_password(self, length=None):
        """生成8-10位随机密码"""
        if length is None:
            length = random.randint(8, 10)
        letters = string.ascii_letters
        digits = string.digits
        special = '!@#$%^&*'
        # 确保密码包含至少一个大写字母、一个小写字母、一个数字和一个特殊字符
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(digits),
            random.choice(special)
        ]
        # 剩余位数随机填充
        password.extend(random.choices(letters + digits + special, k=length-4))
        # 打乱密码顺序
        random.shuffle(password)
        return ''.join(password)

    def create_user(self, username: str, password=None):
        """创建Emby用户"""
        if password is None:
            password = self.generate_random_password()

        # 创建用户
        create_url = f"{self.base_url}/emby/Users/New"
        create_data = { "Name": username, "HasPassword": True }

        try:
            response = requests.post(
                create_url,
                headers=self.headers,
                params=self.params,
                json=create_data
            )

            if response.status_code == 200:
                # 从响应中提取用户ID
                user_id = response.json()['Id']

                # 设置用户密码
                pwd_url = f"{self.base_url}/emby/Users/{user_id}/Password"
                pwd_data = {
                    "Id": user_id,
                    "CurrentPw": "",
                    "NewPw": password,
                    "ResetPassword": False
                }
                requests.post(pwd_url, headers=self.headers,
                              params=self.params, json=pwd_data)
                
                # 设置用户权限
                self.set_user_policy(user_id)
                return {
                    "success": True,
                    "user_id": user_id,
                    "username": username,
                    "password": password
                }
            else:
                return {
                    "success": False,
                    "error": f"创建用户失败: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"创建用户时发生错误: {str(e)}"
            }
    
    def set_user_policy(self, user_id: str) -> dict:
        """设置用户权限"""
        policy_url = f"{self.base_url}/emby/Users/{user_id}/Policy"
        policy_data = {
            "IsAdministrator": False,                   # 是否为管理员
            "IsHidden": True,                           # 用户是否隐藏
            "IsHiddenRemotely": True,                   # 是否在远程访问时隐藏
            "IsHiddenFromUnusedDevices": True,          # 是否在未使用的设备上隐藏
            "IsDisabled": False,                        # 用户是否被禁用
            "AllowTagOrRating": False,                  # 是否允许标记或评级
            "IsTagBlockingModeInclusive": False,        # 是否以标签阻止模式进行阻止
            "EnableUserPreferenceAccess": True,         # 是否允许用户访问首选项
            "EnableRemoteControlOfOtherUsers": False,   # 是否允许远程控制其他用户
            "EnableSharedDeviceControl": True,          # 是否允许共享设备的控制
            "EnableRemoteAccess": True,                 # 是否允许远程访问
            "EnableLiveTvManagement": False,            # 是否允许管理 Live TV
            "EnableLiveTvAccess": False,                # 是否允许访问 Live TV
            "EnableMediaPlayback": True,                # 是否允许媒体播放
            "EnableAudioPlaybackTranscoding": False,    # 表示是否允许音频转码
            "EnableVideoPlaybackTranscoding": False,    # 表示是否允许视频转码
            "EnablePlaybackRemuxing": False,            # 是否允许媒体复用
            "EnableContentDeletion": False,             # 是否允许删除内容
            "EnableContentDownloading": False,          # 是否允许下载内容
            "EnableSubtitleDownloading": False,         # 是否允许下载字幕
            "EnableSubtitleManagement": False,          # 是否允许管理字幕
            "EnableSyncTranscoding": False,             # 是否允许同步转码
            "EnableMediaConversion": False,             # 是否允许媒体转换
            "EnablePublicSharing": False,               # 是否允许公开共享
            "EnableAllDevices": True,                   # 是否允许访问所有设备
            "EnableAllChannels": True,                  # 是否允许访问所有频道
            "EnableAllFolders": True,                   # 是否允许访问所有文件夹
            "DisablePremiumFeatures": False,            # 是否禁用高级功能
            "AllowCameraUpload": False,                 # 是否允许相机上传
            "IsTagBlockingModeInclusive": False,        # 是否以标签阻止模式进行阻止
            "SimultaneousStreamLimit": 2                # 同时流式传输的限制
        }
        response = requests.post(policy_url, headers=self.headers, params=self.params, json=policy_data)
        if response.status_code == 204:
            return {
                "success": True
            }
        elif response.status_code == 500 and "Object reference not set to an instance of an object." in response.text:
            logger.info(f"用户不存在或已删除: {user_id}")
            return {
                "success": False,
                "error": "用户不存在或已删除"
            }
        else:
            return {
                "success": False,
                "error": f"设置用户权限失败: {response.status_code}"
            }

    def delete_user(self, user_id: str) -> dict:
        """删除指定的Emby用户

        Args:
            user_id: 要删除的用户ID

        Returns:
            dict: 包含操作结果的字典
                success: 是否成功
                error: 如果失败，错误信息
        """
        try:
            url = f"{self.base_url}/emby/Users/{user_id}"
            response = requests.delete(
                url, params=self.params, headers=self.headers)
            if response.status_code == 204:
                logger.info(f"成功删除Emby用户: {user_id}")
                return {
                    "success": True
                }
            elif response.status_code == 404:
                logger.info(f"用户不存在或已删除: {user_id}")
                return {
                    "success": True
                }
            else:
                error_msg = f"删除用户失败，状态码: {response.status_code}"
                if response.text:
                    error_msg += f"，错误信息: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            error_msg = f"删除用户时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


def main():
    # 使用示例
    api = EmbyAPI()

    # 创建用户
    result = api.create_user()
    if result["success"]:
        print(f"用户创建成功！")
        print(f"用户名: {result['username']}")
        print(f"密码: {result['password']}")
        print(f"用户ID: {result['user_id']}")
    else:
        print(f"创建失败: {result['error']}")


if __name__ == "__main__":
    main()
