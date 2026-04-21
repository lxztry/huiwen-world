content = open('game_master.py', encoding='utf-8').read()
replacements = [
    ("'lin_daiyu'", "'lin-daiyu'"),
    ("'zhuge_liang'", "'zhuge-liang'"),
    ("'song_jiang'", "'song-jiang'"),
    ("'wu_song'", "'wu-song'"),
    ("'sun_wukong'", "'sun-wukong'"),
]
for old, new in replacements:
    content = content.replace(old, new)
open('game_master.py', 'w', encoding='utf-8').write(content)
print('Done')
