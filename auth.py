#!/usr/bin/env python

from __future__ import print_function
import six, subprocess, plumbum, os, json, re, sys
import gnupg
#import plac # someday ... I might get around to using this ...
#from plumbum.cmd import getdisplay, tty, sponge

for n in filter(lambda x: x.split(' ')[0] == 'add_to_path',open(os.path.expanduser('~/.profile'))):
	plumbum.local.env.path.append(os.path.expanduser(n.split(' ')[1].strip()))

for n in 'getdisplay, tty'.split(', '):
	globals()[n] = plumbum.local[plumbum.local.which(n)]

from sorted_yaml_representer import yaml, sort_credential, sort_credentials

PIPE = subprocess.PIPE

class GPGError(IOError):
	pass

def get_variables():
	hostname = subprocess.Popen(['uname','-n'],stdout=PIPE).communicate()[0].decode('utf-8').strip()
	agent_info = list(filter(bool,map(lambda x: re.match('GPG_AGENT_INFO=([^;]+)',x), open(os.path.join(os.getenv('HOME'),'.keychain',hostname+'-sh-gpg')).readlines())))[0].groups()[0]
	ssh_auth_sock = list(filter(bool,map(lambda x: re.match('SSH_AUTH_SOCK=([^;]+)',x), open(os.path.join(os.getenv('HOME'),'.keychain',hostname+'-sh')).readlines())))[0].groups()[0]
	ssh_agent_pid = list(filter(bool,map(lambda x: re.match('SSH_AGENT_PID=([^;]+)',x), open(os.path.join(os.getenv('HOME'),'.keychain',hostname+'-sh')).readlines())))[0].groups()[0]
	tty = str(subprocess.Popen(['tty'],stdout=PIPE).communicate()[0]).strip()
	display = getdisplay().strip()
	if tty.startswith('not a tty'):
		for doc in (plumbum.local[os.getenv('HOME')+'/bin/session-getter.pl'])().splitlines():
			if doc.strip():
				try:
					sess = json.loads(doc)
				except Exception as e:
					raise ValueError('encountered {!r} when trying to parse {!r}'.format(e,doc))
				print(doc,file=sys.stderr)
				if sess["Active"] == 'yes':
					tty = sess["Device"]
					if sess["Display"]: display = sess["Display"]
	#print(__import__('yaml').dump(dict(os.environ)))
	ret = dict(os.environ)
	ret.update({'GPG_AGENT_INFO':agent_info,'GPG_TTY':tty,'GNUPG_AGENT_INFO':agent_info,'SSH_AUTH_SOCK':ssh_auth_sock,'SSH_AGENT_PID':ssh_agent_pid,'DISPLAY':display})
	return ret

def read():
	gpg = gnupg.GPG(gnupghome=os.path.join(os.getenv('HOME'),'.gnupg'))
	plaintext = gpg.decrypt(open(os.path.join(os.getenv('HOME'),'.auth.asc')).read())
	if plaintext: return yaml.load_all(str(plaintext))
	else: raise GPGError(plaintext.status)

def write(docs):
	if docs:
		gpg = gnupg.GPG(gnupghome=os.path.join(os.getenv('HOME'),'.gnupg'))
		ciphertext = gpg.encrypt(
			yaml.dump_all(
				map(sort_credential,sort_credentials(filter(bool,docs))),
				default_flow_style=False
			)
		)
		if ciphertext: (sponge[os.getenv('HOME'),'.auth.asc'] << str(ciphertext))()
		else: raise GPGError(ciphertext.status)
	else: raise ValueError('document list needed for writing')

def getcredential(search,usernamesearch=None):
	results = []
	for doc in read():
		try:
			if doc and search in doc['url'] and (usernamesearch is None or usernamesearch in doc['username']):
				results.append((doc['url'], doc['username'], doc['password']))
		except KeyError:
			pass
	if len(results) > 1: raise KeyError('search "%s" is ambiguous' % search)
	elif len(results) == 1: return results[0]
	else: raise KeyError('credential matching "%s" does not exist' % search)

if not six.PY3:
	from keyring.backend import KeyringBackend
	class SuperCryptedKeyringBackend(KeyringBackend):
		def supported(self): return 0
		def get_password(self,service,username):
			return getcredential(service,username)[2]
		def set_password(self,service,username,password):
			raise NotImplementedError('tried to set a password')
			docs = read()
			docs.append(dict(url=service,username=username,password=password))
			write(docs)
			return 0
		def delete_password(self, service, username):
			raise NotImplementedError('tried to set a password')
			docs = read()
			dead = None
			for i,doc in enumerate(docs):
				if doc['url'] == service and doc['username'] == username:
					dead = i
			if dead is None:
				raise KeyError('No matching credential.')
			else:
				del docs[i]
				write(docs)
				return 0

def main(): pass

#if __name__ == '__main__':
#	plac.call(main)
if __name__ == '__main__':
	#if isinstance(results,tuple): results = [results]
	#for result in results:
	#	print('\t'.join(result))
	print('\t'.join(getcredential(' '.join(map(str,sys.argv[1:])))))

