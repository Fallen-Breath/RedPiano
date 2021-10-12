import json
from typing import Dict, List

from item import Item, Sheet
from serializer import Serializable


class Configure(Serializable):
	symbols: Dict[str, str]
	items: Dict[str, Item]


config = Configure.get_default()


def main():
	with open('config.json') as file:
		config.update_from(json.load(file))

	sequence: List[str] = []
	with open('input.txt') as file:
		for line in file.readlines():
			for seg in line.strip().split(' '):
				if len(seg) > 0:
					seg = config.symbols.get(seg, seg)
					sequence.append(seg)

	sheet = Sheet()
	for seg in sequence:
		item = config.items.get(seg)
		if item is not None:
			sheet.add_item(Item(
				id=item.id,
				count=1,
				name=item.name
			))
		else:
			print('Unknown segment {}'.format(seg))

	sheet.done()
	with open('output.txt', 'w') as file:
		for shulker in sheet.shulkers:
			file.write(shulker.to_give_command())
			file.write('\n')


if __name__ == '__main__':
	main()
