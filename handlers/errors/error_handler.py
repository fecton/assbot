from loader import dp

@dp.errors_handler()
async def errors_handler(update, exception):
	from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
										CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
										MessageTextIsEmpty, RetryAfter,
										CantParseEntities, MessageCantBeDeleted, BadRequest)

	if isinstance(exception, CantDemoteChatCreator):
		print("Can't demote chat creator")
		return

	if isinstance(exception, MessageNotModified):
		print('Message is not modified')
		return
	if isinstance(exception, MessageCantBeDeleted):
		print('Message cant be deleted')
		return

	if isinstance(exception, MessageToDeleteNotFound):
		print('Message to delete not found')
		return

	if isinstance(exception, MessageTextIsEmpty):
		print('MessageTextIsEmpty')
		return

	if isinstance(exception, Unauthorized):
		print(f'Unauthorized: {exception}')
		return

	if isinstance(exception, InvalidQueryID):
		print(f'InvalidQueryID: {exception} \nUpdate: {update}')
		return

	if isinstance(exception, TelegramAPIError):
		print(f'TelegramAPIError: {exception} \nUpdate: {update}')
		return

	if isinstance(exception, RetryAfter):
		print(f'RetryAfter: {exception} \nUpdate: {update}')
		return

	if isinstance(exception, CantParseEntities):
		print(f'CantParseEntities: {exception} \nUpdate: {update}')
		return

	if isinstance(exception, BadRequest):
		print(f'CantParseEntities: {exception} \nUpdate: {update}')
		return
