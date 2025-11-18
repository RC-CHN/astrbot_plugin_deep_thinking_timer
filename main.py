from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)


@register("astrbot_plugin_deep_thinking_timer", "Roo", "深度思考计时器插件", "0.1.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        pass

    async def _set_user_nickname(
        self, event: AstrMessageEvent, user_id: str, nickname: str
    ):
        """辅助函数：设置群名片"""
        # This function is platform-specific (e.g., QQ/aiocqhttp)
        if not isinstance(event, AiocqhttpMessageEvent):
            logger.warning(
                f"Attempted to set nickname in a non-aiocqhttp context: {event.get_platform_name()}"
            )
            return False

        try:
            group_id = event.get_group_id()
            self_id = event.get_self_id()
            if not group_id:
                logger.warning("Attempted to set nickname outside of a group chat.")
                return False

            await event.bot.set_group_card(
                group_id=int(group_id),
                self_id=int(self_id),
                user_id=int(user_id),
                card=nickname,
            )
            logger.info(
                f"Successfully set nickname for user {user_id} in group {group_id} to '{nickname}'."
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to set nickname for user {user_id} in group {group_id}: {e}"
            )
            return False

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass
