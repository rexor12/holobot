from holobot.discord.sdk.models import Embed, EmbedFooter
from holobot.extensions.general.options import EconomicOptions
from holobot.extensions.general.sdk.quests.dtos import QuestRewardDescriptor
from holobot.extensions.general.sdk.quests.models import CurrencyQuestReward
from holobot.sdk.i18n import II18nProvider

def create_quest_reward_embed(
    i18n_provider: II18nProvider,
    rewards: QuestRewardDescriptor,
    options: EconomicOptions
) -> Embed:
    description = []
    if rewards.completion_text:
        description.extend((rewards.completion_text, "\n\n"))

    if rewards.granted_items or rewards.granted_xp or rewards.granted_sp:
        description.append(i18n_provider.get(
            "extensions.general.quests.received_rewards"
        ))
        description.append("\n")

        if rewards.granted_xp:
            description.append(i18n_provider.get(
                "extensions.general.quests.reward_experience_points",
                { "xp": rewards.granted_xp }
            ))
            description.append("\n")

        if rewards.granted_sp:
            description.append(i18n_provider.get(
                "extensions.general.quests.reward_skill_points",
                { "sp": rewards.granted_sp }
            ))
            description.append("\n")

        for item in rewards.granted_items:
            # TODO Non-currency items.
            if not isinstance(item, CurrencyQuestReward):
                continue

            description.append(i18n_provider.get(
                "extensions.general.quests.reward_currency",
                {
                    "amount": item.count,
                    "emoji_name": item.emoji_name,
                    "emoji_id": item.emoji_id
                }
            ))

    return Embed(
        title=i18n_provider.get(
            f"extensions.general.quests.quest_complete",
            {
                "name": rewards.title or str(rewards.quest_proto_id.code)
            }
        ),
        description="".join(description),
        thumbnail_url=options.QuestsEmbedThumbnailUrl,
        footer=EmbedFooter(
            text=rewards.note
        ) if rewards.note else None
    )
