#!/usr/bin/perl
##
##
## usage:   perl this-program.pl /path/to/pc/members/file.csv /path/to/parsed/file.csv < input-file.txt
#
## read from perl stdin
use strict;
use warnings;
use Text::CSV_XS;

sub pc_match_me {
    my ($ii, $aref) = @_;
    my @names_array = split(/\./, $main::pcfirst[$ii]);
    my $initial1;
    my $initial2;
    if( (scalar @names_array) eq 1 ) {
        $initial1 = substr($names_array[0],0,1).$main::stop;
    } else {
        $initial1 = substr($names_array[0],0,1).$main::stop;
        $initial2 = substr($names_array[1],0,1).$main::stop;
    }
    #print "Initial1: $initial1, Initial2: $initial2, to match on: @$aref\n";
    if( $aref->[2] eq ($main::pclast[$ii]) ||
        ($aref->[2] eq ($main::pclast[$ii].$main::comma)) ||
        ($aref->[2] eq ($main::pclast[$ii].$main::stop)) ){
        # Case 1: simple, [ (junk), D., Sanchez ] matches Daniel Sanchez
        #if( index($aref->[1],$initial1) ) {
        if( $aref->[1] eq $initial1 ) {
            #print "Matched $initial1, $main::pclast[$ii] in @$aref, CASE 1\n";
            return 1;
        }
        # Case 2: medium , [ T., F., Wenisch ] matches T. Wenisch
        #if( index($aref->[0],$initial1) ) {
        if( $aref->[0] eq $initial1 ) {
            #print "Matched $initial1, $main::pclast[$ii] in @$aref, CASE 2\n";
            return 1;
        }
        # Case 3: hard , [ T., N., Vijaykumar ] matches T.N. Vijaykumar
        #if( index($aref->[0],$initial1) &&
        #index($aref->[1],$initial2) ){
        if( $aref->[0] eq $initial1 &&
            $aref->[1] eq $initial2 ){
            #print "Matched $initial1, $initial2, $main::pclast[$ii] in @$aref, CASE 3\n";
            return 1;
        }

        if( $aref->[1] eq $main::pcfirst[$ii] ) {
            #print "Matched $main::pcfirst[$ii], $main::pclast[$ii] in @$aref, CASE 4\n";
            return 1;
        }
        if( $aref->[0] eq $main::pcfirst[$ii] ) {
            #print "Matched $main::pcfirst[$ii], $main::pclast[$ii] in @$aref, CASE 5\n";
            return 1;
        }
    }
    return 0;
}

my $printstuff = 1;
my $reference_act1 = 0; 
my $reference_act2 = 0;
my $reference_act = 0;
our @pcfirst = ();
our @pclast = ();
our @pcemail = ();

# Loop to parse PC members into two lists
my $pc_csv = shift;
my $readerObject = Text::CSV_XS->new({ binary=>1,auto_diag=>1 });
open my $pc_fh, "<:encoding(UTF-8)", $pc_csv or die "$pc_csv: $!";

my $array_ref = $readerObject->getline_all($pc_fh);
@pcfirst = map { $_->[0] } @{$array_ref};
@pclast = map { $_->[1] } @{$array_ref};
@pcemail = map { $_->[2] } @{$array_ref};
shift @pclast;
shift @pcfirst;
shift @pcemail;
push @pclast, "Wenisch";
push @pcfirst, "Thomas";
push @pcemail, "twenisch\@umich.edu";

# Open CSV to write output of members referenced
my $output_csv = shift;
#my $writerObject = Text::CSV_XS->new({ binary=>1,auto_diag=>1 });
open my $output_fh , ">:encoding(UTF-8)", $output_csv or die "$output_csv: $!";
#shift; # to get rid of <

my $confidential1 = 'Confidential';
my $confidential2 = 'confidential';
my $references1 = 'REFERENCES';
my $references2 = 'References';
my $ack1 = 'Acknowledgement';
my $ack2 = 'ACKNOWLEDGEMENT';
my $ackset=0;

my $firstref = '[1]';
my $wordcount=0;
my $papernumber=0;
my $filename = 'wordcnt.txt';
open(my $fh, '>>', $filename) or die "Could not open file '$filename' $!";

my $pcsize = @pclast;
our $comma = ",";
our $hash = '#';
our $stop = ".";

my @pccount = ($pcsize);

for (my $i=0; $i < $pcsize ; $i++)
{
    $pccount[$i]=0; 
}

my @rolling_word_array = qw ( blank blank blank );
while (<>)
{
    # split each input line; words are separated by whitespace
    for my $word (split)
    {
        #print $word;
        if($reference_act==0)
        {
            $wordcount++;
        }
        if((index($word,$ack1)!=-1) || (index($word,$ack2)!=-1))
        {
            $ackset=1;
        }
        #print "$word\n";
        if( index($word,$references1) != -1 || index($word,$references2) != -1 )
        {
            #print "found $references1, activating.\n";
            $reference_act = 1;
        }
        if($reference_act==1)
        {
            shift @rolling_word_array;
            push @rolling_word_array, $word;
            #print "Calling matchme with: @rolling_word_array\n";
            for(my $ii=0; $ii < $pcsize; $ii++ )
            {
                if( pc_match_me($ii,\@rolling_word_array) )
                {
                    $pccount[$ii]++;
                }
            }
        } 
    }
}
if ( 0 ) {
    if($ackset == 1){
        print "\nAcknowledgment Printed!!\n";
    }
}
#print "\nWord_Count \t $wordcount\n";
#print "\nPC Members Referenced\n";
#my @values = split('#', $papernumber);
print $output_fh "pc_key,refs\n";
for (my $i=0; $i < $pcsize; $i++)
{
    if($pccount[$i]!=0)
    {
        print $output_fh "$pcemail[$i],$pccount[$i]\n";
    }
}

#print $fh "$wordcount \t $ackset\n";
close $fh;
close $output_fh;
close $pc_fh;
