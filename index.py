from aiogram import *
from aiogram.types import InputFile
import random
import string
import os
import requests
import json
import urllib.parse
from subprocess import check_output
from concurrent.futures import as_completed, ThreadPoolExecutor
import time

# actually dont really matter
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
downloads = os.listdir('.\downloads')

# whitelist, here your user id
whitelist = [id]
# username of your bot in telegram (e.g. sticker_creator_29bot)
bot_link = 'any_bot' 
# title for stickerpacks
packs_title = '@username text 🎈'

# init bot
TOKEN = "YOUR TOKEN HERE"
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot)

# start message
@dp.message_handler(commands=['start', 'newpack'])
async def cmd_start(message: types.message):
    await message.answer(f"Hi!")

# get sticker and do some magic!
@dp.message_handler(content_types=['sticker'])
async def check_sticker(message: types.Message):
    if message.from_user.id in whitelist:
        await message.answer("⏰wait...")
        # get stickerpack info
        set = await bot.get_sticker_set(message.sticker.set_name)
        sticks = []
        for item in set.stickers:
            InputSticker = [item.file_id, item.emoji]
            sticks.append(InputSticker)
        sts_format = 0
        if set.is_animated:
            sts_format = "animated"
        elif set.is_video:
            sts_format = 'video'
        else:
            sts_format = 'static'
        sts_type = set.sticker_type
        # getting info about first sticker in pack, to create our pack
        stt1 = sticks.pop(0)
        em1 = stt1[1]
        st1 = stt1[0]
        # generate link
        name = genName() + "_by_" + bot_link
        print(sts_format, name)

        # static stickerpack
        if sts_format == 'static':
            bool = await bot.create_new_sticker_set(user_id=message.from_user.id, name=name, title=packs_title, emojis=em1, png_sticker=st1)
            if bool:
                msg_proc = await message.answer(f"☑️Stickerpack creaeted\n1 / {len(sticks)+1}")
            else:
                await message.answer(f"Error(")
            procces = 1
            for item in sticks:
                em1 = item[1]
                st1 = item[0]
                procces += 1
                await bot.add_sticker_to_set(user_id=message.from_user.id, name=name, emojis=em1, png_sticker=st1)
                await bot.edit_message_text(text=f"☑️Stickerpack creaeted\n{procces} / {len(sticks)+1}", chat_id=message.chat.id, message_id=msg_proc["message_id"])
            if bool:
                await bot.edit_message_text(text=f"✅Stickerpack creaeted\n{procces} / {len(sticks)+1}\n\nSuccess, url: https://t.me/addstickers/{name}", chat_id=message.chat.id, message_id=msg_proc["message_id"])
            else:
                await message.answer(f"Error(")
        # animated or video stickerpack
        if sts_format == 'animated' or sts_format == 'video':
            # download and sort
            download_anim_stickers(TOKEN=TOKEN,set_name=set.name)
            msg_proc = await message.answer(f"✅Download complete")
            stickFilesList = os.listdir(f".\downloads\{set.name}\webp")
            stickFilesList.sort(key=get_file_num)
            ststfl = stickFilesList.pop(0)
            firstStickPath = os.fspath(
                f'.\downloads\{set.name}\webp\{ststfl}')
            #  creating stickerpack
            stick = InputFile(firstStickPath)
            if get_file_dot(stickFilesList) == 'tgs':
                bool = await bot.create_new_sticker_set(user_id=message.from_user.id, name=name, title=packs_title, emojis=em1, tgs_sticker=stick, )
            elif get_file_dot(stickFilesList) == 'webm':
                bool = await bot.create_new_sticker_set(user_id=message.from_user.id, name=name, title=packs_title, emojis=em1, webm_sticker=stick, )
            if bool:
                await bot.edit_message_text(text=f"✅Download complete\n☑️Stickerpack creaeted\n1 / {len(sticks)+1}\nurl: https://t.me/addstickers/{name}", chat_id=message.chat.id, message_id=msg_proc["message_id"])

            else:
                await message.answer(f"Error(")
            procces = 1
            # add stickers in pack
            for item in stickFilesList:
                try:
                    try:
                        for itemm in sticks:
                            em1 = itemm[1]
                    except: em1 = "✨"
                    firstStickPath = os.fspath(
                        f'.\downloads\{set.name}\webp\{item}')

                    stick = InputFile(firstStickPath)
                    procces += 1
                    
                    if get_file_dot(stickFilesList) == 'tgs':
                        await bot.add_sticker_to_set(user_id=message.from_user.id, name=name, emojis=em1, tgs_sticker=stick)
                    if get_file_dot(stickFilesList) == 'webm':
                        await bot.add_sticker_to_set(user_id=message.from_user.id, name=name, emojis=em1, webm_sticker=stick)
                    await bot.edit_message_text(text=f"✅Download complete\n☑️Stickerpack creaeted\n{procces} / {len(sticks)+1}\nurl: https://t.me/addstickers/{name}", chat_id=message.chat.id, message_id=msg_proc["message_id"])
                except: continue
            # final message
            if procces == len(sticks)+1:
                await bot.edit_message_text(text=f"✅Download complete\n✅Stickerpack creaeted\n{procces} / {len(sticks)+1}\n\nSuccess, url: https://t.me/addstickers/{name}", chat_id=message.chat.id, message_id=msg_proc["message_id"])
            else:
                await message.answer(f"Error!( Error(\n please let me know (@)")
            # delete temp files
            stickFilesList = os.listdir(f".\downloads\{set.name}\webp")
            for item in stickFilesList:
                os.remove(f'.\downloads\{set.name}\webp\{item}')
            os.rmdir(f'.\downloads\{set.name}\webp')
            os.rmdir(f'.\downloads\{set.name}')
    else:
        await message.answer(f"You aren't whitelisted!")

# generate random link in 8 random letters 
def genName():
    letters = string.ascii_letters
    res = ''.join(random.choice(letters) for i in range(8))
    return res

# sort downloaded stickers (for animated or video)
def get_file_num(item):
    return int(item.split('_')[1].split('.')[0])

# get file extension
def get_file_dot(list):
    return list[0].split('_')[1].split('.')[1]

# download anim stickers (literally)
def download_anim_stickers(TOKEN, set_name):
    
    def assure_folder_exists(folder, root):
        full_path = os.path.join(root, folder)
        if os.path.isdir(full_path):
            pass
        else:
            os.mkdir(full_path)
        return full_path


    def random_filename(length, ext):
        return ''.join([random.choice(string.ascii_lowercase) for _ in range(length)]) + '.{}'.format(ext)


    # TODO: Replace with a named tuple
    class File:
        def __init__(self, name, link):
            self.name = name
            self.link = link

        def __repr__(self):
            return '<F:{}>'.format(self.name)


    class StickerDownloader:
        def __init__(self, token, session=None, multithreading=4):
            self.THREADS = multithreading
            self.token = token
            self.cwd = assure_folder_exists('downloads', root=os.getcwd())
            if session is None:
                self.session = requests.Session()
            else:
                self.session = session
            self.api = 'https://api.telegram.org/bot{}/'.format(self.token)
            verify = self._api_request('getMe', {})
            if verify['ok']:
                pass
            else:
                print('Invalid token.')
                exit()

        def _api_request(self, fstring, params):
            try:
                param_string = '?' + urllib.parse.urlencode(params)
                res = self.session.get('{}{}{}'.format(self.api, fstring, param_string))
                if res.status_code != 200:
                    raise Exception
                res = json.loads(res.content.decode('utf-8'))
                if not res['ok']:
                    raise Exception(res['description'])
                return res

            except Exception as e:
                print('API method {} failed. Error: "{}"'.format(fstring, e))
                return None

        def get_file(self, file_id):
            info = self._api_request('getFile', {'file_id': file_id})
            f = File(name=info['result']['file_path'].split('/')[-1],
                    link='https://api.telegram.org/file/bot{}/{}'.format(self.token, info['result']['file_path']))

            return f

        def get_sticker_set(self, name):
            """
            Get a list of File objects.
            :param name:
            :return:
            """
            params = {'name': name}
            res = self._api_request('getStickerSet', params)
            if res is None:
                return None
            stickers = res['result']['stickers']
            files = []
            print('Search "{}" ..'.format(name))
            with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
                futures = [executor.submit(self.get_file, i['file_id']) for i in stickers]
                for i in as_completed(futures):
                    files.append(i.result())


            sticker_set = {
                'name': res['result']['name'].lower(),
                'title': res['result']['title'],
                'files': files
            }
            return sticker_set

        def download_file(self, name, link, path):
            time.sleep(0.5)
            file_path = os.path.join(path, name)
            with open(file_path, 'wb') as f:
                res = self.session.get(link)
                f.write(res.content)

            return file_path

        def download_sticker_set(self, sticker_set):
            swd = assure_folder_exists(sticker_set['name'], root=self.cwd)
            download_path = assure_folder_exists('webp', root=swd)
            downloads = []

            print('Download "{}" in {}'.format(sticker_set['name'], download_path))
            with ThreadPoolExecutor(max_workers=self.THREADS) as executor:
                futures = [executor.submit(self.download_file, f.name, f.link, download_path) for f in sticker_set['files']]
                for i in as_completed(futures):
                    downloads.append(i.result())


            return downloads

        @staticmethod
        def convert_file(_input, _output):
            command = 'dwebp -quiet "{}" -o "{}"'.format(_input, _output)
            check_output(command, shell=True)
            return _output

        def convert_to_pngs(self, name):
            print()


    if __name__ == "__main__":
        downloader = StickerDownloader(TOKEN)
        print('StickerGraber start..')
        names = []
        names.append(set_name)

        for sset in names:
            print('=' * 60)
            _ = downloader.get_sticker_set(sset)
            if _ is None:
                continue
            print('-' * 60)
            _ = downloader.download_sticker_set(_)
            print('-' * 60)
            downloader.convert_to_pngs(sset)

# i dont know
@dp.message_handler()
async def answer(message: types.message):
    await message.reply(f"just send me sticker...")

# start
if __name__ == "__main__":
    executor.start_polling(dp)

# dont touch
input()
