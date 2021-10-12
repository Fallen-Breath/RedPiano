import collections
from enum import Enum
from typing import Optional, List, Dict

from item import ShulkerSheetStorage
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
		self.tracks: List[Track] = []

	@classmethod
	def load(cls, content: str) -> 'Sheet':
		tonality = None
		rhythm_mode = RhythmMode.short_tone
		data_line = ''
		for line in content.upper().splitlines():
			if line.startswith('1='):
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
		warn_count = 0
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
						warn_count += 1
				noteblock_symbol_list.append(noteblock_symbol)
			self.symbol_containers.append(noteblock_symbol_list)
		print('翻译后音符序列:')
		print(' '.join(map(lambda lst: '({})'.format(' '.join(map(str, lst))), self.symbol_containers)))
		if warn_count > 0:
			print('##################')
			print('>>> 警告: {}个 <<<'.format(warn_count))
			print('##################')

	def process_time_mark(self):
		tracks: List[Track] = []
		for idx, symbols in enumerate(self.symbol_containers):
			required_items = []
			symbol2times: Dict[NoteBlockSymbol, int] = collections.defaultdict(lambda: TimeMark.of('0000'))
			seg_len = {1: 4, 2: 2, 4: 1}[len(symbols)]
			for i, symbol in enumerate(symbols):
				len_1 = 1 if self.rhythm_mode == RhythmMode.short_tone else seg_len
				len_prev_0 = seg_len * i
				marker_text = ('0' * len_prev_0 + '1' * len_1).ljust(4, '0')
				symbol2times[symbol] |= TimeMark.of(marker_text)
			for symbol, time_mark in symbol2times.items():
				if symbol != NoteBlockSymbol.empty():
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

		self.tracks = tracks
		print()
		print('====== 音轨预览 ====== ')
		print('共需要{}条音轨'.format(len(tracks)))
		for i, track in enumerate(tracks):
			print('音轨#{}'.format(i + 1))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.symbol).rjust(2, ' ').ljust(4, ' '), track)))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.time), track)))

	def generate_command(self):
		print()
		print('====== 指令输出 ====== ')
		for i, track in enumerate(self.tracks):
			print('音轨#{}'.format(i + 1))
			storage_symbol = ShulkerSheetStorage('音轨#{}音符序列'.format(i + 1))
			storage_time_mark = ShulkerSheetStorage('音轨#{}节奏序列'.format(i + 1))
			for track_item in track:
				storage_symbol.add_item(track_item.to_items()[0])
				storage_time_mark.add_item(track_item.to_items()[1])
			storage_symbol.done()
			storage_time_mark.done()
			cmd_s = storage_symbol.export_give_chest_command()
			cmd_t = storage_time_mark.export_give_chest_command()
			print('  音符序列需要{}个潜影盒:'.format(len(storage_symbol.export_give_command())))
			for cmd in cmd_s:
				print('\t{}'.format(cmd))
			print('  节奏序列需要{}个潜影盒:'.format(len(storage_time_mark.export_give_command())))
			for cmd in cmd_t:
				print('\t{}'.format(cmd))
