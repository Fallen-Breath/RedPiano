import os
import sys
import traceback
from contextlib import contextmanager

from item import ShulkerSheetStorage
from sheet import Sheet
from symbol import NoteBlockSymbol
from track import RedPianoTrackItem


def dump_items():
	storage = ShulkerSheetStorage('音符序列模板盒')
	for i in range(25):
		storage.add_item(RedPianoTrackItem(NoteBlockSymbol.of(i), 0).to_items()[0])
	storage.add_item(RedPianoTrackItem(NoteBlockSymbol.empty(), 0).to_items()[0])
	storage.done()
	print('音符序列模板盒')
	print('\n'.join(storage.export_give_command()))

	storage = ShulkerSheetStorage('时间序列模板盒')
	for i in range(16):
		storage.add_item(RedPianoTrackItem(NoteBlockSymbol.empty(), i).to_items()[1])
	storage.done()
	print('时间序列模板盒')
	print('\n'.join(storage.export_give_command()))
	print()


def main():
	if not os.path.isfile('input.txt'):
		print('输入文件"input.txt"未找到')
		return
	with open('input.txt', encoding='utf8') as f:
		sheet = Sheet.load(f.read())
	sheet.process_data()
	sheet.process_time_mark()
	sheet.generate_command()


class FakeStdOut(object):
	def __init__(self):
		self.terminal = sys.stdout
		open('output.txt', 'w').close()

	def write(self, message):
		self.terminal.write(message)
		with open('output.txt', 'a', encoding='utf8') as f:
			f.write(message)

	@classmethod
	@contextmanager
	def wrap(cls):
		wrapper = FakeStdOut()
		sys.stdout = wrapper
		try:
			yield
		finally:
			sys.stdout = wrapper.terminal


if __name__ == '__main__':
	with FakeStdOut.wrap():
		try:
			# dump_items()
			main()
		except:
			traceback.print_exc()
			print('漏虫了，可能是输入有虫，也有可能是程序有虫，看看上面说啥')
	print()
	print('程序的输出文本也可在output.txt中找到')
	input('按回车退出程序...')
