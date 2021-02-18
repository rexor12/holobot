from discord.user import User

class BotInterface:
    def get_user_by_id(self, user_id: int) -> User:
        raise NotImplementedError