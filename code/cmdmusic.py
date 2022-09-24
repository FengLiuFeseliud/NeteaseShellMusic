import asyncio
from subprocess import Popen, DEVNULL
from threading import Thread
import time
from typing import Union
from pycloudmusic.object.music163 import Music
import os


class Played:

    def __init__(
        self, 
        play_music_list: Union[list[Music], Music], 
        cache_play_music = 2
    ) -> None:
        self._music_list: list[Music] = []
        self._cache_play_music = cache_play_music
        self._music_index = 0
        self._play_in = False
        self._sh = None
        self.add_play_music(play_music_list)

    def __enter__(self):
        self.start()
        time.sleep(0.5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._sh is None:
            return

        self.stop()

    def start(self):
        def play(self):
            async def start(self):
                self._play_in = True
                while self._play_in:
                    try:
                        await self.play()
                    except IndexError:
                        await asyncio.sleep(1)
                        if self._music_list == []:
                            continue

                        self._music_index = 0
            
            asyncio.run(start(self))
        
        thread = Thread(target=play, args=(self,))
        thread.setDaemon(True)
        thread.start()
    
    def stop(self):
        self._play_in = False
        self._sh.terminate()
        self._music_index -= 1

    def up(self):
        if self._music_index  < 0:
            self._music_index = len(self._music_list) - 1
        else:
            self._music_index -= 2
        
        self._sh.terminate()

    def down(self):
        self._sh.terminate()
    
    def get_play_music(self):
        return self._music_list[self._music_index]

    def add_play_music(self, music: Union[list[Music], Music]):
        if type(music) is list:
            self._music_list += music
        else:
            self._music_list.append(music)

    async def _play_music(self):
        from code.tools import print_music

        music = self.get_play_music()
        music_path = os.path.abspath(f"./download/{music.id}.mp3")
        if not os.path.isfile(music_path):
            await music.play()
        
        self._sh = Popen(f"mpg123 {music_path}", stdout=DEVNULL, stderr=DEVNULL)
        print_music(music)

    async def play(self):
        await self._play_music()
        self._sh.wait()
        self._music_index += 1

    def set_play_in_music(self, music: Music):
        if not music in self._music_list:
            return
            
        self._music_index = self._music_list.index(music) - 1
        self.down()


class Fm_Played(Played):

    def __init__(
        self,
        fm,
        cache_play_music=2
    ) -> None:
        super().__init__([], cache_play_music)
        self.fm = fm

    async def play(self):
        if len(self._music_list) == self._music_index:
            await self.fm.read()
            self.add_play_music([music for music in self.fm])

        await self._play_music()
        self._sh.wait()
        self._music_index += 1