"""群成员缓存服务 - 用于@显示群昵称而非QQ号."""

from typing import Any

from mofish.api import actions


class MemberCacheService:
    """群成员缓存服务，提供QQ号到昵称的映射."""

    def __init__(self) -> None:
        # group_id -> {user_id -> member_info}
        self._cache: dict[int, dict[int, dict[str, Any]]] = {}

    async def ensure_cache(self, group_id: int) -> None:
        """确保指定群的成员缓存已加载."""
        if group_id in self._cache:
            return

        try:
            members = await actions.get_group_member_list(group_id)
            self._cache[group_id] = {
                m.get("user_id", 0): m for m in members
            }
        except Exception:
            self._cache[group_id] = {}

    def get_display_name(self, group_id: int, user_id: int | str) -> str | None:
        """获取群成员显示名称（群名片 > 昵称），未找到返回 None."""
        if group_id not in self._cache:
            return None

        uid = int(user_id) if isinstance(user_id, str) else user_id
        member = self._cache[group_id].get(uid)

        if not member:
            return None

        card = member.get("card", "")
        nickname = member.get("nickname", "")
        return card or nickname or None

    def get_members_list(self, group_id: int) -> list[dict[str, Any]]:
        """获取群成员列表（用于 mention_handler）."""
        if group_id not in self._cache:
            return []
        return list(self._cache[group_id].values())

    def clear_cache(self, group_id: int | None = None) -> None:
        """清除缓存，可指定群或清除全部."""
        if group_id is None:
            self._cache.clear()
        elif group_id in self._cache:
            del self._cache[group_id]


# 全局单例
member_cache = MemberCacheService()
