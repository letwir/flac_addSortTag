#!python3
import glob
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import psutil
from mutagen.flac import FLAC
from pykakasi import kakasi

# -*- coding: utf-8 -*-

# kakasiオブジェクトをインスタンス化（日本語の文字種変換用）
kakasi = kakasi()

# モードの設定：漢字・ひらがなをカタカナに変換
kakasi.setMode("J", "K")  # J:漢字→K:カタカナ
kakasi.setMode("H", "K")  # H:ひらがな→K:カタカナ

# ---- ログの設定 ----
logging.basicConfig(
    level=logging.DEBUG,  # ログレベルを設定（必要に応じてDEBUGなどに変更可能）
    format="%(asctime)s [%(levelname)s] %(message)s",  # ログのフォーマット
    handlers=[
        # logging.FileHandler("lastfm_ranking.log"),  # ログをファイルに出力
        logging.StreamHandler(sys.stdout),  # ログをコンソールに出力
    ],
)

# CPUコア数を取得してスレッド数を決定
jobs = psutil.cpu_count(logical=False)  # 論理コア数を取得


def convertKana(text):
    if text == None or text == False:
        return False
    """テキストをカタカナに変換する関数"""
    conv = kakasi.getConverter()
    return conv.do(text)


def insertSortTags(tags: FLAC, file):
    # アルバム名をカタカナに変換して格納
    if tags.get("album"):
        tags["albumsort"] = convertKana(tags["album"][0])
        logging.info("ALBUM: " + tags["albumsort"][0])
    else:
        logging.error(f"Missing ALBUM tags: {file}")

    # アルバムアーティストをカタカナに変換して格納
    if tags.get("albumartist"):
        tags["albumartistsort"] = convertKana(tags["albumartist"][0])
        logging.info("ALBUMARTIST: " + tags["albumartistsort"][0])
    else:
        logging.error(f"Missing ALBUMARTIST tags: {file}")

    # cuesheetタグがある場合
    if "cuesheet" in tags:
        cuelist = tags["cuesheet"][0].splitlines()
        tracknum = ""
        for item in cuelist:
            # TRACK行からトラック番号を取得
            if item.startswith("  TRACK"):
                logging.info(item.split()[1])
                tracknum = str(item.split()[1].rstrip())
            # TITLE行からタイトルを取得し、カタカナに変換して格納
            if item.startswith("    TITLE"):
                tags["CUE_TRACK" + tracknum + "_titlesort"] = convertKana(
                    item.split('TITLE "')[1].rstrip('"')
                )
                logging.info("TITLE: " + tags["CUE_TRACK" + tracknum + "_titlesort"][0])
            # PERFORMER行からアーティストを取得し、カタカナに変換して格納
            if item.startswith("    PERFORMER"):
                tags["CUE_TRACK" + tracknum + "_artistsort"] = convertKana(
                    item.split('PERFORMER "')[1].rstrip('"')
                )
                logging.info(
                    "ARTIST: " + tags["CUE_TRACK" + tracknum + "_artistsort"][0]
                )
            # composerタグがあればコンポーザーもカタカナに変換して格納
            if (
                item.startswith("  TRACK")
                and "cue_track" + tracknum + "_composer" in tags
            ):
                tags["CUE_TRACK" + tracknum + "_composersort"] = convertKana(
                    tags["cue_track" + tracknum + "_composer"][0]
                )
                logging.info(
                    "COMPOSER: " + tags["CUE_TRACK" + tracknum + "_composersort"][0]
                )
    else:
        # cuesheetがない場合、通常のタグをカタカナに変換して格納
        tags["titlesort"] = convertKana(tags["title"][0])
        logging.info("TITLE: " + tags["titlesort"][0])
        tags["artistsort"] = convertKana(tags["artist"][0])
        logging.info("ARTIST: " + tags["artistsort"][0])
        if "composer" in tags:
            tags["composersort"] = convertKana(tags["composer"][0])
            logging.info("COMPOSER: " + tags["composersort"][0])

    # タグ情報を表示して保存
    logging.debug(f"tags: {tags.pprint()}")
    try:
        tags.save()
    except e:
        logging.error(f"Save Error, skip: {file}\n{e}")
        pass


def main(directory):
    # ディレクトリ内の全ファイルを取得
    filelist = glob.glob(os.path.join(directory, "**", "*.flac"), recursive=True)
    # スレッドプールを使用して並列処理を実行
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        futures = []
        for file in filelist:
            # 拡張子が.flacのファイルのみ処理
            if file.endswith(".flac"):
                tags = FLAC()
                try:
                    tags = FLAC(file)
                except e:
                    logging.error(f"FLAC Load Error, skip: {file}\n{e}")
                    continue
                # アルバムソートタグが同じ場合はスキップ。albumタグがない場合も同様(False = False)。
                if tags.get("albumsort")[0] == convertKana(tags.get("album")[0]):
                    logging.debug(f"already sorted. skip: {file}")
                    continue
                futures.append(ex.submit(insertSortTags, tags, file))
        logging.info("-" * 40)
        for f in as_completed(futures):
            logging.info("Completed: " + str(f.result()))
            pass


# メイン処理の実行
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python flac_addSortTag.py <directory>")
        sys.exit(1)
    # コマンドライン引数からディレクトリを取得
    directory = sys.argv[1]
    main(directory)
