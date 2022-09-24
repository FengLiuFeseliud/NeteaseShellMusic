import asyncio
from pycloudmusic.object.music163 import *
from abc import abstractmethod, ABCMeta
from math import ceil
from pycloudmusic import Page, Music163Api
from pycloudmusic.object.music163 import User, My
import os

from code.cmdmusic import Played


"""
输出样式
"""


def print_music(music: Music):
    os.system("cls")
    print(
        music.name_str, 
        "\n\n\n\n",
        f"歌手: {music.artist_str}\n\n",
        f"专辑: {music.album_str}\n\n",
        f"ID: {music.id}\n\n",
        "[up] 上一首 [down] 下一首 [stop] 停止播放\n\n",
        "[like] 红心歌曲 [sub] 收藏至歌单 [at] 获取歌手 [ab] 获取专辑\n\n",
        "[list] 查看播放队列 / 选择队列播放位置"
    )


def print_search_music(music: Music):
    print(
        f"\n\n{music.name_str}", 
        "\n\n\n\n",
        f"歌手: {music.artist_str}\n\n",
        f"专辑: {music.album_str}\n\n",
        f"ID: {music.id}"
    )


def print_album(album: Album):
    print(
        f"\n\n{album.name}",
        f"\n\n\n\n",
        f"歌手: {album.artists_str}\n\n",
        f"ID: {album.id}\n\n",
        f"{album.description}"
    )


def print_artist(artist: Artist):
    print(
        f"\n\n{artist.name}",
        f"\n\n\n\n",
        f"单曲数: {artist.music_size}\n\n",
        f"专辑数: {artist.album_size}\n\n",
        f"Mv数: {artist.mv_size}\n\n",
        f"ID: {artist.id}\n\n",
        f"{artist.brief_desc_str}"
    )


def print_playlist(playlist: PlayList):
    print(
        f"\n\n{playlist.name}",
        f"\n\n\n\n",
        f"用户: {playlist.user_str}\n\n",
        f"单曲数: {len(playlist.music_list)}\n\n",
        f"ID: {playlist.id}\n\n",
        f"{playlist.description}"
    )


"""
UI 操作
"""

async def search(page_ui, print_fun, search_api, get_api, args, limt = 8):
    search_data_list = []
    for _, page in await Page(search_api, key=args.search).all():
        search_data_list += [search_data for search_data in page]

    search_data = page_ui(search_data_list, limt=limt).select_page()

    for data in search_data:
        print_fun(await get_api(data.id))


async def search_playlist(musicapi: Music163Api, args, limt = 8):
    search_data_list = []
    def all_page(data):
        return data['result']["playlistCount"]

    for data in await Page(musicapi._search, type_="1000", key=args.search).all(all_page):
        if data['result']["playlistCount"] == 0:
            continue
        
        search_data_list += data['result']["playlists"]

    search_data = PlayList_Search_Page_Ui(search_data_list, limt=limt).select_page()

    for data in search_data:
        print_playlist(await musicapi.playlist(data["id"]))


class Page_Ui(metaclass=ABCMeta):

    def __init__(
        self,
        data_list: list[Any],
        limt: int
    ) -> None:
        self.data_list_len, page_len_in = len(data_list),  0
        self.page_len = ceil(self.data_list_len / limt)
        self._limt = limt
        self._data_list = {}
        self._select_data_list = []

        while page_len_in < self.page_len:
            self._data_list[page_len_in] = data_list[page_len_in * limt:(page_len_in + 1) * limt]
            page_len_in += 1
    
    def select_page(self, page_index: int = 0):
        page = self._data_list[page_index]
        mode = self.print_page(page, page_index)

        if mode == "":
            return self.select_page(page_index)

        elif mode[0] == ":":
            input_page_index = int(mode[1:]) - 1
            return self.select_page(input_page_index)
        
        elif mode == "end":
            return self._select_data_list
        
        else:
            try:
                input_data_index_list = mode.split(" ")
                for index in input_data_index_list:
                    index = int(index)
                    index -= 1
                    if index > self._limt:
                        continue
                    
                    if index < 0:
                        continue

                    self._select_data_list.append(page[index])
            except ValueError:
                pass

            return self.select_page(page_index)

    @abstractmethod
    def _print_page(self, page: Any):
        pass

    def print_page(self, page: Any, page_index: int):
        os.system("cls")
        self._print_page(page)
        return input(f"当前在第 {page_index + 1} 页, 总共 {self.page_len} 页, {self.data_list_len} 条结果 >> ")


class Artist_Page_Ui(Page_Ui):

    def _print_page(self, page: list[Artist]):
        data_in = 1
        for data in page:
            try:
                name, id_ = data["name"], data["id"]
            except TypeError:
                name, id_ = data.name, data.id

            print(f"[{data_in}] {name} ID: {id_}\n")
            data_in += 1


class PlayList_Page_Ui(Page_Ui):

    def _print_page(self, page: list[PlayList]):
        data_in = 1
        for data in page:
            print(f"[{data_in}] {data.name} ID: {data.id}\n")
            data_in += 1


class PlayList_Search_Page_Ui(Page_Ui):

    def _print_page(self, page: list[dict[str, Any]]):
        data_in = 1
        for data in page:
            print("[%s] %s 用户: %s\n" % (data_in, data["name"], data["creator"]["nickname"]))
            data_in += 1


class Music_Page_Ui(Page_Ui):

    def _print_page(self, page: list[Music]):
        data_in = 1
        for data in page:
            print(f"[{data_in}] {data.name_str} - {data.artist_str} ID: {data.id}\n")
            data_in += 1


class Played_Ui_Select:

    def __init__(
        self, 
        musicapi: Music163Api, 
        my: My, 
        limt: int = 8
    ) -> None:
        self._musicapi = musicapi
        self._my = my
        self._limt = limt
        self._my_play_list = []

    async def select_user_playlist(self, user: User = None):
        data_list = []
        if not self._my_play_list and user is None:
            data_list.append(await self._my.like_music())
            page = Page(self._my.playlist, limit=30)
            page.set_max_page(99)
        else:
            page = Page(user.playlist, limit=30)
            page.set_max_page(99)

        if not self._my_play_list or user is not None:
            async for playlist_list in page:
                data = [playlist for playlist in playlist_list]
                if not data:
                    break
                
                data_list += data
        
        if user is None:
            if data_list:
                self._my_play_list = data_list
            
            ui = PlayList_Page_Ui(self._my_play_list, self._limt)
        else:
            ui = PlayList_Page_Ui(data_list, self._limt)

        return ui.select_page()

    async def played_select(self, played: Played):
        mode = input()
        music = played.get_play_music()
        print_music(music)

        if mode == "down":
            played.down()
        
        elif mode == "up":
            played.up()
        
        elif mode == "stop":
            played.stop()

            import sys
            sys.exit()

        elif mode == "like":
            print(await music.like())

        elif mode == "ab":
            print_album(await music.album())

        elif mode == "at":
            ui = Artist_Page_Ui(music.artist, self._limt)
            data_list = ui.select_page()
            print_music(music)
            if not data_list:
                return
            
            tasks = [asyncio.create_task(self._musicapi.artist(data["id"])) for data in data_list]
            done, _ = await asyncio.wait(tasks)
            
            for task in done:
                print_artist(task.result())
        
        elif mode == "sub":
            data_list = await self.select_user_playlist()
            print_music(music)

            if not data_list:
                return

            tasks = [asyncio.create_task(playlist.add(music.id)) for playlist in data_list]
            done, _ = await asyncio.wait(tasks)
            
            for task in done:
                print(task.result())
        
        elif mode == "list":
            play_in_music = Music_Page_Ui(played._music_list, self._limt).select_page()
            if not play_in_music:
                return

            played.set_play_in_music(play_in_music[0])