import time
import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent


@register("astrbot_plugin_deep_thinking_timer", "RC-CHN", "深度思考计时器插件", "0.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.target_user_ids = config.get("target_user_ids", [])
        self.last_message_time = {}

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        logger.info(f"深度思考计时器已加载，目标用户: {self.target_user_ids}")

    @filter.event_message_type(filter.EventMessageType.ALL, priority=-1)
    async def on_message(self, event: AstrMessageEvent):
        logger.debug(f"收到消息: {event.get_message_outline()}, from: {event.get_sender_id()} in {event.get_group_id()}")

        if not event.get_group_id() or not isinstance(event, AiocqhttpMessageEvent):
            return

        sender_id = event.get_sender_id()
        if sender_id not in self.target_user_ids:
            return

        current_time = time.time()
        current_nickname = event.get_sender_name()

        # 解析原始昵称
        match = re.match(r"^(.*?)\s*\(已深度思考\d+秒\)$", current_nickname)
        if match:
            original_nickname = match.group(1)
        else:
            original_nickname = current_nickname

        if sender_id in self.last_message_time:
            elapsed_time = int(current_time - self.last_message_time[sender_id])
            if elapsed_time > 1: # 避免过于频繁的修改
                new_nickname = f"{original_nickname}   已深度思考 {elapsed_time} 秒"
                logger.info(f"用户 {sender_id} 深度思考了 {elapsed_time} 秒, 准备修改昵称为: {new_nickname}")
                await self._set_user_nickname(event, sender_id, new_nickname)

        self.last_message_time[sender_id] = current_time


    async def _set_user_nickname(self, event: AiocqhttpMessageEvent, user_id: str, nickname: str):
        """辅助函数：设置群名片"""
        try:
            group_id = event.get_group_id()
            self_id = event.get_self_id()

            await event.bot.set_group_card(
                group_id=int(group_id),
                self_id=int(self_id),
                user_id=int(user_id),
                card=nickname,
            )
            logger.info(f"成功为用户 {user_id} 在群 {group_id} 中设置昵称为 '{nickname}'.")
            return True
        except Exception as e:
            logger.error(f"为用户 {user_id} 在群 {group_id} 中设置昵称失败: {e}")
            return False

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass
