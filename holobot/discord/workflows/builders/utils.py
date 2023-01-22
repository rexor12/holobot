import hikari

from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Option

def transform_option_type(option_type: OptionType) -> hikari.OptionType:
    match option_type:
        case OptionType.BOOLEAN: return hikari.OptionType.BOOLEAN
        case OptionType.INTEGER: return hikari.OptionType.INTEGER
        case OptionType.FLOAT: return hikari.OptionType.FLOAT
        case OptionType.USER: return hikari.OptionType.USER
        case _: return hikari.OptionType.STRING

def transform_option(option: Option) -> hikari.CommandOption:
    return hikari.CommandOption(
        type=transform_option_type(option.type),
        name=option.name,
        description=option.description,
        is_required=option.is_mandatory,
        autocomplete=option.is_autocomplete,
        choices=[
            hikari.CommandChoice(
                name=choice.name,
                value=choice.value
            )
            for choice in option.choices
        ] if not option.is_autocomplete
        else ()
    )
