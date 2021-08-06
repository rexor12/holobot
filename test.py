from discord.permissions import Permissions
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import has_permissions
from holobot.sdk.database.queries.constraints.logical_constraint_builder import and_expression, or_expression
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.constraints import column_expression, and_expression, or_expression
from holobot.sdk.database.queries.enums import Equality

query, params = Query.select().columns(
    "rule_id", "group_id", "command_id"
).from_table("command_rules").where().expression(
    and_expression(
        column_expression("server_id", Equality.EQUAL, "1234567890123"),
        or_expression(
            column_expression("channel_id", Equality.EQUAL, None),
            column_expression("channel_id", Equality.EQUAL, "999909123183")
        ),
        or_expression(
            and_expression(
                column_expression("command_group", Equality.EQUAL, None),
                column_expression("command", Equality.EQUAL, None)
            ),
            and_expression(
                column_expression("command_group", Equality.EQUAL, "reminder"),
                or_expression(
                    column_expression("command", Equality.EQUAL, None),
                    column_expression("command", Equality.EQUAL, "view")
                )
            )
        )
    )
).build()

print(query)
print(params)

print("admin in all:", has_permissions(Permissions.all(), Permission.ADMINISTRATOR))
print("admin & channels in all: ", has_permissions(Permissions.all(), Permission.ADMINISTRATOR | Permission.MANAGE_CHANNELS))
print("admin & channels in none: ", has_permissions(Permissions.none(), Permission.ADMINISTRATOR | Permission.MANAGE_CHANNELS))
print("admin & channels in roles: ", has_permissions(Permissions(Permissions.manage_roles.flag), Permission.ADMINISTRATOR | Permission.MANAGE_CHANNELS))
