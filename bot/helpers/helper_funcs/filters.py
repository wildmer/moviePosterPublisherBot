from telegram.ext import MessageFilter
from telegram import Message

# from tg_bot import SUPPORT_USERS, SUDO_USERS
SUPPORT_USERS = [294655685]
SUDO_USERS = [294655685]

OWNER_ID = 294655685
AUTHORIZED_CHATS = [-1001236704652, 294655685]


class CustomFilters:
    class __OwnerFilter(MessageFilter):
        def filter(self, message: Message):
            return bool(message.from_user.id == OWNER_ID)

    owner_filter = __OwnerFilter()

    class __AuthorizedUserFilter(MessageFilter):
        def filter(self, message: Message):
            id = message.from_user.id
            return bool(id in AUTHORIZED_CHATS or id in SUDO_USERS or id == OWNER_ID)

    authorized_user = __AuthorizedUserFilter()

    class __AuthorizedChat(MessageFilter):
        def filter(self, message: Message):
            return bool(message.chat.id in AUTHORIZED_CHATS)

    authorized_chat = __AuthorizedChat()

    class __SudoUser(MessageFilter):
        def filter(self, message: Message):
            return bool(message.from_user.id in SUDO_USERS)

    sudo_user = __SudoUser()

    # class __MirrorOwner(MessageFilter):
    #     def filter(self, message: Message):
    #         user_id = message.from_user.id
    #         if user_id == OWNER_ID:
    #             return True
    #         args = str(message.text).split(" ")
    #         if len(args) > 1:
    #             # Cancelling by gid
    #             with download_dict_lock:
    #                 for message_id, status in download_dict.items():
    #                     if (
    #                         status.gid() == args[1]
    #                         and status.message.from_user.id == user_id
    #                     ):
    #                         return True
    #                 else:
    #                     return False
    #         elif not message.reply_to_message:
    #             return True
    #         # Cancelling by replying to original mirror message
    #         reply_user = message.reply_to_message.from_user.id
    #         return bool(reply_user == user_id)

    # mirror_owner_filter = __MirrorOwner()

    def _owner_query(user_id):
        return bool(user_id == OWNER_ID or user_id in SUDO_USERS)


# class CustomFilters(object):
#     class _Supporters(BaseFilter):
#         def filter(self, message: Message):
#             return bool(message.from_user and message.from_user.id in SUPPORT_USERS)

#     support_filter = _Supporters()

#     class _Sudoers(BaseFilter):
#         def filter(self, message: Message):
#             return bool(message.from_user and message.from_user.id in SUDO_USERS)

#     sudo_filter = _Sudoers()

#     class _MimeType(BaseFilter):
#         def __init__(self, mimetype):
#             self.mime_type = mimetype
#             self.name = "CustomFilters.mime_type({})".format(self.mime_type)

#         def filter(self, message: Message):
#             return bool(message.document and message.document.mime_type == self.mime_type)

#     mime_type = _MimeType

#     class _HasText(BaseFilter):
#         def filter(self, message: Message):
#             return bool(message.text or message.sticker or message.photo or message.document or message.video)

#     has_text = _HasText()
