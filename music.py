import asyncio
import argparse
import logging
import os
import pickle
from math import ceil
from pycloudmusic import Music163Api, Page
from pycloudmusic.error import Music163BadCode
from code.cmdmusic import Played, Fm_Played
from code.tools import *


parse = argparse.ArgumentParser(description="网易云音乐")
parse.add_argument("-id", "--id", type=str, help="资源 ID (获取指定资源时使用)")
parse.add_argument("-d", "--day", action="store_true", help="获取日推")
parse.add_argument("-a", "--all", action="store_true", help="选中全部")
parse.add_argument("-m", "--music", action="store_true", help="获取歌曲")
parse.add_argument("-pl", "--playlist", action="store_true", help="获取歌单")
parse.add_argument("-at", "--artist", action="store_true", help="获取歌手")
parse.add_argument("-ab", "--album", action="store_true", help="获取专辑")
parse.add_argument("-p", "--play", action="store_true", help="播放队列")
parse.add_argument("-hot", "--hot", action="store_true", help="指定为热门")
parse.add_argument("-u", "--user", action="store_true", help="指定为获取用户 (如使用 -u 后, 使用 -pl 代表获取用户歌单)")
parse.add_argument("-s", "--search", type=str, help="搜索")
parse.add_argument("-l", "--list", action="store_true", help="本次执行将操作队列")
parse.add_argument("-c", "--close", action="store_true", help="清空队列")
parse.add_argument("-f", "--fm", action="store_true", help="私人 Fm")
args = parse.parse_args()


musicapi = Music163Api("_ntes_nnid=7983b729a6f870239f3604c91a0a8ce5,1642650174341; _ntes_nuid=7983b729a6f870239f3604c91a0a8ce5; NMTID=00Oa9FHrrPwjD56kEnStxQZO1Vq8dwAAAF-dZSDxQ; WNMCID=acfhbp.1642650175224.01.0; WEVNSM=1.0.0; nts_mail_user=bd233mc666@163.com:-1:1; WM_TID=v2z6dy5yEMZAUBEBVBM7uH4xfqZKNnSR; ntes_kaola_ad=1; __snaker__id=ooOqtUhkdP4o6lBx; _9755xjdesxxd_=32; NTES_P_UTID=LhT1IucaOtsgZ7atg8Lj318ZBElhv7OC|1656276908; P_INFO=bd233mc666@163.com|1656276908|0|mail163|00&99|null&null&null#shh&null#10#0#0|&0|mail163|bd233mc666@163.com; gdxidpyhxdE=aG+NQLcUhCrRiWhV1r8m2L7ljlvGM2OJvo9ONPcjU6lEyB3UWMsKZuYBskwPP29VOqqvv5xX\XVZp06q7qrp5cd2y+usY9Y/IStZl7GCwwoJsD3Nl1C\MqkYSED9g5UnSN1L4v+ACnViql1VixVXqjBe/KnD78jjNwAPhRVGpmYV14ib:1657702579079; YD00000558929251:WM_NI=V0iirdln3AMkuKGaQoj5rG8hBcSqbOJ/1GV0xQdw4HGtH0SKNh/tA0qKq8CS1qBDVgGzP06gXyoNaB//Xf1HghG/Qw2dLsMgWSAI6XdFmuwGd/m27coS0WxhF/14r+5hRUk=; YD00000558929251:WM_NIKE=9ca17ae2e6ffcda170e2e6ee98d568ad8fbeaad17a89968ba3c54a828f9e86d84ee9b1f7d4f75aacb78f8bee2af0fea7c3b92a96f0a78af170b0b2fda2d061b7958982d465aaebbea8bb6482bd9d92e1458af1ffa8d53cbc8fac98b74485ac88d1d2418eb8e195c43cb395bfd9c259f3af8ea5d56d85a6a0d1b56d9ca7a1afe44aedf19887b444a5b889d0d47df2bc8494d06d958d8faab554a89aa396f64da8f1a3d3b669ad8d00b8fb6486f1ffd5f121f7b89eb6ea37e2a3; YD00000558929251:WM_TID=9QCC4ci+zXBBEUERRQKUBu8ozoEwnRjo; WM_NI=rl+fPeAwNOla9W0qY4Dr95SlkXSGR2q6c0KqlRM6LV9+F7H7QJEiuh05X2sJ7Ev/vWnoCSAevOKTGND2D3w4BdOqgtHJk180+EmGiZDLpc6stvT5oJrGEmd02Kvp8UCLem4=; WM_NIKE=9ca17ae2e6ffcda170e2e6eed4dc7989908a8fc44395e78ab7c15f839b8e82d45d95f188b1b760bbeeffabbb2af0fea7c3b92ab2b4e587d36f83a982b0ef6bfb890092dc4088aef7d6d268a9889da8d13ab3eaadd1ca7bb08e83d7cf5efbf58ad8cb3d93968b8af864f4eb98d3f242f59bbad0f55daeb18db4c46fb69185b5c64688ee8cd4f64082bc8192e6808c96a5d2bb3ce99ba3a8ec528894c084b579b8aa9cd6ee42b2998b8ee73cf295ba91bb5f8194ab8eb737e2a3; __csrf=e15b7f6fb54bd378de3c3ca1b63ed283; MUSIC_U=95e0984f39afc2f239a31ea101710dca05c388183ca5e904a38392df7455b27e519e07624a9f00539ce8deec4848b0dacba99ad2a1357891d9c20fb5f15d6948a43a6a215a8553c6a0d2166338885bd7; _iuqxldmzr_=32; JSESSIONID-WYYY=2eyjpMRc5f7q4ZFT8gXMwtX9nWt/2oqV9WJV9URe4t\EYE\RDWhHnsHUd8QvA0BUiupgsGGc3M2TvqsBddcXAAvM+QFUQtHvOUSYek0VvB19bYyOVT/3PUN7XDhdGBmHn+D8Q/pofv7\X7vaEleDGHh6AathhFs4tAS+KBuPZR6IC1BG:1659899242918")

"""
data_list: api 音乐数据列表 (Music 对象)
checked: 选择数据列表 (Music 对象)
play_list: 播放队列 (Music 对象)
"""

data_list, checked, play_list = [], [], []


async def main():
    global data_list, checked, play_list, play_in
    my = await musicapi.my()
    if my != 200:
        print(my)
    played_ui_select = Played_Ui_Select(musicapi, my)


    # -f 进入私人 fm 模式
    if args.fm:
        with Fm_Played(my.fm()) as played:
            while True:
                await played_ui_select.played_select(played)


    if args.search:
        # -s [搜索内容] -m 搜索歌曲
        if args.music:
            await search(
                Music_Page_Ui, 
                print_music, 
                musicapi.search_music, 
                musicapi.music, 
                args
            )

        # -s [搜索内容] -ab 搜索专辑
        if args.album:
            await search(
                PlayList_Page_Ui, 
                print_album, 
                musicapi.search_album, 
                musicapi.album, 
                args
            )

        # -s [搜索内容] -at 搜索歌手
        if args.artist:
            await search(
                Artist_Page_Ui, 
                print_artist, 
                musicapi.search_artist, 
                musicapi.artist, 
                args
            )

        # -s [搜索内容] -pl 搜索歌单
        if args.playlist:
            await search_playlist(musicapi, args)

        return


    if os.path.isfile("./playlist.pic"):
        try:
            with open("./playlist.pic", "rb") as file_:
                while True:
                    play_list.append(pickle.load(file_))

        except EOFError:
            print(f"队列读取完成, 一共 {len(play_list)} 首歌")
    else:
        print("队列为空...")


    if args.id:
        # -id [资源 id] -m 获取指定歌曲
        if args.music:
            data_list.append(await musicapi.music(args.id))

        # -id [资源 id] -pl 获取指定歌单
        if args.playlist:
            data_list += [music for music in await musicapi.playlist(args.id)]

        # -id [资源 id] -ab 获取指定专辑
        if args.album:
            data_list += [music for music in await musicapi.album(args.id)]
        
        # -id [资源 id] -at 获取指定歌手
        if args.artist:
            artist = await musicapi.artist(args.id)
            hot = True if args.hot else False

            page = Page(artist.song, limit=100, hot=hot)
            page._Page__max_page = ceil(artist.music_size / 100)

            async for music_list in page:
                data_list += [music for music in music_list]
        
    if args.user:
        # -id [资源 id] -u 获取指定用户
        if args.id:
            user = await musicapi.user(args.id)
        
        # -u 指定为 cookie 用户
        else:
            user = None

        # -u -pl 获取 cookie 用户歌单 / -id -u -pl 获取指定用户歌单 
        if args.playlist:
            for playlist in await played_ui_select.select_user_playlist(user):
                playlist = await musicapi.playlist(playlist.id)
                data_list += [music for music in playlist]


    # -d 获取日推
    if args.day:
        data_list += [music for music in await my.recommend_songs()]


    """
    指定 -a 时将结果队列 (data_list) 全部选中
    没有指定 -a 时将结果 (data_list) 一个个选中
    """
    if args.all:
        # 选中全部结果
        checked += data_list
    elif data_list:
        # 选择结果
        checked += Music_Page_Ui(data_list, limt=8).select_page()


    if args.list:
        # -a -c -l 清空播放队列
        if args.close and args.all and play_list:
            os.remove("./playlist.pic")
        
        # -c -l 指定从播放队列中删除
        elif args.close and play_list:
            remove_checked = Music_Page_Ui(play_list, limt=8).select_page()
            with open("./playlist.pic", "wb") as file_:
                for music in play_list:
                    if music in remove_checked:
                        continue
                    pickle.dump(music, file_)

        # -l 向播放队列添加结果
        elif not args.play:
            with open("./playlist.pic", "ab") as file_:
                for music in checked:
                    pickle.dump(music, file_)

        # -p -l 播放队列
        elif play_list:
            checked += Music_Page_Ui(play_list, limt=8).select_page()
            play_list = []
    elif args.list and not play_list and not data_list:
        print("在队列为空下操作队列...")
    

    if args.play:
        if not checked and not play_list:
            # 没有选中结果并且队列中没有歌曲
            logging.info("队列中没有歌曲")
            return
        elif checked:
            # 如果选中结果, 播放选中结果
            logging.info("播放选中结果")
            play_list = checked

        with Played(play_list) as played:
            while True:
                await played_ui_select.played_select(played)


try:
    asyncio.run(main())
except Music163BadCode as err:
    print(f"网易云 API 错误: {err}")
except KeyboardInterrupt:
    pass
finally:
    print("\nstop play~")