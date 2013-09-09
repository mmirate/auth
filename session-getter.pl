#!/usr/bin/env perl

use strict;
use warnings;
use JSON::XS;
use IPC::Run qw/start/;

# TODO: unify

my $cls = eval { start ['ck-list-sessions'],'>pipe',\*CKOUT };

if (defined $cls) {
	my $session = {};
	while(<CKOUT>) {
		next if /^$/;
		if (/^Session([0-9]+)/) {
			print JSON::XS->new->ascii->encode($session),"\n" if %$session;
			$session = {};
		} elsif (/^\x09([0-9a-z-]+) = ('[^']*'|TRUE|FALSE)$/) {
			my ($key, $val) = ($1, $2);
			$val =~ s/^'(.*)'$/$1/g;
			$key =~ s/-([a-z])/\u$1/g;
			$session->{"$key"} = $val;
		} else {
			die "nonmatching line $_";
		}
	}
	finish $cls;
	print JSON::XS->new->ascii->encode($session),"\n" if %$session;
} else {
	my $session = {};
	foreach my $id (map {int((split ' ', $_)[0])} `loginctl list-sessions`) {
		foreach my $line (`loginctl show-session $id`) {
			chomp($line);
			my ($key, $val) = split /=/, $line,2;
			$session->{$key} = $val;
			$session->{Device} = "/dev/tty/$val" if $key eq 'VTNr';
		}
		print JSON::XS->new->ascii->encode($session),"\n";
	}
}

