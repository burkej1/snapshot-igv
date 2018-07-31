# snapshot-igv

Python script to generate an IGV batch script snapshot a list of variants in tsv format.

# Arguments

```
usage: create_igv_snapshot_batch.py [-h] -i INPUTTSV [-b BAMDIR]
                                    [-d SNAPSHOTDIRECTORY] [-o BATCHOUTPUT]
                                    [-w WINDOWSIZE] [-H PANELHEIGHT] [-n COLS]

Takes a tsv with a list of variants and identifiers. Creates snapshotcommands
for all bam files matching the identifier number.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTTSV, --inputtsv INPUTTSV
                        Input tsv file. (default: None)
  -b BAMDIR, --bamdir BAMDIR
                        Directory containing bam files. (default: bams/)
  -d SNAPSHOTDIRECTORY, --snapshotdirectory SNAPSHOTDIRECTORY
                        Where the snapshots should be saved. (default: os.getcwd())
  -o BATCHOUTPUT, --batchoutput BATCHOUTPUT
                        Name of output batch file. (default:
                        igvbatchscript.txt)
  -w WINDOWSIZE, --windowsize WINDOWSIZE
                        Width of snapshot in number of bases. (default: 150)
  -H PANELHEIGHT, --panelheight PANELHEIGHT
                        Max height for snapshots. (default: 10000)
  -n COLS, --cols COLS  Comma separated list of column names to use (e.g.
                        chrom,pos,identifier) (default: ['chrom', 'start',
                        'ID'])
```

# Usage

Takes a tsv containing a list of variants in the following format (ID column can contain multiple comma separated identifiers):

| chrom | start | ID |
| --- | --- | --- |
| 1 | 1234 | ID1234 |
| 1 | 1237 | ID1234,ID1789 |

Columns can be in any order, names are used to extract necessary information.

Default column names can be changed with the `--cols` option (order is important):

```
--cols chromosome,position,identifier
```

If bam files are spread across multiple folders symlinking into a single folder is an easy way to deal with it:
```
$ ls
folder1/  folder2/  folder3/
$ mkdir all_bams
$ for ((x=1; x<4; x++)) {
>   ln -s folder${x}/* all_bams/
> }
```

Finally, given a correctly formatted input tsv, a folder containing bam files of interest and a directory to save the snapshots run the script:
```
python create_igv_snapshot_batch.py -i input_tsv.tsv -o igv_batch_script.txt -b all_bams/ -d snapshotdir/
```

Finally, open IGV, select tools, run batch and select the file output by the script (above, igv_batch_script.txt).


