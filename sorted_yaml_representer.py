import yaml, collections

def get_url(doc):
	try: return doc["url"]
	except KeyError: return ""

sort_credentials = lambda docs: sorted(docs,key=get_url)

def sort_credential(cred):
	c = collections.OrderedDict()
	if "url" in c:
		c["url"] = cred["url"]
		c["password"] = cred["password"]
	if cred: c.update(cred)
	return c

# Copyright for the remainder of this file is as follows:
#
# Copyright (c) 2006 Kirill Simonov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def represent_ordered_mapping(self, tag, mapping, flow_style=None):
	value = []
	node = yaml.nodes.MappingNode(tag, value, flow_style=flow_style)
	if self.alias_key is not None:
		self.represented_objects[self.alias_key] = node
	best_style = True
	if hasattr(mapping, 'items'):
		mapping = list(mapping.items())
		#try:
		#	mapping = sorted(mapping)
		#except TypeError:
		#	pass
	for item_key, item_value in mapping:
		node_key = self.represent_data(item_key)
		node_value = self.represent_data(item_value)
		if not (isinstance(node_key, yaml.nodes.ScalarNode) and not node_key.style):
			best_style = False
		if not (isinstance(node_value, yaml.nodes.ScalarNode) and not node_value.style):
			best_style = False
		value.append((node_key, node_value))
	if flow_style is None:
		if self.default_flow_style is not None:
			node.flow_style = self.default_flow_style
		else:
			node.flow_style = best_style
	return node

def represent_value_ordered_mapping(self, tag, mapping, flow_style=None):
	value = []
	node = yaml.nodes.MappingNode(tag, value, flow_style=flow_style)
	if self.alias_key is not None:
		self.represented_objects[self.alias_key] = node
	best_style = True
	if hasattr(mapping, 'items'):
		mapping = list(mapping.items())
		try:
			mapping = sorted(mapping,key=operator.itemgetter(1),reverse=True)
		except TypeError:
			pass
	for item_key, item_value in mapping:
		node_key = self.represent_data(item_key)
		node_value = self.represent_data(item_value)
		if not (isinstance(node_key, yaml.nodes.ScalarNode) and not node_key.style):
			best_style = False
		if not (isinstance(node_value, yaml.nodes.ScalarNode) and not node_value.style):
			best_style = False
		value.append((node_key, node_value))
	if flow_style is None:
		if self.default_flow_style is not None:
			node.flow_style = self.default_flow_style
		else:
			node.flow_style = best_style
	return node

def represent_ordered_dict(self, data):
	return represent_ordered_mapping(self, 'tag:yaml.org,2002:map', data)

def represent_value_ordered_dict(self, data):
	return represent_value_ordered_mapping(self, 'tag:yaml.org,2002:map', data)

yaml.add_representer(collections.OrderedDict,represent_ordered_dict)
yaml.add_representer(collections.Counter,represent_value_ordered_dict)


