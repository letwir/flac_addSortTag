# flac_addSortTag
mutagenを使ってflacファイルにカタカナ、英字でソートタグを追記します。  
CueSheet埋め込みflac(flac+cue)に対応しており、内部のCuesheetから情報を読み取って  
MutagenによりVorbisCommentへ書き込みます。  
  
外部にCueSheetを置いている場合は対応していません。　(hoge.flac, hoge.cue)  
cuetools等で1ファイルにまとめている OR 1ファイル1曲のflacに対応しています。(hoge.flac)  
  
  
# 事前準備
以下が依存なのでpipもしくはpipxでインストールします。  
```
pipx install pykakasi
pipx install mutagen
```
 - - - - - -   
# 使い方  
```
python flac_addSortTag.py <ディレクトリ>
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
   
メタタグ領域のパディングが少ないとかなり時間がかかるので事前に拡張しておくことをオススメします。  
<例>  
```
flac -P 2044 <flacファイル> -o <出力先>
`metaflac --add-padding=2044 <flacファイル>
```
