-- =========================================================
-- RESET: deletes ALL data stored by the bot (keeps the tables)
-- Supabase -> SQL Editor -> New query -> paste -> Run
-- WARNING: this cannot be undone.
-- =========================================================

truncate table
    giveaway_entries,
    giveaways,
    reaction_roles,
    custom_commands,
    custom_triggers,
    tickets,
    ticket_panels,
    warns,
    guild_config
restart identity cascade;

-- Make sure the column defaults are the new English ones
-- (only needed if the tables were created with the old schema)
alter table ticket_panels  alter column button_label set default 'Open Ticket';
alter table custom_commands alter column description set default 'Custom command';
