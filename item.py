import json
from abc import ABC
from typing import List, Optional

from serializer import Serializable


def to_json_str(data) -> str:
	return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


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
				'Name': to_json_str(self.name)
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
		return '/give @p {}{}'.format(self.id, to_json_str(nbt))

	def add_item(self, item: Item):
		item.slot = len(self.items)
		self.items.append(item)

	def append_block_entity_tag(self, tags: dict):
		tags['BlockEntityTag'] = {
			'Items': list(map(lambda item: item.to_dict(), self.items))
		}


class Shulker(Container):
	id: str = 'minecraft:shulker_box'


class Chest(Container):
	id: str = 'minecraft:chest'


CMD_BLOCK_LIMIT = 32000  # real value: 32500


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
		for item in items:
			shulker.add_item(Item(
				id=item.id,
				count=item.count,
				name=item.name
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
		def get_chest():
			nonlocal chest, chest_cnt
			if chest is not None:
				chest.name += str(chest_cnt)
			chest = Chest.get_default()
			chests.append(chest)
			chest_cnt += 1
			chest.name = self.name
			if chest_cnt > 1:
				chest.name += str(chest_cnt)

		chests: List[Chest] = []
		chest: Optional[Chest] = None
		chest_cnt = 0
		for i, shulker in enumerate(self.__shulkers):
			if chest is None:
				get_chest()
			shulker.count = 1
			chest.add_item(shulker)
			if len(chest.to_give_command()) > CMD_BLOCK_LIMIT:
				chest.items.pop(len(chest.items) - 1)
				get_chest()
				chest.add_item(shulker)
			if len(chest.items) == 27:
				chest = None
		return [chest.to_give_command() for chest in chests]
