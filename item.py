import json
from typing import Dict, List

from serializer import Serializable


class Item(Serializable):
	id: str
	name: str
	count: int
	slot: int

	def to_dict(self) -> dict:
		ret = {
			'id': self.id,
			'tag': {
				'display': {
					'Name': json.dumps({
						'text': self.name
					})
				}
			}
		}
		if hasattr(self, 'slot'):
			ret['Slot'] = self.slot
		if hasattr(self, 'count'):
			ret['Count'] = self.count
		return ret


class Shulker(Serializable):
	items: List[Item] = []

	def to_give_command(self) -> str:
		nbt = {
			'BlockEntityTag': {
				'Items': list(map(lambda item: item.to_dict(), self.items))
			}
		}
		return '/give @p minecraft:shulker_box{}'.format(json.dumps(nbt))


class Sheet:
	def __init__(self):
		self.shulkers: List[Shulker] = []
		self.pending_items: List[Item] = []

	def __add_shulker(self, items: List[Item]):
		assert len(items) <= 27
		shulker = Shulker.get_default()
		for i, item in enumerate(items):
			shulker.items.append(Item(
				id=item.id,
				count=item.count,
				name=item.name,
				slot=i
			))
		self.shulkers.append(shulker)

	def add_item(self, item: Item):
		if len(self.pending_items) > 0:
			last_one = self.pending_items[-1]
			if last_one.id == item.id:
				if last_one.count + item.count <= 64:
					last_one.count += item.count
				else:
					print('WARN: {} has >64 count'.format(last_one.id))
				return
		self.pending_items.append(item)
		if len(self.pending_items) > 27:
			self.__add_shulker(self.pending_items[:27])
			self.pending_items = self.pending_items[27:]

	def done(self):
		self.__add_shulker(self.pending_items)
		self.pending_items.clear()
