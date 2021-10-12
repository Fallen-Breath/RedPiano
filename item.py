import json
from abc import ABC
from typing import List, Optional

from serializer import Serializable


class Item(Serializable):
	id: str
	name: str
	count: Optional[str] = None
	slot: Optional[str] = None

	def to_dict(self) -> dict:
		tags = {}
		self.append_name_tag(tags)
		self.append_block_entity_tag(tags)
		ret = {
			'id': self.id,
			'tag': tags
		}
		if self.slot is not None:
			ret['Slot'] = self.slot
		if self.count is not None:
			ret['Count'] = self.count
		return ret

	def append_name_tag(self, tags: dict):
		if self.name is not None:
			tags['display'] = {
				'Name': json.dumps({'text': self.name}, ensure_ascii=False)
			}

	def append_block_entity_tag(self, tags: dict):
		pass


class Container(Item, ABC):
	items: List[Item] = []
	name: Optional[str] = None

	def to_give_command(self) -> str:
		nbt = {}
		self.append_name_tag(nbt)
		self.append_block_entity_tag(nbt)
		return '/give @p {}{}'.format(self.id, json.dumps(nbt, ensure_ascii=False))

	def append_block_entity_tag(self, tags: dict):
		tags['BlockEntityTag'] = {
			'Items': list(map(lambda item: item.to_dict(), self.items))
		}


class Shulker(Container):
	id: str = 'minecraft:shulker_box'


class Chest(Container):
	id: str = 'minecraft:chest'


class ShulkerSheetStorage:
	def __init__(self, name: Optional[str] = None):
		self.name = name
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

	def done(self) -> List[str]:
		self.__add_shulker(self.__pending_items)
		self.__pending_items.clear()
		return [shulker.to_give_command() for shulker in self.__shulkers]

	def export_give_command(self) -> List[str]:
		return [shulker.to_give_command() for shulker in self.__shulkers]

	def export_give_chest_command(self) -> List[str]:
		chests: List[Chest] = []
		chest: Optional[Chest] = None
		for i, shulker in enumerate(self.__shulkers):
			if chest is None:
				chest = Chest.get_default()
				chest.name = self.name
			shulker.slot = i
			shulker.count = 1
			chest.items.append(shulker)
			if len(chest.items) == 27:
				chests.append(chest)
				chest = None
		if chest is not None:
			chests.append(chest)
		return [chest.to_give_command() for chest in chests]

