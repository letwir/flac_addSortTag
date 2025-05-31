#!python3
from pykakasi import kakasi
from mutagen.flac import FLAC
import glob
import sys
import os

# -*- coding: utf-8 -*-

# kakasiオブジェクトをインスタンス化（日本語の文字種変換用）
kakasi = kakasi()

# モードの設定：漢字・ひらがなをカタカナに変換
kakasi.setMode("J", "K")  # J:漢字→K:カタカナ
kakasi.setMode("H", "K")  # H:ひらがな→K:カタカナ

# コマンドライン引数からディレクトリを取得
directory = sys.argv[1]
# ディレクトリ内の全ファイルを取得
filelist = glob.glob(os.path.join(directory, "**", "*.flac"), recursive=True)

def main():
    for file in filelist:
        # 拡張子が.flacのファイルのみ処理
        if file.endswith(".flac"):
            tags = FLAC(file)
            # cuesheetタグがある場合
            if "cuesheet" in tags:
                cuelist = tags["cuesheet"][0].splitlines()
                print(cuelist)
                tracknum = ""
                for item in cuelist:
                    # TRACK行からトラック番号を取得
                    if item.startswith("  TRACK"):
                        print(item.split()[1])
                        tracknum = str(item.split()[1].rstrip())
                    # TITLE行からタイトルを取得し、カタカナに変換して格納
                    if item.startswith("    TITLE"):
                        tags["CUE_TRACK" + tracknum + "_titlesort"] = convertKana(
                            item.split('TITLE "')[1].rstrip('"')
                        )
                        print(
                            "TITLE: " + tags["CUE_TRACK" + tracknum + "_titlesort"][0]
                        )
                    # PERFORMER行からアーティストを取得し、カタカナに変換して格納
                    if item.startswith("    PERFORMER"):
                        tags["CUE_TRACK" + tracknum + "_artistsort"] = convertKana(
                            item.split('PERFORMER "')[1].rstrip('"')
                        )
                        print(
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
                        print(
                            "COMPOSER: "
                            + tags["CUE_TRACK" + tracknum + "_composersort"][0]
                        )
            else:
                # cuesheetがない場合、通常のタグをカタカナに変換して格納
                tags["artistsort"] = convertKana(tags["artist"][0])
                print("ARTIST: " + tags["artistsort"][0])
                tags["titlesort"] = convertKana(tags["title"][0])
                print("TITLE: " + tags["titlesort"][0])
                if "composer" in tags:
                    tags["composersort"] = convertKana(tags["composer"][0])
                    print("COMPOSER: " + tags["composersort"][0])

            # アルバムアーティストをカタカナに変換して格納
            tags["albumartistsort"] = convertKana(tags["albumartist"][0])
            print("ALBUMARTIST: " + tags["albumartistsort"][0])
            # アルバム名をカタカナに変換して格納
            tags["albumsort"] = convertKana(tags["album"][0])
            print("ALBUM: " + tags["albumsort"][0])
            # タグ情報を表示
            tags.pprint()
            # タグを保存
            tags.save()

# 文字列をカタカナに変換する関数
def convertKana(text):
    conv = kakasi.getConverter()
    return conv.do(text)

# メイン処理の実行
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python flac_sortTag.py <directory>")
        sys.exit(1)
    main()
