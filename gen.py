import json
from typing import Dict

from json_parser import MinecraftJsonParser


def main():
	text = '''
{x: 100765, y: 1, z: 172, Items: [{Slot: 0b, id: "minecraft:shulker_box", Count: 1b, tag: {BlockEntityTag: {Items: [{Slot: 0, id: "minecraft:light_blue_concrete", tag: {display: {Name: '{"text": "3_A"}'}}, Count: 1}, {Slot: 1, id: "minecraft:light_gray_concrete_powder", tag: {display: {Name: '{"text": "24_F#"}'}}, Count: 1}, {Slot: 2, id: "minecraft:purple_concrete", tag: {display: {Name: '{"text": "10_E"}'}}, Count: 1}, {Slot: 3, id: "minecraft:oak_fence", tag: {display: {Name: '{"text": "X"}'}}, Count: 1}, {Slot: 0, id: "minecraft:light_gray_carpet", tag: {display: {Name: '{"text": "1000"}'}}, Count: 3}, {Slot: 1, id: "minecraft:white_carpet", tag: {display: {Name: '{"text": "0000"}'}}, Count: 1}]}, display: {Name: '{"text": "音轨#1节奏序列-1"}'}}}], id: "minecraft:chest"}
'''
	data = MinecraftJsonParser.convert_minecraft_json(text.strip())
	with open('gen_items_raw.json', 'w') as file:
		json.dump(data, file, indent=4, ensure_ascii=False)
	mapping: Dict[str, str] = {}
	for item in data['Items']:
		mapping[str(item['Slot'])] = item['id']
	with open('gen_items.json', 'w') as file:
		from mcdreforged.utils.serializer import serialize
		json.dump(serialize(mapping), file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
	main()
