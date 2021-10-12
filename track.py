from typing import List

from symbol import NoteBlockSymbol


class TimeMark:
	@classmethod
	def is_valid(cls, value: int) -> bool:
		return 0 <= value <= 15

	@classmethod
	def of(cls, text: str) -> int:
		value = int(text, 2)
		assert cls.is_valid(value)
		return value


class TrackItem:
	symbol: NoteBlockSymbol
	__time_mark: int

	def __init__(self, symbol: NoteBlockSymbol, time_mark: int):
		self.symbol = symbol
		assert TimeMark.is_valid(time_mark)
		self.__time_mark = time_mark

	@property
	def time(self) -> str:
		return bin(self.__time_mark)[2:].rjust(4, '0')

	@classmethod
	def empty(cls) -> 'TrackItem':
		return TrackItem(NoteBlockSymbol.empty(), 0)

	def __str__(self):
		return '{}@{}'.format(self.symbol, self.time)


class Track(List[TrackItem]):
	pass
