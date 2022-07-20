from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Option

import hikari

def transform_option_type(option_type: OptionType) -> hikari.OptionType:
    if option_type == OptionType.BOOLEAN:
        return hikari.OptionType.BOOLEAN
    if option_type == OptionType.INTEGER:
        return hikari.OptionType.INTEGER
    if option_type == OptionType.FLOAT:
        return hikari.OptionType.FLOAT
    return hikari.OptionType.STRING

def transform_option(option: Option) -> hikari.CommandOption:
    return hikari.CommandOption(
        type=transform_option_type(option.type),
        name=option.name,
        description=option.description,
        is_required=option.is_mandatory,
        choices=[
            hikari.CommandChoice(
                name=choice.name,
                value=choice.value
            )
            for choice in option.choices
        ]
    )