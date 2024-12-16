-- Migrate the user badges into the new table
INSERT INTO "user_items" (
    user_id, server_id, serial_id, item_type, item_id1, item_id2, item_id3, count, item_data_json
)
SELECT
    ub.user_id,
    ub.server_id,
    ROW_NUMBER() OVER (ORDER BY ub.user_id, ub.server_id, ub.badge_id) AS serial_id,
    2 AS item_type,
    ub.badge_id AS item_id1,
    NULL aS item_id2,
    NULL AS item_id3,
    1 AS count,
    json_build_object(
        '$type', 'holobot.extensions.general.repositories.records.items.badge_item_storage_model.BadgeItemStorageModel',
        'count', 1,
        'badge_id', json_build_object(
            'server_id', ub.server_id,
            'badge_id', ub.badge_id
        ),
        'unlocked_at', ub.unlocked_at
    )::text AS item_data_json
FROM "user_badges" ub;

-- Migrate the user currencies (wallets) into the new table
INSERT INTO "user_items" (
    user_id, server_id, serial_id, item_type, item_id1, item_id2, item_id3, count, item_data_json
)
SELECT
    w.user_id,
    w.server_id,
    ROW_NUMBER() OVER (ORDER BY w.user_id, w.server_id, w.currency_id)
        + (SELECT COUNT(*) FROM "user_badges") AS serial_id,
    1 AS item_type,
    w.currency_id AS item_id1,
    NULL AS item_id2,
    NULL AS item_id3,
    w.amount AS count,
    json_build_object(
        '$type', 'holobot.extensions.general.repositories.records.items.currency_item_storage_model.CurrencyItemStorageModel',
        'count', w.amount,
        'currency_id', w.currency_id
    )::text AS item_data_json
FROM "wallets" w;

DROP TABLE user_badges;
DROP TABLE wallets;
