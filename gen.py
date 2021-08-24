import json
from typing import Dict

from json_parser import MinecraftJsonParser


def main():
	text = '''{x: -671, y: 69, z: 235, Items: [{Slot: 0b, id: "minecraft:white_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"0-F4#"}'}}}, {Slot: 1b, id: "minecraft:orange_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"1-G4"}'}}}, {Slot: 2b, id: "minecraft:magenta_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"2-G#4"}'}}}, {Slot: 3b, id: "minecraft:light_blue_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"3-A4"}'}}}, {Slot: 4b, id: "minecraft:yellow_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"4-A#4"}'}}}, {Slot: 5b, id: "minecraft:lime_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"5-B4"}'}}}, {Slot: 6b, id: "minecraft:pink_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"6-C5"}'}}}, {Slot: 7b, id: "minecraft:gray_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"7-C#5"}'}}}, {Slot: 8b, id: "minecraft:light_gray_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"8-D5"}'}}}, {Slot: 9b, id: "minecraft:cyan_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"9-D#5"}'}}}, {Slot: 10b, id: "minecraft:purple_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"10-E5"}'}}}, {Slot: 11b, id: "minecraft:blue_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"11-F5"}'}}}, {Slot: 12b, id: "minecraft:brown_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"12-F#5"}'}}}, {Slot: 13b, id: "minecraft:green_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"13-G5"}'}}}, {Slot: 14b, id: "minecraft:red_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"14-G#5"}'}}}, {Slot: 15b, id: "minecraft:black_concrete", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"15-A5"}'}}}, {Slot: 16b, id: "minecraft:white_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"16-A#5"}'}}}, {Slot: 17b, id: "minecraft:orange_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"17-B5"}'}}}, {Slot: 18b, id: "minecraft:magenta_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"18-C6"}'}}}, {Slot: 19b, id: "minecraft:light_blue_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"19-C#6"}'}}}, {Slot: 20b, id: "minecraft:yellow_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"20-D6"}'}}}, {Slot: 21b, id: "minecraft:lime_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"21-D#6"}'}}}, {Slot: 22b, id: "minecraft:pink_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"22-E6"}'}}}, {Slot: 23b, id: "minecraft:gray_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"23-F6"}'}}}, {Slot: 24b, id: "minecraft:light_gray_concrete_powder", Count: 64b, tag: {RepairCost: 0, display: {Name: '{"text":"24-F#6"}'}}}], id: "minecraft:shulker_box"}'''
	data = MinecraftJsonParser.convert_minecraft_json(text)
	with open('gen_items_raw.json', 'w') as file:
		json.dump(data, file, indent=4, ensure_ascii=False)
	from main import Item
	mapping: Dict[str, Item] = {}
	for item in data['Items']:
		mapping[str(item['Slot'])] = Item(
			id=item['id'],
			name=json.loads(item['tag']['display']['Name'])['text']
		)
	with open('gen_items.json', 'w') as file:
		from mcdreforged.utils.serializer import serialize
		json.dump(serialize(mapping), file, indent=4, ensure_ascii=False)

	text = '''f# g g# a a# b c1 c1# d1 d1# e1 f1 f1# g1 g1# a1 a1# b1 c2 c2# d2 d2# e2 f2 f2#'''
	symbols = {}
	for i, seg in enumerate(text.split(' ')):
		symbols[seg] = str(i)
	for key, value in mapping.items():
		symbols[value.name.split('-')[1]] = key

	with open('gen_symbols.json', 'w') as file:
		json.dump(symbols, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
	main()
