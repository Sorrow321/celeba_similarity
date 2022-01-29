import telebot
import yaml
import logging
from pathlib import Path
from query import get_embedding_from_file
from qdrant_client import QdrantClient


yaml_path = Path(__file__).parent / 'cfg.yaml'
with open(yaml_path, 'r') as file:
    try:
        cfg = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        print(exc)


API_KEY = cfg['API_KEY']
COLLECTION_NAME = cfg['collection_name']

logging.basicConfig(
    filename=cfg['log_file'],
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s'
)
bot = telebot.TeleBot(API_KEY, parse_mode=None)
client = QdrantClient(host="localhost", port=6333)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Send me voice message and I will tell which celebrity does your voice sounds like.") # noqa: 501


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    logging.debug(f'New audio received. Chat id {message.chat.id}. Sender name: {message.chat.first_name}') # noqa: 501
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('last_sound.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    query_embedding = get_embedding_from_file(Path('last_sound.ogg'))
    hits = client.search(
        collection_name='vox_celeba',
        query_vector=query_embedding,
        query_filter=None,
        append_payload=True,
        top=5
    )
    for i, (point, payload) in enumerate(hits):
        celeba_name = payload['full_name'][0].replace('_', ' ')
        msg = f'Top-{i+1} matching celebrity: ' + celeba_name
        msg += '\n'
        msg += f'Score: {point.score}'
        sample_path = Path('voxceleba1') / payload['speaker_id'][0] / payload['video_link'][0] / payload['utterance'][0]  # noqa: 501
        bot.reply_to(message, msg)
        bot.send_audio(chat_id=message.chat.id, audio=open(sample_path, 'rb'))


bot.infinity_polling()
