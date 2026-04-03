# flac_addSortTag
## 概要
flacファイルにカタカナ、英字でソートタグを追記します。  
  
## 事の発端
音楽ファイルをfoobar2000やiTunesで管理していると、アーティスト名のフリガナが無いとソートが不便だったので作った。
  
## 詳細
CueSheet埋め込みflac (flac+cue) に対応しており、
内部のCuesheetから情報を読み取って  
MutagenによりVorbisCommentへ書き込みます。  
  
外部にCueSheetを置いている場合は対応していません。　(hoge.flac, hoge.cue)  
cuetools等で1ファイルにまとめている OR 1ファイル1曲のflacに対応しています。(hoge.flac)  
  
  
 - - - - - -   
## 使い方  
### インストール
依存関係をpipもしくはvenv環境下でインストールします。  
```
# 前提プラグインのインストール
# **Linuxの方はvenvを使用してください。**
pip install pykakasi
pip install mutagen
# 本体のダウンロード
curl https://raw.githubusercontent.com/letwir/flac_addSortTag/refs/heads/main/flac_addSortTag.py -o flac_addSortTag.py
```
### 実行
Windowsユーザー
```
python flac_addSortTag.py <ディレクトリ>
```
**Linuxユーザーは以下**
```
python3 flac_addSortTag.py <ディレクトリ>
```
ディレクトリ以下のflacファイルを全検索します。  
 * 漢字、ひらがな -> カタカナ  
 * 英字はそのまま  
の変換を行います。
  
  
変換したものを各sortタグに格納します。
以下内容
  
 * TITLE -> titlesort  
 * ARTIST -> artistsort  
 * COMPOSER -> composersort  
 * ALBUMARTIST -> albumartistsort  
 * ALBUM -> albumsort  
   
### TIPS
メタタグ領域のパディングが少ないとかなり時間がかかるので事前に拡張しておくことをオススメします。  
<例>  
```
metaflac --add-padding=2044 <flacファイル>
# or
flac -P 2044 <flacファイル> -o <出力先>
```
