#/bin/bash
#bash clearscript.sh
for file in *.pdf
do
    if [ ! -f $file ]; then
        pdftotext $file
    fi
done
for file in *.txt
do
    echo "Processing $file"
    SUBNUM=`echo $file | sed -ne 's/.*paper\([0-9]*\).*/\1/p'`
    perl paperparser.pl ../isca18-pcinfo.csv ./paper${SUBNUM}.csv < $file
done
