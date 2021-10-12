import collections
from enum import Enum
from typing import Optional, List, Dict

from symbol import NoteBlockSymbol, SheetSymbol
from track import Track, TrackItem, TimeMark


class RhythmMode(Enum):
	short_tone = '短音'
	long_tone = '长音'

	@classmethod
	def guess_line(cls, line: str) -> Optional['RhythmMode']:
		for tone in cls:
			if tone.value in line:
				return tone
		return None


class Sheet:
	def __init__(self, base_tonality: NoteBlockSymbol, rhythm_mode: RhythmMode, data_line: str):
		self.base_tonality: NoteBlockSymbol = base_tonality  # 调性
		self.rhythm_mode: RhythmMode = rhythm_mode
		self.data_line = data_line
		self.symbol_containers: List[List[NoteBlockSymbol]] = []

	@classmethod
	def load(cls, content: str) -> 'Sheet':
		tonality = None
		rhythm_mode = RhythmMode.short_tone
		data_line = ''
		for line in content.splitlines():
			if line.upper().startswith('1='):
				tonality = NoteBlockSymbol.ofTonality(line[2:])
			rm = RhythmMode.guess_line(line)
			if rm is not None:
				rhythm_mode = rm
			if line.startswith('|'):
				data_line += line
		if tonality is None:
			raise Exception('缺失音调基准')
		return Sheet(tonality, rhythm_mode, data_line)

	def process_data(self):
		print('音调基准: 1 = {}'.format(self.base_tonality))
		print('节奏模式: {}'.format(self.rhythm_mode.value))
		data = self.data_line.replace('|', '')
		prev_symbols = None
		for segment in data.split(' '):
			if not segment:
				continue
			symbols: List[SheetSymbol] = []
			if segment == '-':
				if self.rhythm_mode == RhythmMode.short_tone:
					symbols = [SheetSymbol.empty()]
				else:
					assert prev_symbols is not None and len(prev_symbols) == 1, '延音符前需要是一个四分音符，但前面却是{}'.format(prev_symbols)
					symbols = prev_symbols.copy()
			else:
				while len(segment) > 0:
					try:
						sheet_symbol, segment = SheetSymbol.read(segment)
					except Exception as e:
						raise ValueError('Failed to read SheetSymbol from {}: {}'.format(segment, e))
					symbols.append(sheet_symbol)
			assert len(symbols) in [1, 2, 4], '空格之间的简谱音符个数{}不合法'.format(len(symbols))
			prev_symbols = symbols
			noteblock_symbol_list: List[NoteBlockSymbol] = []
			for sheet_symbol in symbols:
				if sheet_symbol.is_empty():
					noteblock_symbol = NoteBlockSymbol.empty()
				else:
					delta = sheet_symbol.get_delta()
					try:
						noteblock_symbol = self.base_tonality.shift(delta, clamp=False)
					except ValueError:
						noteblock_symbol = self.base_tonality.shift(delta, clamp=True)
						print('[警告] 简谱音符{}偏移{}后超出音符盒音符范围，使用边界值{}近似替代'.format(sheet_symbol, delta, noteblock_symbol))
				noteblock_symbol_list.append(noteblock_symbol)
			self.symbol_containers.append(noteblock_symbol_list)

	def process_time_mark(self):
		tracks: List[Track] = []
		for idx, symbols in enumerate(self.symbol_containers):
			required_items = []

			def append(idx: int, mark: str):
				required_items.append(TrackItem(symbols[idx], TimeMark.of(mark)))

			# 若只有一个数字 - 四分音符
			if len(symbols) == 1:
				if self.rhythm_mode == RhythmMode.long_tone:  # 长音
					append(0, '1111')
				else:  # 短音
					append(0, '1000')
			# 若有两个数字 - 两个八分音符
			elif len(symbols) == 2:
				# 若两个数字表示的音符相同
				if symbols[0] == symbols[1]:
					if self.rhythm_mode == RhythmMode.long_tone:  # 长音
						append(0, '1111')
					else:  # 短音
						append(0, '1010')
				# 若两个数字表示的音符不同
				else:
					if self.rhythm_mode == RhythmMode.long_tone:  # 长音
						append(0, '1100')
						append(1, '0011')
					else:  # 短音
						append(0, '1000')
						append(1, '0010')
			# 若有四个数字 - 四个十六分音符
			elif len(symbols) == 4:
				symbol2times: Dict[NoteBlockSymbol, int] = collections.defaultdict(lambda: TimeMark.of('0000'))
				symbol2times[symbols[0]] |= TimeMark.of('1000')
				symbol2times[symbols[1]] |= TimeMark.of('0100')
				symbol2times[symbols[2]] |= TimeMark.of('0010')
				symbol2times[symbols[3]] |= TimeMark.of('0001')
				for symbol, time_mark in symbol2times.items():
					required_items.append(TrackItem(symbol, time_mark))

			if len(tracks) < len(required_items):
				for i in range(len(required_items) - len(tracks)):
					track = Track()
					for j in range(idx):
						track.append(TrackItem.empty())
					tracks.append(track)
			for i in range(len(tracks)):
				item = required_items[i] if i < len(required_items) else TrackItem.empty()
				tracks[i].append(item)

		print('共需要{}条音轨'.format(len(tracks)))
		for i, track in enumerate(tracks):
			print('音轨#{}'.format(i))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.symbol), track)))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.time), track)))


if __name__ == '__main__':
	sheet = Sheet.load(open('input.txt', encoding='utf8').read())
	sheet.process_data()
	sheet.process_time_mark()
