# mypy: disable-error-code="union-attr,index"
from collections.abc import Sequence
from enum import StrEnum, auto
from io import BytesIO
from pathlib import Path
from typing import cast

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

__all__ = ["ADD_ITEM_CONV"]

from .._utils.types import CONTEXT_TYPE
from ..constants import ItemDecision
from ..models import Item, ItemComment, ItemName


class States(StrEnum):
    ITEM_NAME = auto()
    ITEM_DESCRIPTION = auto()
    ITEM_PHOTOS = auto()
    ITEM_COMMENT = auto()
    ITEM_RECOMMENDATION = auto()


def build_item(context: CONTEXT_TYPE) -> Item:
    return Item(
        name=ItemName(slug=context.chat_data["name"]), description=context.chat_data["description"]
    )


def clear_chat_data(context: CONTEXT_TYPE) -> None:
    context.chat_data.clear()


def store_item(context: CONTEXT_TYPE) -> None:
    item = context.chat_data["item"]
    item.write_to_file()


async def entry_point(update: Update, context: CONTEXT_TYPE) -> States:
    clear_chat_data(context)
    await update.effective_message.reply_text("What is the name of the item?")
    return States.ITEM_NAME


async def parse_item_name(update: Update, context: CONTEXT_TYPE) -> States:
    name = update.effective_message.text
    context.chat_data["name"] = name
    await update.message.reply_text("What is the description of the item?")
    return States.ITEM_DESCRIPTION


async def parse_item_description(update: Update, context: CONTEXT_TYPE) -> States:
    description = update.effective_message.text
    context.chat_data["description"] = description
    await update.message.reply_text("Please send photos of the item.")

    item = build_item(context)
    context.chat_data["item"] = item

    return States.ITEM_PHOTOS


async def parse_item_photos(update: Update, context: CONTEXT_TYPE) -> States:
    attachment = (
        at[-1] if isinstance(at := update.effective_message.effective_attachment, Sequence) else at
    )

    photo_file = await attachment.get_file()

    data = BytesIO()
    await photo_file.download_to_memory(data)
    data.seek(0)

    item = context.chat_data["item"]
    item.add_photo(
        file_name=Path(photo_file.file_path).name,  # type: ignore[arg-type]
        file_content=data.read(),
    )

    await update.message.reply_text("Send additional photos or /done when you're done.")
    return States.ITEM_PHOTOS


async def switch_to_comments(update: Update, _: CONTEXT_TYPE) -> States:
    await update.message.reply_text(
        "Please send your comment for the item. Send /skip to skip the comment."
    )
    return States.ITEM_COMMENT


async def send_recommendation_keyboard(update: Update) -> States:
    await update.effective_message.reply_text(
        "What do you recommend to do with this item?",
        reply_markup=InlineKeyboardMarkup.from_row(
            [
                InlineKeyboardButton("💾", callback_data=ItemDecision.KEEP_ITEM.name),
                InlineKeyboardButton("🗑", callback_data=ItemDecision.DISCARD_ITEM.name),
                InlineKeyboardButton("🎁", callback_data=ItemDecision.GIVE_AWAY.name),
                InlineKeyboardButton("❓", callback_data=ItemDecision.UNDECIDED.name),
            ]
        ),
    )
    return States.ITEM_RECOMMENDATION


async def parse_item_comments(update: Update, context: CONTEXT_TYPE) -> States:
    comment = cast(str, cast(Message, update.effective_message).text)
    context.chat_data["comment"] = ItemComment(
        author=context.bot_data.default_author, content=comment
    )
    return await send_recommendation_keyboard(update)


async def skip_comment(update: Update, context: CONTEXT_TYPE) -> States:
    context.chat_data["comment"] = ItemComment(author=context.bot_data.default_author)
    return await send_recommendation_keyboard(update)


async def parse_recommendation(update: Update, context: CONTEXT_TYPE) -> States:
    recommendation = ItemDecision[cast(str, update.callback_query.data)]
    comment = context.chat_data["comment"]
    comment.set_recommendation(recommendation)

    item = context.chat_data["item"]
    item.add_comment(comment)

    store_item(context)
    clear_chat_data(context)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Item added successfully! Let's start over. Send /done to finish."
    )
    return await entry_point(update, context)


async def exit_conversation(update: Update, _: CONTEXT_TYPE) -> int:
    await update.message.reply_text("Conversation ended. Send /add_item to start over.")
    return ConversationHandler.END


ADD_ITEM_CONV = ConversationHandler(
    entry_points=[CommandHandler("add_item", entry_point)],
    states={
        States.ITEM_NAME: [
            CommandHandler("done", exit_conversation),
            MessageHandler(filters.TEXT, parse_item_name),
        ],
        States.ITEM_DESCRIPTION: [MessageHandler(filters.TEXT, parse_item_description)],
        States.ITEM_PHOTOS: [
            MessageHandler(filters.PHOTO | filters.Document.IMAGE, parse_item_photos),
            CommandHandler("done", switch_to_comments),
        ],
        States.ITEM_COMMENT: [
            CommandHandler("skip", skip_comment),
            MessageHandler(filters.TEXT, parse_item_comments),
        ],
        States.ITEM_RECOMMENDATION: [CallbackQueryHandler(parse_recommendation)],
    },
    fallbacks=[],
    per_user=False,
    per_chat=True,
)
