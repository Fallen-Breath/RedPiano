from typing import Dict, Tuple, Optional


class NoteBlockSymbol:
	note: int

	__MAPPING: Dict[int, str] = {0: 'F#', 1: 'G', 2: 'G#', 3: 'A', 4: 'A#', 5: 'B', 6: 'C', 7: 'C#', 8: 'D', 9: 'D#', 10: 'E', 11: 'F', 12: 'F#', 13: 'G', 14: 'G#', 15: 'A', 16: 'A#', 17: 'B', 18: 'C', 19: 'C#', 20: 'D', 21: 'D#', 22: 'E', 23: 'F', 24: 'F#'}

	def __init__(self, note: int):
		assert -1 <= note <= 24
		self.note = note
		self.symbol = self.__MAPPING.get(self.note)

	def __str__(self):
		return '{}_{}'.format(self.note, self.symbol) if not self.is_empty() else 'X'

	def __eq__(self, other):
		return isinstance(other, type(self)) and self.note == other.note

	def __hash__(self):
		return hash(self.note)

	def is_empty(self) -> bool:
		return self.note == -1

	@classmethod
	def __is_valid_note(cls, note: int) -> bool:
		return 0 <= note <= 24

	@classmethod
	def of(cls, note: int) -> 'NoteBlockSymbol':
		assert isinstance(note, int)
		if cls.__is_valid_note(note):
			return NoteBlockSymbol(note=note)
		else:
			raise ValueError('Unknown note {}'.format(note))

	@classmethod
	def ofTonality(cls, symbol: str) -> 'NoteBlockSymbol':
		mapping: Dict[str, int] = dict([(v, k) for k, v in cls.__MAPPING.items() if 3 <= k <= 14])
		return cls.of(mapping[symbol])

	def shift(self, other: int, clamp: bool) -> 'NoteBlockSymbol':
		assert isinstance(other, int)
		new_note = self.note + other
		if not self.__is_valid_note(new_note) and clamp:
			new_note = max(0, min(24, new_note))
		return self.of(new_note)

	@classmethod
	def empty(cls) -> 'NoteBlockSymbol':
		return cls(-1)


class SheetSymbol:
	note: int  # 0, 1 ~ 7
	prefix: str  # 数字前的升降记号   #b
	suffix: str  # 数字后的跨八度符号 ,'

	__NOTE_DELTA: Dict[int, int] = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}

	def __init__(self, note: int, prefix: str, suffix: str):
		self.note = note
		self.prefix = prefix
		self.suffix = suffix

	def __str__(self):
		return '{}{}{}'.format(self.prefix, self.note, self.suffix)

	@classmethod
	def read(cls, text: str, prev_symbol: Optional['SheetSymbol'] = None) -> Tuple['SheetSymbol', str]:
		prefix = ''
		suffix = ''
		if not text[0].isdigit():
			prefix = text[0]
			text = text[1:]
			if prefix == '-':
				assert prev_symbol is not None, '延音符前方未找到音符'
				return prev_symbol, text
			assert prefix in '#B', '非法升降记号前缀{}'.format(prefix)
		assert len(text) > 0 and text[0].isdigit(), '剩余字符串{}首字母不是数字'.format(text)
		note = int(text[0])
		text = text[1:]
		assert 0 <= note <= 7, '简谱数字{}超出了0~7范围'.format(note)
		if len(text) > 0 and text[0] in ",'":
			suffix = text[0]
			text = text[1:]
		return cls(note, prefix, suffix), text

	@classmethod
	def of(cls, text: str) -> 'SheetSymbol':
		inst, rest = cls.read(text)
		assert len(rest) == 0
		return inst

	@classmethod
	def empty(cls) -> 'SheetSymbol':
		return cls.of('0')

	def is_empty(self) -> bool:
		return self.note == 0

	def get_delta(self) -> int:
		assert not self.is_empty()
		delta = self.__NOTE_DELTA[self.note]
		if self.prefix == '#':
			delta += 1
		elif self.prefix == 'B':
			delta -= 1
		if self.suffix == "'":
			delta += 12
		elif self.suffix == ',':
			delta -= 12
		return delta
