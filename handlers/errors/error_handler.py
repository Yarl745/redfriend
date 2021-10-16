import logging
from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                      CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter,
                                      CantParseEntities, MessageCantBeDeleted)


from loader import dp
from utils import send


@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging
    """

    if isinstance(exception, CantDemoteChatCreator):
        await send.exception(update, exception)
        logging.exception("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        await send.exception(update, exception)
        logging.exception('Message is not modified')
        return True

    if isinstance(exception, MessageCantBeDeleted):
        await send.exception(update, exception)
        logging.exception('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        await send.exception(update, exception)
        logging.exception('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        await send.exception(update, exception)
        logging.exception('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        await send.exception(update, exception)
        logging.exception(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        await send.exception(update, exception)
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        await send.exception(update, exception)
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, RetryAfter):
        await send.exception(update, exception)
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, CantParseEntities):
        await send.exception(update, exception)
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, Exception):
        await send.exception(update, exception)
        logging.exception(f'Update: {update} \n{exception}')
        return True