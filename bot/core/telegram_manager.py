import asyncio

from telegram.ext import (  # ConversationHandler,; MessageHandler,;
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from bot import LOGGER

from ..core.config_manager import Config


class TgClient:
    app=None
    @classmethod
    def start_bot(cls):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        persistence = PicklePersistence(filepath="conversationbot")

        # Create the Application and pass it your bot's token.
        # application = (
        #     Application.builder()
        #     .token(Config["BOT"]["TOKEN"])
        #     .persistence(persistence)
        #     .build()
        # )
        cls.app = ApplicationBuilder().token(Config.BOT_TOKEN).persistence(persistence).build()

        from ..core.handlers import add_handlers

        add_handlers()

        # Start the Bot
        LOGGER.info("Bot Started!")
        asyncio.set_event_loop(asyncio.new_event_loop())
        cls.app.run_polling()