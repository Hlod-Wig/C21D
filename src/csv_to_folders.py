import csv
import json
import re
import os
import random

def Proces (demarcacio):

    # Input file
    csvfile = open('escoles-%s.csv' % demarcacio, 'r')

    reader = csv.reader(csvfile, delimiter=';')

    # On first row on input there is the column names, then we need to
    # skip it
    first = True;

    # We will parse row by row the input file
    for row in reader:

        # Skip column names line
        if first:
            first = False
            continue


        localitat = row[1].upper()
        localitat = localitat.replace('"', ".");
        localitat = localitat.replace('(', ",");
        localitat = localitat.replace(')', ",");

        escola = row[7].upper()
        escola = escola.replace('"', ".");
        escola = escola.replace('(', ",");
        escola = escola.replace(')', ",");

        folder = "resultats/%s/%s/%s/%s-%s-%s-%s/" % (demarcacio.upper(),localitat, escola, row[2],row[3],row[4],row[5])
        print folder
        cmd = 'mkdir -p "%s"' % folder
        os.system(cmd)

        cmd = 'cp %s "%s/resultats.txt"' % ("template-%s.txt" % demarcacio, folder)
        os.system(cmd)

        i = random.randint(0, 3)
        cmd = "convert -resize 768X1024 -quality 40 acta-%d.jpg acta.jpg" % i
        os.system(cmd)

        cmd = 'cp acta.jpg "%s/"' % folder
        os.system(cmd)


def usage():
    print
    print "Usage: csv_to_folders.py [girona|barcelona|lleida|tarragona]"
    print

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        demarcacio = sys.argv[1]
    else:
        usage()
        sys.exit(0)

    process = Proces(demarcacio)
