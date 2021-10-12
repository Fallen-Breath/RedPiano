import json
from typing import List

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


class ShulkerSheetStorage:
	def __init__(self):
		self.__shulkers: List[Shulker] = []
		self.__pending_items: List[Item] = []

	def __add_shulker(self, items: List[Item]):
		assert len(items) <= 27
		if len(items) == 0:
			return
		shulker = Shulker.get_default()
		for i, item in enumerate(items):
			shulker.items.append(Item(
				id=item.id,
				count=item.count,
				name=item.name,
				slot=i
			))
		self.__shulkers.append(shulker)

	def add_item(self, item: Item):
		if len(self.__pending_items) > 0:
			last_one = self.__pending_items[-1]
			if last_one.id == item.id:
				if last_one.count + item.count <= 64:
					last_one.count += item.count
				else:
					print('WARN: {} has >64 count'.format(last_one.id))
				return
		self.__pending_items.append(item)
		if len(self.__pending_items) > 27:
			self.__add_shulker(self.__pending_items[:27])
			self.__pending_items = self.__pending_items[27:]

	def done_and_export(self) -> List[str]:
		self.__add_shulker(self.__pending_items)
		self.__pending_items.clear()
		return [shulker.to_give_command() for shulker in self.__shulkers]

