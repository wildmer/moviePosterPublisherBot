from ..helper.telegram_helper.bot_commands import BotCommands
from ..modules import *
from .telegram_manager import TgClient


def add_handlers():
    TgClient.app.add_handler(CommandHandler(BotCommands.StartCommand, start))
    TgClient.app.add_handler(CommandHandler(BotCommands.MovieCommand, post_movie))
    TgClient.app.add_handler(CommandHandler(BotCommands.ShowCommand, post_tv))
    TgClient.app.add_handler(CommandHandler(BotCommands.InfoCommand, post_info))
    TgClient.app.add_handler(CommandHandler(BotCommands.PingCommand, ping))
    TgClient.app.add_handler(CommandHandler(BotCommands.LogCommand, send_log))
    TgClient.app.add_handler(CommandHandler(BotCommands.ICommand, get_info_message))
    TgClient.app.add_handler(CommandHandler(BotCommands.SaveCommand, save_files))
    TgClient.app.add_handler(CommandHandler(BotCommands.ListCommand, show_list_files))
    TgClient.app.add_handler(CommandHandler(BotCommands.SendCommand, send_list_files))
    TgClient.app.add_handler(CommandHandler(BotCommands.CleanCommand, clean_list_files))
    TgClient.app.add_handler(CommandHandler(BotCommands.AddCloudCommand, add_cloud))
    # TgClient.app.add_handler(CommandHandler("add_origins", add_origins))
    TgClient.app.add_handler(CommandHandler(BotCommands.AddPathsCommand, add_paths))
    TgClient.app.add_handler(CommandHandler(BotCommands.EditCommand, edit_message_command))
    TgClient.app.add_handler(CommandHandler(BotCommands.AddCommand, add_cloud_links))

    # TgClient.app.add_handler(
    #     MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post)
    # )
    TgClient.app.add_handler(
        MessageHandler(
            filters.Chat(chat_id=Config.GROUP_ID),  # - 1001236704652),
            handle_discussion_message,
        )
    )

    movie_handler = MovieSearchHandler()
    TgClient.app.add_handler(CommandHandler(BotCommands.ChangeCommand, movie_handler.change))
    TgClient.app.add_handler(CommandHandler(BotCommands.SearchCommand, movie_handler.search_movie))
    TgClient.app.add_handler(CallbackQueryHandler(movie_handler.flip, pattern="^(nex|pre|clo)$"))
    TgClient.app.add_handler(CallbackQueryHandler(movie_handler.select, pattern="^sel$"))