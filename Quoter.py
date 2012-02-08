import sublime, sublime_plugin
import uuid, re

def enclose_region(view, edit, region, enc_string):
	sel_str = view.substr(region)
	view.replace(edit, region, '%s%s%s' % (enc_string, sel_str, enc_string))

def trim_region(view, region):
	sel_str = view.substr(region)
	a, b  = region.begin(), region.end()

	whitespace = [' ','\t']

	while view.substr(a) in whitespace: 
		a += 1
		print "a=", a
	while view.substr(b-1) in whitespace: 
		b -= 1
		print "b=", b

	return sublime.Region(a,b)

class QuoterCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sels = self.view.sel()
		for sel in sels:
			enclose_region(self.view, edit, sel, '"')


class EraseTrailingWhitespaceCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		trailing_white_space = view.find_all("[\t ]+$")
		trailing_white_space.reverse()
		edit = view.begin_edit()
		for r in trailing_white_space:
		    view.erase(edit, r)
		view.end_edit(edit)

def leading_tab_count(str):
	match = re.search("^(\\t+).*$",str)
	matched_string = match.group(1) if match else ''
	return len( matched_string)


class TabToLineCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		new_sels = set()
		for sel in self.view.sel():
			lines = self.view.lines(sel)
			prev_line = self.view.line(lines[0].begin()-1)
			#print "prev_line: region=", prev_line, " line=", self.view.substr(prev_line)

			number_of_tabs = leading_tab_count(self.view.substr(prev_line))

			offset = 0
			for line in lines:
				corrected_line = sublime.Region(line.begin() + offset, line.end() + offset)
				corrected_line_str = self.view.substr(corrected_line)

				additional_tabs = number_of_tabs - leading_tab_count(corrected_line_str)

				new_line_str = '\t'*additional_tabs + corrected_line_str
				self.view.replace(edit, corrected_line, new_line_str)

				offset += len(new_line_str) - len(corrected_line_str)
			
			new_sels.add(sublime.Region(sel.begin(), sel.end() + offset))

		self.view.sel().clear()
		for new_sel in new_sels:
			self.view.sel().add(new_sel)			



class QuotelinesCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sels = self.view.sel()
		for sel in sels:
			lines = self.view.lines(sel)

			i = 0
			quote_str = '"'
			quote_length = len(quote_str) * 2 # because we add quote line 2 times
			for line in lines:
				offset = i * quote_length
				#print "i=",i," offset=", offset
				region = sublime.Region(line.begin() + offset, line.end() + offset)
				#print "line=", line, " region=", region
				region = trim_region(self.view, region)
				enclose_region(self.view, edit, region, quote_str)
				i += 1
			
			self.view.sel().subtract(sel)
			self.view.sel().add(sublime.Region(sel.begin(), sel.end() + len(lines) * quote_length))





class UuidCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		uuid_str = str(uuid.uuid4())
		self.view.insert(edit, self.view.sel()[0].begin(), uuid_str)
