import sublime, sublime_plugin
import time
import re

from datetime import datetime

class manager():
	timer_dicts = {}

	BEGIN = 0
	DURATION = 0

	DATETIME_FORMAT = '%H:%M:%S'

	def start(self, name):
		name = self.__filter_name(name)
		timer_dicts = self.timer_dicts

		if name not in timer_dicts:
			timer_dicts[name] = [self.__create_timer()]

		timers = timer_dicts[name]
		timer_last = timers[-1]

		if self.__is_timer_started(timer_last):
			sublime.status_message('Timer `' + name + '` already started')
		else:
			timer_new = self.__start_timer(self.__create_timer())
			timers.append(timer_new)
			sublime.status_message('Begin timer `' + name + '` ')

	def stop(self, name):
		name = self.__filter_name(name)
		timer_dicts = self.timer_dicts

		if name not in timer_dicts:
			sublime.status_message('Unknown timer `' + name + '` ')
			return None

		timers = timer_dicts[name]
		timer_last = timers[-1]

		if self.__is_timer_started(timer_last):
			timers[-1] = self.__stop_timer(timer_last)
			sublime.status_message('Stop timer `' + name + '` ')
		else:
			sublime.status_message('Timer `' + name + '` is not started')

	def delete(self, name):
		name = self.__filter_name(name)
		timer_dicts = self.timer_dicts

		if name in timer_dicts:
			del timer_dicts[name]



	def list(self):
		items = []
		for name in self.timer_dicts.keys():
			item = [name]
			timers = self.timer_dicts[name]
			timer_last = timers[-1]

			duration_all = 0
			for timer in timers:
				begin, duration = timer
				if self.__is_timer_started(timer):
					duration_all += time.time() - begin
				else:
					duration_all += duration

			line_second = ''
			started = self.__is_timer_started(timer_last)
			if started:
				line_second = 'Started'
			else:
				line_second = 'Stopped'

			if duration_all != 0:
				dt = datetime.utcfromtimestamp(duration_all).__format__(self.DATETIME_FORMAT)
				if started:
					line_second += ' before ' + dt
				else:
					line_second += '. Duration: ' + dt

			if line_second != '':
				item.append(line_second)

			items.append(item)

		return items

	def __create_timer(self):
		return (self.BEGIN, self.DURATION)

	def __start_timer(self, timer):
		begin, duration = timer
		return (time.time(), duration)

	def __is_timer_started(self, timer):
		begin, duration = timer
		return begin != 0 and duration == 0

	def __stop_timer(self, timer):
		begin, duration = timer
		now = time.time()

		duration_new = now - begin + duration
		return (begin, duration_new)

	def __filter_name(self, name):
		if type(name) == list:
			return name[0]
		else:
			return name

man = manager()

class stt_start_timer_command(sublime_plugin.WindowCommand):

	def run(self):
		self.messages = ['New timer...'] + man.list()
		self.window.show_quick_panel(self.messages, self.select)

	def select(self, index):
		if index == 0:
			self.window.show_input_panel('Timer Name', '', self.create, None, None)
		else:
			if index > 0:
				msg = self.messages[index]
				man.start(msg)

	def create(self, name):
		man.start(name)

class stt_stop_timer_command(sublime_plugin.WindowCommand):

	def run(self):
		self.messages = ['Nothing to stop'] + man.list()
		self.window.show_quick_panel(self.messages, self.select)

	def select(self, index):
		if index > 0:
			msg = self.messages[index]
			man.stop(msg)

class stt_delete_timer_command(sublime_plugin.WindowCommand):

	def run(self):
		self.messages = ['Nothing to delete'] + man.list()
		self.window.show_quick_panel(self.messages, self.select)

	def select(self, index):
		if index > 0:
			msg = self.messages[index]
			man.delete(msg)

