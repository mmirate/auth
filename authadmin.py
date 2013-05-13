#!/usr/bin/env python3

# This script is intended to be used only from within a session of an editor's GPG plugin (e.g. gnupg.vim); some subcommands produce a complete plaintext from the on-disk ciphertext.

import collections,auth,operator,urllib.parse

from sorted_yaml_representer import yaml, sort_credential, sort_credentials

def alistFromDict(d):
	try:
		return list(d.items())
	except NameError:
		return d

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 1 or sys.argv[1] == 'sort':
		auth.write(auth.read())
	elif sys.argv[1] == 'frequency':
		distributions = collections.OrderedDict()
		for key,func in {"password":lambda x:x,"username":lambda x:x,"url":lambda x:urllib.parse.urlparse(x,scheme='http').scheme}.items():
			distributions[key] = collections.Counter(map(lambda x: func(x[key]),filter(bool,filter(lambda x: x and key in x and x[key],auth.getcredentials()))))
		print(yaml.dump(distributions,default_flow_style=False))

