import json
from typing import Dict

from json_parser import MinecraftJsonParser


def main():
	text = '''
{x: 100761, y: 1, z: 225, Items: [{Slot: 0b, id: "minecraft:white_carpet", Count: 64b}, {Slot: 1b, id: "minecraft:orange_carpet", Count: 64b}, {Slot: 2b, id: "minecraft:magenta_carpet", Count: 64b}, {Slot: 3b, id: "minecraft:light_blue_carpet", Count: 64b}, {Slot: 4b, id: "minecraft:yellow_carpet", Count: 64b}, {Slot: 5b, id: "minecraft:lime_carpet", Count: 64b}, {Slot: 6b, id: "minecraft:pink_carpet", Count: 64b}, {Slot: 7b, id: "minecraft:gray_carpet", Count: 64b}, {Slot: 8b, id: "minecraft:light_gray_carpet", Count: 64b}, {Slot: 9b, id: "minecraft:cyan_carpet", Count: 64b}, {Slot: 10b, id: "minecraft:purple_carpet", Count: 64b}, {Slot: 11b, id: "minecraft:blue_carpet", Count: 64b}, {Slot: 12b, id: "minecraft:brown_carpet", Count: 64b}, {Slot: 13b, id: "minecraft:green_carpet", Count: 64b}, {Slot: 14b, id: "minecraft:red_carpet", Count: 64b}, {Slot: 15b, id: "minecraft:black_carpet", Count: 64b}], id: "minecraft:shulker_box"}
'''
	data = MinecraftJsonParser.convert_minecraft_json(text.strip())
	mapping: Dict[str, str] = {}
	for item in data['Items']:
		mapping[str(item['Slot'])] = item['id']
	with open('gen_items.json', 'w') as file:
		from mcdreforged.utils.serializer import serialize
		json.dump(serialize(mapping), file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
	main()
