import os
from pyrogram import Client, types
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.entities_utils.entities_parsing import parse_entities
from app.bots.workers_bots.pyrogram_scripts.utils.parsing_posts_utils.markup_utils.markup_parsing import parse_markup
from app.services.logs.logging import logger


def get_download_path(file_id: str, content_type: str, document_ending=None):
    try:
        if content_type == "photo":
            ending = "png"
        elif content_type == "video" or content_type == "video_note" or content_type == "animation":
            ending = "mp4"
        elif content_type == "document":
            ending = document_ending
        elif content_type == "audio" or content_type == "voice":
            ending = "mp3"
        else:
            ending = "webp"

        curr_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        path = os.path.join(curr_dir, f"media/{file_id}.{ending}")
        return path
    except Exception as e:
        logger.error("Возникла ошибка в download_file: %s", e)


async def post_parsing(message: types.Message):
    post_data = [None, None, None, None, None, None, None, None, None, None,
                 None, None, None, None, None, None, None]
    try:

        logger.info(f"Сбор поста {message.id}")

        if message.text:
            post_data[0] = message.text
            post_data[14] = "text"
        else:
            if message.caption:
                post_data[0] = message.caption

            if message.photo:
                post_data[1] = message.photo.file_id
                post_data[14] = "photo"
                await message.download(file_name=get_download_path(
                    file_id=message.photo.file_id,
                    content_type=post_data[14]
                ))
            elif message.video:
                post_data[2] = message.video.file_id
                post_data[14] = "video"
                await message.download(file_name=get_download_path(
                    file_id=message.video.file_id,
                    content_type=post_data[14]
                ))
            elif message.audio:
                post_data[3] = message.audio.file_id
                post_data[14] = "audio"
                await message.download(file_name=get_download_path(
                    file_id=message.audio.file_id,
                    content_type=post_data[14]
                ))
            elif message.document:
                post_data[4] = message.document.file_id
                post_data[14] = "document"
                await message.download(file_name=get_download_path(
                    file_id=message.document.file_id,
                    content_type=post_data[14],
                    document_ending=message.document.mime_type
                ))
            elif message.video_note:
                post_data[5] = message.video_note.file_id
                post_data[14] = "video_note"
                await message.download(file_name=get_download_path(
                    file_id=message.video_note.file_id,
                    content_type=post_data[14]
                ))
            elif message.voice:
                post_data[6] = message.voice.file_id
                post_data[14] = "voice"
                await message.download(file_name=get_download_path(
                    file_id=message.voice.file_id,
                    content_type=post_data[14]
                ))
            elif message.sticker:
                post_data[7] = message.sticker.file_id
                post_data[14] = "sticker"
                await message.download(file_name=get_download_path(
                    file_id=message.sticker.file_id,
                    content_type=post_data[14]
                ))
            elif message.location:
                post_data[8] = f"latitude: {message.location.latitude}, longitude: {message.location.longitude}"
                post_data[14] = "location"
            elif message.contact:
                post_data[9] = f"phone: {message.contact.phone_number}, first_name: {message.contact.first_name}"
                post_data[14] = "contact"
            elif message.poll:
                answers = []
                for ans in message.poll.options:
                    answers.append(ans.text)

                post_data[10] = (f"question: {message.poll.question}, answers: {answers}, "
                                 f"anonymous: {message.poll.is_anonymous}, type: {message.poll.type}, "
                                 f"multiply_answers: {message.poll.allows_multiple_answers}, "
                                 f"correct_option_id: {message.poll.correct_option_id}, "
                                 f"explanation: {message.poll.explanation}, "
                                 f"open_period: {message.poll.open_period}")
                post_data[14] = "poll"
            elif message.animation:
                post_data[11] = message.animation.file_id
                post_data[14] = "animation"
                await message.download(file_name=get_download_path(
                    file_id=message.animation.file_id,
                    content_type=post_data[14]
                ))
            else:
                logger.warning("Unknowing message object: %s", message.link)
                return
        if message.reply_markup:
            if message.reply_markup.inline_keyboard:
                post_data[12] = parse_markup(message.reply_markup)

        logger.critical(message.entities)
        if message.entities:
            post_data[13] = parse_entities(entities=message.entities)

        post_data[15] = message.media_group_id
        post_data[16] = message.id
    except Exception as e:
        logger.error("Возникла ошибка в collect_post: %s", e)
    finally:
        return post_data
