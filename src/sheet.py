import collections
from enum import Enum
from typing import Optional, List, Dict, NamedTuple

from item import ShulkerSheetStorage
from symbol import NoteBlockSymbol, SheetSymbol
from track import RedPianoTrack, RedPianoTrackItem, TimeMark


class RhythmMode(Enum):
	short_tone = '短音'
	long_tone = '长音'

	@classmethod
	def guess_line(cls, line: str) -> Optional['RhythmMode']:
		for tone in cls:
			if tone.value in line:
				return tone
		return None


# | 12 34 5 0 |
#   12 <-- Segment
# 音段
class Segment(NamedTuple):
	text: str
	base_tonality: NoteBlockSymbol


NoteBlockSymbolTrack = List[List[NoteBlockSymbol]]  # 音段 - 音符


class Sheet:
	def __init__(self, rhythm_mode: RhythmMode, segments_list: List[List[Segment]]):
		self.rhythm_mode: RhythmMode = rhythm_mode
		self.segments_list: List[List[Segment]] = segments_list
		self.noteblock_tracks: List[NoteBlockSymbolTrack] = []
		self.red_tracks: List[RedPianoTrack] = []

	@classmethod
	def load(cls, content: str) -> 'Sheet':
		segments_list: Dict[int, List[Segment]] = collections.defaultdict(list)
		tonality = None
		rhythm_mode = RhythmMode.short_tone
		segments_id = 0
		for line in content.upper().splitlines():
			if '//' in line:
				line = line.split('//')[0]
			if line.startswith('1='):
				tonality = NoteBlockSymbol.ofTonality(line[2:])
			rm = RhythmMode.guess_line(line)
			if rm is not None:
				rhythm_mode = rm
			if line.startswith('|'):
				assert tonality is not None, '音高基准未声明，无法输入简谱音轨'
				segments: List[Segment] = []
				for segment in line.replace('|', '').replace('\t', ' ').split(' '):
					if len(segment) > 0:
						segments.append(Segment(segment, tonality))
				segments_list[segments_id].extend(segments)
				segments_id += 1
			# 多个简谱音轨间用空行隔开
			elif len(line) == 0:
				segments_id = 0
		assert len(segments_list) > 0, '未找到简谱音轨'
		len_ = len(segments_list[0])
		assert all(map(lambda lst: len(lst) == len_, segments_list.values())), '存在长度不一致的简谱音轨。简谱音轨长度列表为：{}'.format(' ,'.join(map(str, map(len, segments_list.values()))))
		print('成功读取{}条简谱音轨，长度为{}'.format(len(segments_list), len_))
		return Sheet(rhythm_mode, list(segments_list.values()))

	@property
	def segment_amount(self) -> int:
		return len(self.segments_list[0])

	def process_data(self):
		print('节奏模式: {}'.format(self.rhythm_mode.value))
		prev_symbols: Optional[List[SheetSymbol]] = None
		warn_count = 0
		for segments in self.segments_list:
			noteblock_track: NoteBlockSymbolTrack = []
			for segment in segments:
				symbols: List[SheetSymbol] = []
				prev_symbol: SheetSymbol
				if self.rhythm_mode == RhythmMode.long_tone:
					prev_symbol = prev_symbols[-1] if prev_symbols is not None and len(prev_symbols) > 0 else None
				else:
					prev_symbol = SheetSymbol.empty()
				text = segment.text
				while len(text) > 0:
					try:
						sheet_symbol, text = SheetSymbol.read(text, prev_symbol)
					except Exception as e:
						raise ValueError('从{}读取简谱音符失败: {}'.format(text, e))
					if self.rhythm_mode == RhythmMode.long_tone:
						prev_symbol = sheet_symbol
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
							noteblock_symbol = segment.base_tonality.shift(delta, clamp=False)
						except ValueError:
							noteblock_symbol = segment.base_tonality.shift(delta, clamp=True)
							print('[警告] 简谱音符{}于基调{}偏移{}后超出音符盒音符范围，使用边界值{}近似替代'.format(sheet_symbol, segment.base_tonality, delta, noteblock_symbol))
							warn_count += 1
					noteblock_symbol_list.append(noteblock_symbol)
				noteblock_track.append(noteblock_symbol_list)
			self.noteblock_tracks.append(noteblock_track)
		print('翻译后音符序列:')
		for i, track in enumerate(self.noteblock_tracks):
			print('简谱音轨#{}: '.format(i + 1) + ' '.join(map(lambda lst: '({})'.format(' '.join(map(str, lst))), track)))
		if warn_count > 0:
			print('##################')
			print('>>> 警告: {}个 <<<'.format(warn_count))
			print('##################')

	def process_time_mark(self):
		red_tracks: List[RedPianoTrack] = []
		for idx in range(self.segment_amount):
			required_items = []
			symbol2times: Dict[NoteBlockSymbol, int] = collections.defaultdict(lambda: TimeMark.of('0000'))
			for track in self.noteblock_tracks:
				symbols: List[NoteBlockSymbol] = track[idx]
				seg_len = {1: 4, 2: 2, 4: 1}[len(symbols)]
				for i, symbol in enumerate(symbols):
					len_1 = 1 if self.rhythm_mode == RhythmMode.short_tone else seg_len
					len_prev_0 = seg_len * i
					marker_text = ('0' * len_prev_0 + '1' * len_1).ljust(4, '0')
					symbol2times[symbol] |= TimeMark.of(marker_text)

			for symbol, time_mark in symbol2times.items():
				if symbol != NoteBlockSymbol.empty():
					required_items.append(RedPianoTrackItem(symbol, time_mark))

			if len(red_tracks) < len(required_items):
				for i in range(len(required_items) - len(red_tracks)):
					track = RedPianoTrack()
					for j in range(idx):
						track.append(RedPianoTrackItem.empty())
					red_tracks.append(track)
			for i in range(len(red_tracks)):
				item = required_items[i] if i < len(required_items) else RedPianoTrackItem.empty()
				red_tracks[i].append(item)

		self.red_tracks = red_tracks
		print()
		print('====== 音轨分析 ====== ')
		print('共需要{}条红乐音轨'.format(len(red_tracks)))
		for i, track in enumerate(red_tracks):
			print('红乐音轨#{}'.format(i + 1))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.symbol).rjust(2, ' ').ljust(4, ' '), track)))
			print('  ' + ' '.join(map(lambda track_item: str(track_item.time), track)))

	def generate_command(self):
		print()
		print('====== 指令输出 ====== ')
		for i, track in enumerate(self.red_tracks):
			print('> 红乐音轨#{}'.format(i + 1))
			storage_symbol = ShulkerSheetStorage('音轨#{}音符序列'.format(i + 1))
			storage_time_mark = ShulkerSheetStorage('音轨#{}节奏序列'.format(i + 1))
			for track_item in track:
				storage_symbol.add_item(track_item.to_items()[0])
				storage_time_mark.add_item(track_item.to_items()[1])
			storage_symbol.done()
			storage_time_mark.done()
			cmd_s = storage_symbol.export_give_chest_command()
			cmd_t = storage_time_mark.export_give_chest_command()
			print('音符序列需要{}个潜影盒:'.format(len(storage_symbol.export_give_command())))
			print('\n'.join(cmd_s))
			print('节奏序列需要{}个潜影盒:'.format(len(storage_time_mark.export_give_command())))
			print('\n'.join(cmd_t))
			print()
