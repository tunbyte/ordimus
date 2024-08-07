import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
import firebase_admin
import requests
import spotipy
from bs4 import BeautifulSoup
from firebase_admin import credentials, firestore
from googleapiclient.discovery import build
from moviepy.video.io.VideoFileClip import VideoFileClip
import yt_dlp
from spotipy.oauth2 import SpotifyClientCredentials
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler


# cookie_string = """
# #HttpOnly_.youtube.com	TRUE	/	FALSE	0	SIDCC	AKEyXzW48C1QNzsyLHasmSc7FACjqVNucJNVSwAlwptv_iZqZSugrPMHVWYuSxV2MwRu_FBg3Ko
# #HttpOnly_.youtube.com	TRUE	/	FALSE	0	__Secure-1PSIDCC	AKEyXzW48C1QNzsyLHasmSc7FACjqVNucJNVSwAlwptv_iZqZSugrPMHVWYuSxV2MwRu_FBg3Ko
# ...
# """


client_credentials_manager = SpotifyClientCredentials(
    client_id='00b2191b89a74a709e3cdd6d0f45569d',
    client_secret='0552a4038898419c8930aa90dc58dd24'
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

api_key = "AIzaSyCfIyM5ZyB4hoKAzIRq8elN-_ZdXoCp5G8"
api = 'bf9d87652657d390350a04714a6a9136'

TOKEN = "7259514995:AAGHXOK_VtNhIRi0uIrKDumIfNjsFkGHWnY"
BOT_USERNAME = "@test_bot"

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

translations = {
    "en": {
        "greeting": "Hello {user}! 🎵 Welcome to OrdiMus, your personal music assistant.\n\n"
                    "I can help you download <b>YouTube video's audio</b>, download <b>music</b>, and more. <b>Here is How</b>:\n"
                    "<b>1. Type the name of a song to install it.</b>\n\n"
                    "<b>2. Send me a YouTube video link to download the audio.</b>\n\n"
                    "<b>3. Send an audio or a video message to recognize and download the music.</b>\n\n"
                    "<b>4. Send an Instagram post or reel link to download media.</b>\n\n"
                    "<b>5. Send a TikTok video link to download the video.</b>\n\n"
                    "<b>6. Send /language command in order to set language.</b>\n\n"
                    "Feel free to ask for assistance anytime! 😊\n",


        "help": "Need assistance? 🤔\n\n"
                "I can help you download <b>YouTube video's audio</b>, download <b>music</b>, and more. <b>How</b>:\n"
                "<b>1. Type the name of a song to install it.</b>\n\n"
                "<b>2. Send me a YouTube video link to download the audio.</b>\n\n"
                "<b>3. Send an audio or a video message to recognize and download the music.</b>\n\n"
                "<b>4. Send an Instagram post or reel link to download media.</b>\n\n"
                "<b>5. Send a TikTok video link to download the video.</b>\n\n"
                "Still need help? Contact @tunbyte for assistance.",

        "song": "Please choose a song:",
        "wait": "Processing, please wait...",
        "error": "An error occurred: {e}\nPlease send this error message to @tunbyte. ",
        "no_result": "No results found😖",
        "download": "Do you want to download {title} - {artist}?",
        "yes": "Download",
        "no": "Cancel",
        "Download_NO": "Download canceled",
        "suggestion": "Some suggestions I prepared using Artificial Intelligence :)",
        "donate": "Support us",
        "not_video": "An error occurred: We cannot download TikTok photos. Please provide a valid video URL.",
        "again": "Please try again later."
    },

    "tr": {
        "greeting": "Merhaba, {user}! 🎵 Kişisel asistanınız OrdiMus'a hoş geldiniz!\n\n"
                    "<b>YouTube video</b> sesini indirmenize, <b>müzik</b> indirmenize ve daha pek çok şeye yardımcı olabilirim. <b>Nasıl</b>:\n"
                    "1. <b>Yüklemek için istediğiniz şarkının adını yazın.</b>\n\n"
                    "2. <b>Videonun sesini indirmek için bana bir YouTube video bağlantısı gönderin.</b>\n\n"
                    "3. <b>Müziği tanıyıp indirmek için bir sesli mesaj veya video gönderin.</b>\n\n"
                    "4. <b>Instagram gönderisi veya reel bağlantısı gönderin, medyanı yükleyin.</b>\n\n"
                    "5. <b>TikTok video bağlantısı gönderin, videoyu indirin.</b>\n\n"
                    "6. <b>Dil ayarlamak için /language komutunu gönderin.</b>\n\n"
                    "İstediğiniz zaman yardım istemekten çekinmeyin!😊\n",


        "help": "Yardıma mı ihtiyacınız var? 🤔\n\n"
                "<b>YouTube video</b> sesini indirmenize, <b>müzik</b> indirmenize ve daha pek çok şeye yardımcı olabilirim. <b>Nasıl</b>:\n"
                "1. <b>Yüklemek için istediğiniz şarkının adını yazın.</b>\n\n"
                "2. <b>Videonun sesini indirmek için bana bir YouTube video bağlantısı gönderin.</b>\n\n"
                "3. <b>Müziği tanıyıp indirmek için bir sesli mesaj veya video gönderin.</b>\n\n"
                "4. <b>Instagram gönderisi veya reel bağlantısı gönderin, medyanı yükleyin.</b>\n\n"
                "5. <b>TikTok video bağlantısı gönderin, videoyu indirin.</b>\n\n"
                "Hala yardıma mı ihtiyacınız var? Yardım için @tunbyte ile iletişime geçin.",

        "song": "Lütfen bir şarkı seçin:",
        "wait": "İşleniyor... Lütfen bekleyin...",
        "error": "Bir hata oluştu: {e}\nLütfen bu hata mesajını @tunbyte'a gönderin.",
        "no_result": "Sonuç bulunamadı😖",
        "download": "{title} - {artist}'ı indirmek istiyor musunuz?",
        "yes": "İndir",
        "no": "Vazgeç",
        "Download_NO": "İndirmeden vazgeçildi.",
        "suggestion": "<b>Yapay Zeka</b> kullanarak hazırladığım bazı öneriler :)",
        "donate": "Bizi destekleyin",
        "not_video": "Bir hata oluştu: TikTok'taki fotoğrafları indirememekteyiz. Lütfen geçerli bir video URL'si gönderin.",
        "again": "Lütfen daha sonra tekrar deneyin"
    },

    "az": {
        "greeting": "Salam, {user}! 🎵 Şəxsi köməkçiniz OrdiMus-a xoş gəlmisiniz!\n\n"
                    "Sizə <b>YouTube videosunun</b> audiosunu yükləməyə, <b>musiqi</b> endirməyə və daha çoxuna kömək edə bilərəm. <b>Necə</b>:\n"
                    "1. <b>Yükləmək istədiyiniz mahnının adını yazın.</b>\n\n"
                    "2. <b>Videonun audiosunu endirmək üçün mənə YouTube video linkini göndərin.</b>\n\n"
                    "3. <b>Musiqini tanımaq və yükləmək üçün səsli mesaj və ya video göndərin.</b>\n\n"
                    "4. <b>Instagram postu və ya reel linki göndərin, medyanı yükləyin.</b>\n\n"
                    "5. <b>TikTok video linki göndərin, videonu yükləyin.</b>\n\n"
                    "6. <b>Dili ayarlamaq üçün /language əmrini göndərin.</b>\n\n"
                    "İstənilən vaxt kömək istəməkdən çəkinməyin!😊\n",


        "help": "Köməyə ehtiyacınız var? 🤔\n\n"
                "Sizə <b>YouTube videosunun</b> audiosunu yükləməyə, <b>musiqi</b> endirməyə və daha çoxuna kömək edə bilərəm. <b>Necə</b>:\n"
                "1. <b>Yükləmək istədiyiniz mahnının adını yazın.</b>\n\n"
                "2. <b>Videonun audiosunu endirmək üçün mənə YouTube video linkini göndərin.</b>\n\n"
                "3. <b>Musiqini tanımaq və yükləmək üçün səsli mesaj və ya video göndərin.</b>\n\n"
                "4. <b>Instagram postu və ya reel linki göndərin, mediyanı yükləyin.</b>\n\n"
                "5. <b>TikTok video linki göndərin, videonu yükləyin.</b>\n\n"
                "Hələ də köməyə ehtiyacınız var? Yardım üçün @tunbyte ilə əlaqə saxlayın.",

        "song": "Zəhmət olmasa mahnı seçin:",
        "wait": "Emal edilir... Zəhmət olmasa gözləyin...",
        "error": "Xəta baş verdi: {e}\nZəhmət olmasa, bu xəta mesajını @tunbyte ünvanına göndərin.",
        "no_result": "Nəticə tapılmadı😖",
        "download": "{title} - {artist} yükləmək istəyirsiniz?",
        "yes": "Yüklə",
        "no": "İmtina et",
        "Download_NO": "Yükləmə ləğv edildi.",
        "suggestion": "<b>Süni İntellekt</b>dən istifadə edərək hazırladığım bəzi təkliflər :)",
        "donate": "Bizi dəstəkləyin",
        "not_video": "Xəta baş verdi: TikTok fotoşəkillərini endirə bilmirik. Zəhmət olmasa keçərli video linki göndərin.",
        "again": "Zəhmət olmasa daha sonra yenidən cəhd edin."
    }
}


def get_youtube_video_id(api_key, video_title):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        q=video_title,
        part='snippet',
        type='video',
        maxResults=1
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        video_id = response['items'][0]['id']['videoId']
        return video_id
    else:
        return None


def get_translation(language_code, key):
    if language_code in translations:
        return translations[language_code].get(key, translations['en'][key])
    else:
        return translations['en'][key]


async def send_translated_message(update: Update, text_key: str):
    user = update.message.from_user.first_name
    user_id = update.message.from_user.id
    user_ref = db.collection('users').document(str(user_id))
    lang_doc = user_ref.get()
    language = lang_doc.get('language')
    translated_text = get_translation(language, text_key).format(user=user)
    await update.message.reply_html(translated_text)


def send_email(body):
    sender = 'tunar3950@gmail.com'
    psw = 'dcijbiwfmwtrmvnn'
    receiver = 'tunar.memmedov@icloud.com'
    subject = 'OrdiMUS BOT'

    em = EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender, psw)
        smtp.send_message(em)


def save_user_info(us_id: int, username: str, user: str, message: str, language: str, proplem=None, result=None) -> None:
    user_ref = db.collection('users').document(str(us_id))
    timestamp = datetime.now(timezone.utc)

    data = {
        'username': username,
        'user': user,
        'message': message,
        'language': language,
        'timestamp': timestamp,
    }

    if proplem:
        data['error'] = proplem
    if result:
        data['result'] = result

    user_ref.set(data)


def get_lang(us_id: int):
    user_ref = db.collection('users').document(str(us_id))
    lang_doc = user_ref.get()

    user_lang = lang_doc.get('language')

    return user_lang


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    username = update.message.from_user.username
    us_id = update.message.chat_id
    user_lang = update.message.from_user.language_code

    greeting = get_translation(user_lang, 'greeting').format(user=user)

    donation = get_translation(user_lang, 'donate')

    keyboard = [
        [InlineKeyboardButton(donation, url="https://buymeacoffee.com/tunbyte")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(greeting, reply_markup=reply_markup)

    save_user_info(us_id, username, user, 'start', user_lang)

    # send_email(f'User: {user}\nUsername: {username}\nID: {us_id} sent "/start"')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    username = update.message.from_user.username
    us_id = update.message.chat_id

    await send_translated_message(update, 'help')

    user_lang = get_lang(us_id)
    save_user_info(us_id, username, user, '/help', user_lang)
    await update.message.reply_text(user_lang)

    # send_email(f'User: {user}\nUsername: {username}\nID: {us_id} sent "/help"')


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    user = update.message.from_user.first_name
    us_id = update.message.chat_id

    user_language = get_lang(us_id)

    try:
        genres = sp.recommendation_genre_seeds()
        genre_seeds = genres['genres'][:5]

        recommendations = sp.recommendations(seed_genres=genre_seeds, limit=10)

        if recommendations and recommendations['tracks']:
            keyboard = []
            for track in recommendations['tracks']:
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                track_id = track['id']
                keyboard.append([InlineKeyboardButton(f"{track_name} - {artist_name}", callback_data=track_id)])

            reply_markup = InlineKeyboardMarkup(keyboard)
            suggestion_text = get_translation(user_language, 'suggestion')
            await update.message.reply_html(suggestion_text, reply_markup=reply_markup)
            save_user_info(us_id, username, user, '/recommend', user_language)

            send_email(f'User: {user}\nUsername: {username}ID:{us_id}\nCommand: /suggest\nAI: Success')
        else:
            await send_translated_message(update, 'no_result')
            save_user_info(us_id, username, user, '/recommend', user_language, 'no_result')

    except Exception as e:
        error_message = get_translation(user_language, 'error').format(e=e)
        await update.message.reply_text(error_message)

        save_user_info(us_id, username, user, '/recommend', user_language, str(e))
        send_email(f'User: {user}\nUsername: {username}ID:{us_id}\nCommand: /suggest\nAI_Error: {error_message}')


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = 'Please select a language.'
    keyboard = [
        [InlineKeyboardButton('English 🏴󠁧󠁢󠁥󠁮󠁧󠁿󠁧', callback_data='lang_en'),
         InlineKeyboardButton('Azerbaijani 🇦🇿', callback_data='lang_az')],
        [InlineKeyboardButton('Turkish 🇹🇷', callback_data='lang_tr')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    user = update.message.from_user.first_name
    us_id = update.message.chat_id
    song_name = update.message.text
    user_language = get_lang(us_id)

    save_user_info(us_id, username, user, song_name, user_language)

    try:
        if 'https://www.tiktok.com/' in song_name or 'https://vt.tiktok.com/' in song_name:
            await send_translated_message(update, 'wait')
            part = song_name.split('/')
            if part[4] == 'photo':
                await send_translated_message(update, 'not_video')
                return
            ydl_opts = {
                'outtmpl': 'tiktok.mp4',
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([song_name])
            except Exception as e:
                save_user_info(us_id, username, user, song_name, user_language, str(e))

                send_email(f'User: {user}\nUsername: {username}\nID: {us_id}\nMessage: {song_name}\nTiktok_Error: {str(e)}')
                await send_translated_message(update, 'not_video')
                return

            with open('tiktok.mp4', 'rb') as file:
                await update.message.reply_video(file, caption=BOT_USERNAME)
            os.remove('tiktok.mp4')

        elif 'https://www.instagram.com/' in song_name:
            await send_translated_message(update, 'wait')
            html_content = ''
            url = song_name.replace('www.', 'dd')
            base_url = "https://ddinstagram.com"

            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
            else:
                await update.message.reply_text(f"Failed to retrieve content. Status code: {response.status_code} - {response.text}")
                send_email(f'User: {user}\nUsername: {username}\nID: {us_id}Message: {song_name}\nInstagram_Error: Failed to retrieve content. Status code: {response.status_code} - {response.text}')
                save_user_info(us_id, username, user, song_name, user_language, f'Ins_Error:{response.status_code} - {response.text}')

            soup = BeautifulSoup(html_content, 'html.parser')

            video_tag = soup.find('meta', attrs={'property': 'og:video'})
            image_tag = soup.find('meta', attrs={'property': 'og:image'})
            full_media_url = ''
            media_type = ''
            if video_tag:
                media_url = video_tag['content']
                full_media_url = base_url + media_url if media_url.startswith('/') else media_url
                media_type = 'video'
            elif image_tag:
                media_url = image_tag['content']
                full_media_url = base_url + media_url if media_url.startswith('/') else media_url
                media_type = 'image'
            else:
                await update.message.reply_text("Please try again later.")

            media_response = requests.get(full_media_url)
            if media_response.status_code == 200:
                if media_type == 'video':
                    await update.message.reply_video(media_response.content, caption=BOT_USERNAME)
                elif media_type == 'image':
                    await update.message.reply_photo(media_response.content, caption=BOT_USERNAME)
            else:
                await update.message.reply_text(f"Failed to download {media_type}. Status code: {media_response.status_code}")
                send_email(f'User: {user}\nUsername: {username}\nID: {us_id}Message: {song_name}\nInstagram_Error: Failed to download {media_type}. Status code: {media_response.status_code}')
                save_user_info(us_id, username, user, song_name, user_language,
                               f'Instagram_Error: Failed to download {media_type}. Status code: {media_response.status_code}')

        elif "https://yout" in song_name or "https://www.yout" in song_name:
            try:
                await send_translated_message(update, 'wait')
                video_url = song_name

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

                await update.message.reply_chat_action(action=ChatAction.UPLOAD_VOICE)
                with open(mp3_file_path, "rb") as file:
                    await update.message.reply_audio(audio=file, caption=f"{BOT_USERNAME}",
                                                     duration=info_dict.get('duration'))
                os.remove(mp3_file_path)

            except Exception as e:
                save_user_info(us_id, username, user, song_name, user_language, f'YTB_Error:{str(e)}')
                error_message = get_translation(user_language, 'error').format(e=str(e))
                send_email(f'User: {user}\nUsername: {username}\nID: {us_id}\nMessage: {song_name}\nYTB_Error: {str(e)}')
                await update.message.reply_text(error_message)

        else:
            song_translation = get_translation(user_language, "song")

            results = sp.search(q=song_name, type='track', limit=10)
            if not results:
                await update.message.reply_text("No songs found.")
                return

            keyboard = []

            for item in results['tracks']['items']:
                track_name = item['name']
                track_id = item['id']
                artist_name = item['artists'][0]['name']
                keyboard.append([InlineKeyboardButton(f"{track_name} - {artist_name}", callback_data=track_id)])

            rep = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(song_translation, reply_markup=rep)

    except Exception as e:
        save_user_info(us_id, username, user, song_name, user_language, f'Handle_Message_Error: {str(e)}')
        error_message = get_translation(user_language, 'error').format(e=e)
        await update.message.reply_text(error_message)
        send_email(f'User:{user}\nID:{us_id}\nMessage: {song_name}\nHandle_Message_Error: {str(e)}')


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    username = update.message.from_user.username
    us_id = update.message.chat_id
    audio = update.message.voice

    user_language = get_lang(us_id)

    api = 'bf9d87652657d390350a04714a6a9136'

    file = await context.bot.get_file(audio.file_id)
    await file.download_to_drive('audio.mp3')

    try:
        data = {
            'api_token': api,
            'return': 'apple_music,spotify',
        }
        files = {
            'file': open('audio.mp3', 'rb'),
        }

        result = requests.post('https://api.audd.io/', data=data, files=files)
        data = result.json()

        if 'result' in data and data['result']:
            title = data['result'].get('title', 'Unknown title')
            artist = data['result'].get('artist', 'Unknown artist')
            combine = title + " - " + artist
            keyboard = [
                [
                    InlineKeyboardButton(get_translation(user_language, "yes"), callback_data=f'audio_yes_{combine}'),
                    InlineKeyboardButton(get_translation(user_language, "no"), callback_data='download_no')
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                get_translation(user_language, "download").format(title=title, artist=artist),
                reply_markup=reply_markup
            )
            save_user_info(us_id, username, user, file.file_path, user_language, result=combine)

        else:
            await send_translated_message(update, 'no_result')
            save_user_info(us_id, username, user, file.file_path, user_language, result='no_result_found')


    except Exception as e:
        save_user_info(us_id, username, user, file.file_path, user_language, str(e))
        error_message = get_translation(user_language, 'error').format(e=e)
        await update.message.reply_text(error_message)
        send_email(f'User:{user}\nID:{us_id}\nMessage: {file.file_path}\nHandle_Audio_Error: {str(e)}')


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    username = update.message.from_user.username
    us_id = update.message.chat_id
    video = update.message.video

    user_language = get_lang(us_id)


    video_file = await context.bot.get_file(video.file_id)
    video_path = 'video.mp4'
    await video_file.download_to_drive(video_path)

    audio_path = 'audio_from_video.mp3'
    with VideoFileClip(video_path) as video_clip:
        video_clip.audio.write_audiofile(audio_path)


    try:
        data = {
            'api_token': api,
            'return': 'apple_music,spotify, deezer, napster',
        }
        files = {
            'file': open(audio_path, 'rb'),
        }

        result = requests.post('https://api.audd.io/', data=data, files=files)
        data = result.json()

        if 'result' in data and data['result']:
            title = data['result'].get('title', 'Unknown title')
            artist = data['result'].get('artist', 'Unknown artist')
            combine = title
            keyboard = [
                [
                    InlineKeyboardButton(get_translation(user_language, "yes"), callback_data=f'audio_yes_{combine}'),
                    InlineKeyboardButton(get_translation(user_language, "no"), callback_data='download_no')
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                get_translation(user_language, "download").format(title=title, artist=artist),
                reply_markup=reply_markup
            )
            save_user_info(us_id, username, user, video_file.file_path, user_language, result=combine)

        else:
            await send_translated_message(update, 'no_result')
            save_user_info(us_id, username, user, video_file.file_path, user_language, result='no_result_found')

    except Exception as e:
        save_user_info(us_id, username, user, video_file.file_path, user_language,f'Handle_Video_Error: {str(e)}')
        error_message = get_translation(user_language, 'error').format(e=e)
        await update.message.reply_text(error_message)
        send_email(f'User:{user}\nID:{us_id}\nMessage: {video_file.file_path}\nHandle_Video_Error: {str(e)}')

    finally:
        os.remove(video_path)
        os.remove(audio_path)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_language = query.data.split('_')[1]
    user_id = query.message.chat_id

    await query.answer()

    user_ref = db.collection('users').document(str(user_id))

    user_ref.set({'language': user_language}, merge=True)

    if user_language == 'en':
        await query.edit_message_text("Language set to English.󠁧󠁢󠁥󠁮󠁧󠁧󠁢󠁥󠁮󠁧")
    elif user_language == 'tr':
        await query.edit_message_text("Dil Türkçe olarak ayarlandı.")
    elif user_language == 'az':
        await query.edit_message_text("Dil Azərbaycan dilidir.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.message.from_user.first_name
    chat_id = query.message.chat_id
    song_name = query.message.text

    user_language = get_lang(chat_id)

    await query.answer()

    try:
        if query.data.startswith("audio_yes_"):
            wait = get_translation(user_language, "wait")
            await query.edit_message_text(wait)
            music = query.data[10:]
            video_id = get_youtube_video_id(api_key, music)
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            if os.path.exists(mp3_file_path):
                await query.message.reply_chat_action(action=ChatAction.UPLOAD_VOICE)
                with open(mp3_file_path, "rb") as file:
                    await query.message.reply_audio(audio=file, caption=f"{BOT_USERNAME}", title=file.name[:-4], filename=file.name[:-4],
                                                    duration=info_dict.get('duration'))

                os.remove(mp3_file_path)
            else:
                await query.message.reply_text(
                    get_translation(user_language, 'error').format(e='File not found after conversion'))

        elif query.data == "download_no":
            txt = get_translation(user_language, "Download_NO")
            await query.edit_message_text(txt)

        else:
            wait = get_translation(user_language, "wait")
            proces = await query.edit_message_text(wait)
            ms_id = proces.message_id

            track_id = query.data
            track_info = sp.track(track_id)
            name = track_info['name']
            artist = track_info['artists'][0]['name']
            video_title = f"{name} - {artist}"
            video_id = get_youtube_video_id(api_key, video_title)

            if not video_id:
                await query.message.reply_text("ERROR: Could not find the video")
                return

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            if os.path.exists(mp3_file_path):
                await query.message.reply_chat_action(action=ChatAction.UPLOAD_VOICE)
                with open(mp3_file_path, "rb") as file:
                    await query.message.reply_audio(audio=file, caption=f"{BOT_USERNAME}", filename=file.name[:-4], performer=artist, title=file.name[:-4],
                                                    duration=info_dict.get('duration'))

                os.remove(mp3_file_path)
            else:
                await query.message.reply_text(
                    get_translation(user_language, 'error').format(e='File not found after conversion'))

            await query._bot.delete_message(message_id=ms_id, chat_id=chat_id)

    except Exception as e:
        error_message = get_translation(user_language, 'error').format(e=e)
        await query.message.reply_text(error_message)
        send_email(f'User:{user}\n\nID:{chat_id}\nMessage: {song_name}\nButtonError: {str(e)}')


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_email(f"BOT_ERROR: {context.error}")

if __name__ == '__main__':
    print("BOT starting...")
    app = Application.builder().token("7259514995:AAGHXOK_VtNhIRi0uIrKDumIfNjsFkGHWnY").build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('recommend', recommend_command))
    app.add_handler(CommandHandler('language', language_command))

    app.add_handler(CallbackQueryHandler(button, pattern='^(?!lang_).*'))
    app.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_audio))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))

    app.add_error_handler(error)

    print("BOT polling...")
    app.run_polling(poll_interval=1.0)