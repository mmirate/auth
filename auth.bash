function copypass () {
	local PASSTWICE=""
	local PASSONLY=""
	local CLIPBOARD=""
	for arg in $*; do
		case $arg in
			--pass-twice|--pt|-t)
				local PASSTWICE="yes"
				;;
			--pass-only|--po|-p)
				local PASSONLY="yes"
				;;
			--clipboard|--cb|-c)
				local CLIPBOARD=" -selection clipboard"
				;;
		esac
	done
	read
	echo -n "Password for: " 1>&2
	cut -f 1 <<<"$REPLY" 1>&2 # echo the comment field to stderr
	# head chops off the newline
	[[ -z "$PASSONLY"  ]] && cut -f 2 <<<"$REPLY" | head -c -1 | xclip -i -loops 1 -verbose $CLIPBOARD
	cut -f 3 <<<"$REPLY" | head -c -1 | xclip -i -loops 1 -verbose $CLIPBOARD
	[[ -n "$PASSTWICE" ]] && cut -f 3 <<<"$REPLY" | head -c -1 | xclip -i -loops 1 -verbose $CLIPBOARD
	echo -n | xclip -i $CLIPBOARD
	REPLY="$(head -c 400 /dev/urandom | tr -dc '[:alnum:][:punct:]')"
}
echopass()	{ ./auth.py $@; }
getpass()	{ local search="$1"; shift; echopass $search | copypass $@; }
