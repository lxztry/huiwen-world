import sys
sys.path.insert(0, '.')

import character
import database

print("=== Database ===")
database.init_db()

print("\n=== Characters ===")
chars = character.list_characters()
for c in chars:
    print(f"  {c['character_id']}: {c['name']} (《{c['work']}》)")

print("\n=== Character Prompt Test ===")
prompt = character.build_character_prompt("lin-daiyu", {
    'wenge_type': '书香门第',
    'wenge_name': '测试用户',
    'catchphrase': '唉，说来话长……'
}, familiarity=1)
print(f"Prompt length: {len(prompt)} chars")
print(f"Contains 林黛玉: {'林黛玉' in prompt}")
print(f"Contains 熟悉度: {'熟悉' in prompt}")

print("\n=== Game Master Test ===")
import game_master
gm = game_master.GameMaster()

# Test character list
chars = gm.list_characters()
print(f"GameMaster loaded {len(chars)} characters")

# Test user registration
test_user = "test_user_001"
if not gm.is_registered(test_user):
    result = gm.start_wen_ge_setup(test_user, "书香门第")
    print(f"Started wenge setup: type={result['wenge_type']}, questions={len(result['questions'])}")

print("\nAll tests passed!")
