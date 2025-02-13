#!/usr/bin/perl   -wT

# Copyright 2010 Emma Rath. All rights reserved.
# Soon this program will be released under an open source software license such as GNU General Public License or
# Creative Commons license for Free Software Foundation's GNU General Public License at creativecommons.org

# perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain B
# perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain Z -fromchain H
# perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain B -fromline 5190 -toline 5200

# This perl program runs as a as a cgi script on a web server that displays web pages.
# This perl program also runs as a as batch program on the command line.

# This program reads in a PDB 3D file and
# renames the chain field (column 22) to the -tochain
# for lines starting with ATOM or HETATM.
# If -fromchain is present, or if -fromline and -toline are present,
# then only that chain or those lines will have the chain renamed.

use warnings;
use strict;
use diagnostics;
use Getopt::Long;
use Math::Complex;
use Math::Trig;
use CGI;
use Data::Dumper;
# $Data::Dumper::Purity = 1;
# print "var x = " . Dumper( $x ) . "\n"; # debug
# my $wait_for_key_press = <STDIN>; # debug

my $q = new CGI;
my $global;
my $input;
my $debug = '';

#===================================================================================================
#=================================              MAIN              ==================================
#===================================================================================================

init();

get_program_mode();

if ($global->{'program_mode'} eq 'cgi-display-form') {

	display_html_form();

} elsif ($global->{'program_mode'} eq 'cgi-output') {

	get_html_input();
	if ($global->{'got_error'} == 0) {
		build_and_output_results_for_html_output();
	} else {
		display_html_form();
	}

} else { # $global->{'program_mode'} eq 'command-line'

	get_command_line_input();
	if ($global->{'got_error'} == 0) {

		my $untainted_infile = untaint( $input->{'infile'} );
		if ($untainted_infile eq '') {
			$untainted_infile = "renamepdbchain";
		}
		my $output_file = $untainted_infile . ".pdb";
		open( OUTFILE, ">$output_file") or
			die "Cannot open $output_file for writing\n";
		build_and_output_results_for_command_line();
		close OUTFILE;
	} else {
		output_command_line_help();
	}
}



#===================================================================================================
#	this is the main logic subroutine of this program for command-line mode.
#	given an input PDB file, proces the input and produce the output.
#===================================================================================================

sub build_and_output_results_for_command_line {

	build_the_output();

	my @input_lines = @{$input->{'input_lines'}};
	foreach my $line (@input_lines) {
		print OUTFILE "$line\n";
	}
}



#===================================================================================================
#	this is the main logic subroutine of this program for cgi-output mode.
#	given an input PDB file, process the input and produce the output.
#===================================================================================================

sub build_and_output_results_for_html_output {

	build_the_output();

	if ($input->{'whereto'} eq 'S') { # write output to the screen

	print $q->header();
	print	#$q->start_html(-title=>$text_title),
		"<html><head>\n",
		'<style type="text/css">' . "\n",
		'<!--' . "\n",
		'.tt {' . "\n",
		'	font-size: 14px;' . "\n",
		'	font-family: courier, monospace;' . "\n",
		'	color: #000000;' . "\n",
		'}' . "\n",
		'-->' . "\n",
		'</style>' . "\n",
		"</head><body>\n";
		print "<span class='tt'>\n";
		my @input_lines = @{$input->{'input_lines'}};
		foreach my $line (@input_lines) {
			$line =~ s/ /&nbsp;/g;
			$line = "$line<br>\n";
			print $line;
		}
		print "</span></body></html>\n";

	} else { # $input->{'whereto'} eq 'F' # write output to a file to be downloaded

		print $q->header("Content-type: text/plain");
		my @input_lines = @{$input->{'input_lines'}};
		foreach my $line (@input_lines) {
			print "$line\n";
		}

	}

	if ($debug ne '') {
		print "$debug\n";
	}
}



#===================================================================================================
#	move the input PDB file contents to output, changing the chain
#===================================================================================================

sub build_the_output {

	my @input_lines = @{$input->{'input_lines'}};

	if (($input->{'fromline'} ne '') and ($input->{'toline'} eq '')) {
		$input->{'toline'} = 9999999;
	} elsif (($input->{'fromline'} eq '') and ($input->{'toline'} ne '')) {
		$input->{'fromline'} = 1;
	}

	for ( my $i = 0; $i < @input_lines; $i++ ) {
		my $line = $input_lines[$i];
		my $l = $i + 1;
		$line = trim($line);
		if ($line ne '') {
			my $change_this_line = 0;
			if (($input->{'fromline'} ne '') and ($input->{'toline'} ne '')) {
				if (($l >= $input->{'fromline'}) && ($l <= $input->{'toline'})) {
					$change_this_line = 1;
				}
			} elsif ($input->{'fromchain'} ne '') {
				if (length($line) >= 22) {
					my $this_chain = trim(substr($line,21,1));
					if ($this_chain eq $input->{'fromchain'}) {
						$change_this_line = 1;
					}
				}
			} else {
				$change_this_line = 1;
			}
			if ($change_this_line == 1) {
				if (length($line) >= 6) {
					my $line_id = substr($line,0,6);
					if (($line_id eq 'ATOM  ') or ($line_id eq 'HETATM') or ($line_id eq 'TER   ')) {
						my $bit1 = substr($line,0,21);
						my $bit2 = substr($line,22);
						my $new_line = $bit1 . $input->{'tochain'} . $bit2;
						$input_lines[$i] = $new_line;
					}
				}
			}
		}
	}

	$input->{'input_lines'} = \@input_lines;
}



#===================================================================================================
#	this program is being called to display the HTML input form
#===================================================================================================

sub display_html_form {

	html_header();

	my $request_uri = $ENV{'REQUEST_URI'};
	my @bits = split(/\//, $request_uri);
	my $pgm_name = $bits[$#bits];

	print "<br><br>\n";

	print "	<form action='$pgm_name' method='post' enctype='multipart/form-data'>\n",
		"	<table cellspacing=0 cellpadding=2 border=0>\n";

	if ($global->{'got_error'} == 1) {
print "		<tr>\n",
"			<td valign='top' align='left'>\n",
"				<p><font color='red'>" . $global->{'err_msg'} . "<br><b>Didn't process because of input error(s).</b><br><br></font></p>\n",
"			</td>\n",
"		</tr>\n";
	}

print "		<tr>\n",
"			<td valign='top' align='left'>\n",
"				<table cellspacing=0 cellpadding=0 border=0>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Please provide a PDB file with the chain id in column 22.<br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Upload the PDB file from your computer.<br>Please note that this PDB file is not validated, so make sure that it is a valid PDB file.<br>\n",
							"<input type='file' name='upload_file'><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"<table cellspacing=10 cellpadding=0 border=0>\n",
							"<tr><td width='20'></td><td valign='top' align='left'>or</td></tr>\n",
							"</table>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"<table cellspacing=10 cellpadding=0 border=0>\n",
							"<tr><td width='20'></td>	<td valign='top' align='left'>Enter the PDB file contents here.<br>Please note that these PDB file contents are not validated, so make sure that they are valid PDB file contents.</td></tr>\n",
							"<tr><td></td>			<td valign='top' align='left'><textarea name='pdb_contents' rows='5' cols='50'></textarea></td></tr>\n",
							"<tr><td></td>			<td valign='top' align='left'>(Provide either a file or enter the contents here, not both.<br>If both provided, then contents here will be processed instead of uploaded file.)</td></tr>\n",
							"</table><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Rename chain to : ",
							"<input type='text' name='tochain' size=3 value=''>",
							" (mandatory field)<br><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Only rename chain : ",
							"<input type='text' name='fromchain' size=3 value=''>",
							" (optional field)<br><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Line from : ",
							"<input type='text' name='fromline' size=3 value=''>",
							" (optional field)<br><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"Line to : ",
							"<input type='text' name='toline' size=3 value=''>",
							" (optional field)<br><br>\n",
"						</td>\n",
"					</tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"<input type='radio' name='whereto' value='S' checked>Display results on screen<br>\n",
							"<input type='radio' name='whereto' value='F'>Write results to output file<br><br>\n",
"						</td>\n",
"					</tr>\n",

"					<tr><td height='15'></td></tr>\n",
"					<tr>\n",
"						<td valign='top' align='left'>\n",
							"<input type='submit' name='submit' value='Upload'>\n",
"						</td>\n",
"					</tr>\n",

"				</table>\n",
"			</td>\n",
"		</tr>\n";

	print "	</table>\n",
		"</form>\n";

	html_footer();
}



#===================================================================================================
#	in command line mode - get the command line options, read the input file.
#===================================================================================================

sub get_command_line_input {

	my $input_file;
	my $input_tochain;
	my $input_fromchain;
	my $input_fromline;
	my $input_toline;
	my $input_h;
	my $input_help;

	GetOptions( "infile=s" => \$input_file, "tochain=s" => \$input_tochain, "fromchain=s" => \$input_fromchain, "fromline=s" => \$input_fromline, "toline=s" => \$input_toline, "h" => \$input_h, "help" => \$input_help );
	if (!defined $input_file) {
		die "Usage $0 -infile INPUTFILE -tochain CHAINID -add NUMBER\n";
	}

	if (defined $input_file) {
		$input->{'infile'} = $input_file;
	}
	if (defined $input_tochain) {
		$input->{'tochain'} = $input_tochain;
	}
	if (defined $input_fromchain) {
		$input->{'fromchain'} = $input_fromchain;
	}
	if (defined $input_fromline) {
		$input->{'fromline'} = $input_fromline;
	}
	if (defined $input_toline) {
		$input->{'toline'} = $input_toline;
	}
	if (defined $input_h) {
		$input->{'h'} = $input_h;
	}
	if (defined $input_help) {
		$input->{'help'} = $input_help;
	}
	if ((defined $input_h) || (defined $input_help)) {
		$global->{'got_error'} = 1;
	}

	open INFILE, $input->{'infile'} or die $!;
	my @input_lines = <INFILE>;
	my @new_input_lines;
	foreach my $line (@input_lines) {
		chomp($line);
		push(@new_input_lines, $line);
	}
	$input->{'input_lines'} = \@new_input_lines;
}



#===================================================================================================
#	get the input from the html form, so can process the input
#===================================================================================================

sub get_html_input {

	my $params = $q->Vars;

	if (defined($params->{'tochain'})) {
		my $input_tochain = trim( $params->{'tochain'} );
		if (is_valid_chain($input_tochain) == 1) {
			$input->{'tochain'} = $input_tochain;
		} else {
			$global->{'got_error'} = 1;
			$global->{'err_msg'} .= $global->{'err_msg'} . "The 'Rename chain to' that you entered is invalid. It must only be 1 character long.<br>\n";
		}
	}
	if ($input->{'tochain'} eq '') {
		$global->{'got_error'} = 1;
		$global->{'err_msg'} .= $global->{'err_msg'} . "Please enter the 'Rename chain to' field.<br>\n";
	}

	if (defined($params->{'fromchain'})) {
		if ($params->{'fromchain'} ne '') {
			my $input_fromchain = trim( $params->{'fromchain'} );
			if (is_valid_chain($input_fromchain) == 1) {
				$input->{'fromchain'} = $input_fromchain;
			} else {
				$global->{'got_error'} = 1;
				$global->{'err_msg'} .= $global->{'err_msg'} . "The 'Only rename chain' that you entered is invalid. It must only be 1 character long.<br>\n";
			}
		}
	}

	if (defined($params->{'fromline'})) {
		if ($params->{'fromline'} ne '') {
			my $input_fromline = trim( $params->{'fromline'} );
			if (is_valid_line_number($input_fromline) == 1) {
				$input->{'fromline'} = $input_fromline;
			} else {
				$global->{'got_error'} = 1;
				$global->{'err_msg'} .= $global->{'err_msg'} . "The 'Line from' that you entered is not a valid line number.<br>\n";
			}
		}
	}

	if (defined($params->{'toline'})) {
		if ($params->{'toline'} ne '') {
			my $input_toline = trim( $params->{'toline'} );
			if (is_valid_line_number($input_toline) == 1) {
				$input->{'toline'} = $input_toline;
			} else {
				$global->{'got_error'} = 1;
				$global->{'err_msg'} .= $global->{'err_msg'} . "The 'Line to' that you entered is not a valid line number.<br>\n";
			}
		}
	}

	if (defined($params->{'whereto'})) {
		if ($params->{'whereto'} ne '') {
			my $input_whereto = trim( $params->{'whereto'} );
			$input->{'whereto'} = uc($input_whereto);
			if (($input->{'whereto'} ne 'S') and ($input->{'whereto'} ne 'F')) {
				$input->{'whereto'} = 'S';
			}
		}
	}

	my @input_lines;
	$input->{'input_lines'} = \@input_lines;

	my $user_provided_pdb_contents = 0;
	if (defined($params->{'pdb_contents'})) {
		my $pdb_contents = trim( $params->{'pdb_contents'} );
		if ($pdb_contents ne '') {
			$user_provided_pdb_contents = 1;
			my @pdb_lines = split(/\n|\r/, $pdb_contents);
			foreach my $pdb_line (@pdb_lines) {
				$pdb_line = trim($pdb_line);
				if ($pdb_line ne '') {
					push( @input_lines, $pdb_line );
				}
			}
		}
	}

	if ( (defined($params->{'upload_file'})) && ($user_provided_pdb_contents == 0)) {
		my $upload_file = $q->param('upload_file');
		my $upload_filehandle = $q->upload('upload_file');
		if ($upload_file ne '') {
			if ($upload_filehandle eq '') {
				$global->{'got_error'} = 1;
				$global->{'err_msg'} .= "The upload didn't work. Probably your file is too big - bigger than 5MB.<br>";
			} else {

				# read the uploaded file

				my @uploaded_lines;

				my $user_data = '';
				while ( <$upload_filehandle> ) {
					my $input_line = $_;
					chomp($input_line);
					push( @input_lines, $input_line );
				}
			}
		}
	}

	if ($global->{'got_error'} == 0) {
		my $num_input_lines = $#{$input->{'input_lines'}};
		if ($num_input_lines < 1) {
			$global->{'got_error'} = 1;
			$global->{'err_msg'} .= "No input PDB lines were given. Please enter your PDB file contents or upload a PDB file.<br>";
		}
	}
}



#===================================================================================================
#	figure out whether this program is being called to display the HTML input form,
#	or whether the form has been filled and now the results need to be displayed,
#	or whether this program is being run in batch mode from the command line.
#===================================================================================================

sub get_program_mode {

	$global->{'program_mode'} = 'command-line';
	if (defined($ENV{'REQUEST_METHOD'})) {
		if ($ENV{'REQUEST_METHOD'} eq 'POST') {
			$global->{'program_mode'} = 'cgi-output';
		} else {
			$global->{'program_mode'} = 'cgi-display-form';
		}
	} else {
		$global->{'program_mode'} = 'command-line';
	}
}



#===================================================================================================
#	html code for the graphics part of the header of the html page
#===================================================================================================

sub html_code_for_graphics_header {

	my $title = shift;
	my $html_code = '';

	$html_code .= "<table width='100%' cellspacing='0' cellpadding='0' border='0'><tr><td align='left'>\n" .
		"<table height='160' cellspacing='0' cellpadding='0' border='0' align='left' bgcolor='#a4a5e9'>\n" .
		#"	style='background-image: url(\"bluegold.gif\");\n" .
		#"		background-attachment: fixed;\n" .
		#"		background-position: top right;\n" .
		#"		background-repeat: no-repeat;'>\n" .
		"	<tr>\n" .
		"		<td height='160' valign='center'>\n" .
		"			<table height='160' cellspacing='0' cellpadding='0' border='0'>\n" .
		"				<tr>\n" .
		"					<td width='20'></td>\n" .
		"					<td width='740' valign='center'>\n" .
		"						<font size='5' color='black'>$title</font>\n" .
		"					</td>\n" .
		#"					<td width='560' valign='center'>\n" .
		#"						<font size='5' color='black'>$title</font>\n" .
		#"					</td>\n" .
		#"					<td width='180' valign='center'>\n" .
		#"						<img src='greenquoll.gif' width='180' height='100' border='1'>\n" .
		#"					</td>\n" .
		"					<td width='240'>\n" .
		"						<img src='bluegold.gif' width='240' height='160' border='0'>\n" .
		"					</td>\n" .
		"				</tr>\n" .
		"			</table>\n" .
		"		</td>\n" .
		"	</tr>\n" .
		"</table>\n" .
		"</td></tr><tr><td align='left'>\n" .
		"<table height='20' cellspacing='0' cellpadding='0' border='0'><tr><td></td></tr></table>\n<br>";

	return $html_code;
}



#===================================================================================================
#	html code for the header of the html page
#===================================================================================================

sub html_header {

	my $title = 'RENAME CHAIN IN PDB FILE';

	print $q->header();
	print	#$q->start_html(-title=>$text_title),
		"<html><head><title>$title</title>\n",
		'<style type="text/css">' . "\n",
		'<!--' . "\n",
		'.basestyle {' . "\n",
		'	color: #FFFFFF;' . "\n",
		'	font-size: 14px;' . "\n",
		'	font-family: Arial, Helvetica, Verdana, sans-serif;' . "\n",
		'}' . "\n",
		'h1 {' . "\n",
		'	font-size: 16px;' . "\n",
		'	font-weight: bold;' . "\n",
		'	font-family: Arial, Helvetica,Verdana, sans-serif;' . "\n",
		'}' . "\n",
		'body, td, p, input {' . "\n",
		'	font-size: 14px;' . "\n",
		'	font-family: Arial, Helvetica, Verdana, sans-serif;' . "\n",
		'	color: #333333;' . "\n",
		'}' . "\n",
		'.navlinks {' . "\n",
		'	font-size: 14px;' . "\n",
		'	font-family: Arial, Helvetica, Verdana, sans-serif;' . "\n",
		'	font-weight: bold;' . "\n",
		'	color: #FFFFFF;' . "\n",
		'}' . "\n",
		'.tt {' . "\n",
		'	font-size: 12px;' . "\n",
		'	font-family: courier, monospace;' . "\n",
		'	color: #000000;' . "\n",
		'}' . "\n",
		'-->' . "\n",
		'</style>' . "\n",
		"</head><body>\n";

		my $output_line = html_code_for_graphics_header($title);
		print $output_line;
}



#===================================================================================================
#	html code for the footer of the html page
#===================================================================================================

sub html_footer {

	print $debug . "<br>\n";

	print "<br><br>\n";
	print "<b>SOURCE CODE :</b> <a href='renamepdbchain_pl.txt'>renamepdbchain_pl.txt</a><br>\n";

	print "<br><br>\n";
	print "<b>COPYRIGHT :</b><br>\n";
	print "Copyright &copy; 2010 Emma Rath. All rights reserved.<br>\n";
	print "Soon this program will be released under an open source software license such as GNU General Public License or<br>\n";
	print "Creative Commons license for Free Software Foundation's GNU General Public License at creativecommons.org<br>\n";

	print "<br><br>\n";
	print "</td></tr></table>\n";
	print $q->end_html();
}



#===================================================================================================
#	initialise global and program variables before starting processing.
#===================================================================================================

sub init {

	my %global_hash;
	$global = \%global_hash;
	$global->{'got_error'} = 0;
	$global->{'err_msg'} = '';

	my %input_hash;
	$input = \%input_hash;
	$input->{'infile'} = '';
	$input->{'fromchain'} = '';
	$input->{'tochain'} = '';
	$input->{'fromline'} = '';
	$input->{'toline'} = '';
	$input->{'whereto'} = '';
	$input->{'h'} = '';
	$input->{'help'} = '';
	my @input_lines;
	$input->{'input_lines'} = \@input_lines;
}



#===================================================================================================
sub is_valid_chain {

	my $chain = shift;
	my $is_ok = 0;
	if (length($chain) <= 1) {
		$is_ok = 1;
	}
	return $is_ok;
}



#===================================================================================================
sub is_valid_decimal {

	my $input_integer = shift;
	my $return = 1;

	if ($input_integer !~ /^-?(?:\d+(?:\.\d*)?|\.\d+)$/) {
		$return = 0;
	} else {
		if ($input_integer < 1) {
			$return = 0;
		}
	}

	return $return;
}



#===================================================================================================
sub is_valid_integer {

	my $input_integer = shift;
	my $return = 1;

	if ($input_integer !~ /^\d+$/) {
		$return = 0;
	} else {
		if ($input_integer < 1) {
			$return = 0;
		}
	}

	return $return;
}



#===================================================================================================
sub is_valid_line_number {

	my $input_integer = shift;
	my $return = 1;

	if ($input_integer !~ /^\d+$/) {
		$return = 0;
	} else {
		if ($input_integer < 1) {
			$return = 0;
		}
	}

	return $return;
}



#===================================================================================================
#	in command line mode, output some text help
#===================================================================================================

sub output_command_line_help {

	my $command_line_help_text = '';

	$command_line_help_text .= "Here are some examples of calling this program in command line mode :\n";
	$command_line_help_text .= "\n";
	$command_line_help_text .= "          perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain B\n";
	$command_line_help_text .= "          perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain B -fromchain E\n";
	$command_line_help_text .= "          perl -T renamepdbchain.pl -infile 1E7P.pdb -tochain B -fromline 12 -toline 120\n";
	$command_line_help_text .= "\n";
	$command_line_help_text .= "This program reads in a PDB 3D file and ";
	$command_line_help_text .= "renames the chain field (column 22) to the -tochain";
	$command_line_help_text .= "for lines starting with ATOM or HETATM.\n";
	$command_line_help_text .= "If -fromchain is present, or if -fromline and -toline are present,";
	$command_line_help_text .= "then only that chain or those lines will have the chain renamed.\n";
	$command_line_help_text .= "\n";

	print $command_line_help_text;
}



#===================================================================================================
#	a perl utility subroutine - remove leading and trailing blanks from a string
#===================================================================================================

sub trim {
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        return $string;
}



#===================================================================================================
#	untaint file name
#===================================================================================================

sub untaint {

	my $path = shift;
	# user_error("path cannot contain metacharacters") if $path=~/[\n|<>&!;\'\"]/;

	# extract only legal alphanumerics from the filename
	# $path =~ m!(/[a-zA-Z/0-9._~\-]+)!;
	# $path =~ /([\w"-"".""_"]+)/;
	$path =~ /([a-zA-Z0-9._~\-]+)/;
	if (defined($1)) {
		$path = $1;
	} else {
		$path = '';
	}

	# user_error("path cannot contain relative directories")
	#	if $path=~m!\.\.!;

	return $path;
}
