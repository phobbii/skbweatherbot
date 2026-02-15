"""Configuration module for the weather bot."""
import os

# API Keys
OWM_KEY = os.getenv('OWM_KEY')
TELEBOT_KEY = os.getenv('TELEBOT_KEY')

# Webhook token
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')

# Content types
CONTENT_TO_HANDLE = ['text', 'location']
CONTENT_TO_REJECT = [
    'message_id', 'message_thread_id', 'direct_messages_topic', 'from', 'sender_chat',
    'sender_boost_count', 'sender_business_bot', 'date', 'business_connection_id', 'chat',
    'forward_origin', 'is_topic_message', 'is_automatic_forward', 'reply_to_message', 'external_reply',
    'quote', 'reply_to_story', 'reply_to_checklist_task_id', 'via_bot', 'edit_date',
    'has_protected_content', 'is_from_offline', 'is_paid_post', 'media_group_id', 'author_signature',
    'paid_star_count', 'entities', 'link_preview_options', 'suggested_post_info', 'effect_id',
    'animation', 'audio', 'document', 'paid_media', 'photo', 'sticker', 'story', 'video', 'video_note',
    'voice', 'caption', 'caption_entities', 'show_caption_above_media', 'has_media_spoiler', 'checklist',
    'contact', 'dice', 'game', 'poll', 'venue', 'new_chat_members', 'left_chat_member', 'new_chat_title',
    'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
    'message_auto_delete_timer_changed', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message',
    'invoice', 'successful_payment', 'refunded_payment', 'users_shared', 'chat_shared', 'gift',
    'unique_gift', 'gift_upgrade_sent', 'connected_website', 'write_access_allowed', 'passport_data',
    'proximity_alert_triggered', 'boost_added', 'chat_background_set', 'checklist_tasks_done', 'checklist_tasks_added',
    'direct_message_price_changed', 'forum_topic_created', 'forum_topic_edited', 'forum_topic_closed',
    'forum_topic_reopened', 'general_forum_topic_hidden', 'general_forum_topic_unhidden', 'giveaway_created',
    'giveaway', 'giveaway_winners', 'giveaway_completed', 'paid_message_price_changed', 'suggested_post_approved',
    'suggested_post_approval_failed', 'suggested_post_declined', 'suggested_post_paid', 'suggested_post_refunded',
    'video_chat_scheduled', 'video_chat_started', 'video_chat_ended', 'video_chat_participants_invited',
    'web_app_data', 'reply_markup'
]

# Sticker collections
ERROR_STICKERS = [
    'CAADAgAD3gEAAvnkbAAB9tAurz2ipZUWBA',
    'CAADAgADpQEAAvnkbAAB3LCoSz9i3NQWBA',
    'CAADAgAD3AIAAvnkbAABZ4r6GvjutU4WBA',
    'CAADAgAD4AIAAvnkbAABano-tB5DgtYWBA',
    'CAADAgADYssAAmOLRgywPTPuHYqUWhYE',
    'CAADAgADLgADNIWFDDKv5aCIOvtVFgQ',
    'CAADAgADKAADNIWFDJH1ZYPnRgPgFgQ'
]

WRONG_CONTENT_STICKERS = [
    'CAADAgAD4QIAAvnkbAAB4uG83jqZC7oWBA',
    'CAADAgADdgIAAvnkbAABwOWRNMVkWAwWBA',
    'CAADAgADAQIAAvnkbAABgYkUR2jzKikWBA',
    'CAADAgAD2wEAAvnkbAABCX-hVktjtVAWBA',
    'CAADAgADwAEAAvnkbAABoDH6R5pwO0cWBA',
    'CAADAgADvwEAAvnkbAABHngR9XeKmpsWBA',
    'CAADAgADtAEAAvnkbAABLH9k4WvwzJgWBA',
    'CAADAgADOgIAAvnkbAABRlHfrrHgNBcWBA',
    'CAADAgADagEAAvnkbAABiDcDQFCEuXgWBA',
    'CAADAgADJAEAAvnkbAAB2fxXBcKZT08WBA',
    'CAADAgADNAEAAvnkbAABdiR2Dg6Dxc8WBA'
]

# Unicode symbols
DEGREE_SIGN = '\N{DEGREE SIGN}'

# Locale setting
LOCALE = 'ru'