#!/usr/bin/env python
'''
Script to generate an IGV script to snapshot all variants in a given tsv in the
relevant bam files.
'''
import os
import argparse


class SplitArg(argparse.Action):
    '''
    A custom argparse action to split a comma separated string.
    Wholly unnecessary and overcomplicated.
    '''
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string):
        setattr(namespace, self.dest, values.split(','))


def parse_args():
    '''
    Parse arguments
    Necessary inputs are:
    - Folder containing all bam files to be checked (symlinks are ok)
    - TSV containing all variants o be checked (maybe also allow spreadsheets?)
    - File name for IGV script to be written to.
    Optional but useful inputs:
    - Folder to save snapshots
    - Snapshot window size
    - Snapshot height (increase if things are getting cut off)
    - More?
    Returns arguments.
    '''
    parser = argparse.ArgumentParser(description="Takes a tsv with a list of variants and identifiers. Creates snapshot " \
                                                 "commands for all bam files matching the identifier number.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--inputtsv",
                        help="Input tsv file.",
                        required=True)
    parser.add_argument("-b", "--bamdir",
                        help="Directory containing bam files.",
                        default="bams/")
    parser.add_argument("-d", "--snapshotdirectory",
                        help="Where the snapshots should be saved.",
                        default=os.getcwd())
    parser.add_argument("-o", "--batchoutput",
                        help="Name of output batch file.",
                        default="igvbatchscript.txt")
    parser.add_argument("-w", "--windowsize",
                        help="Width of snapshot in number of bases.",
                        default=150)
    parser.add_argument("-H", "--panelheight",
                        help="Max height for snapshots.",
                        default="10000")
    parser.add_argument("-n", "--cols",
                        help="Comma separated list of column names to use (e.g. chrom,pos,identifier)",
                        default=["chrom", "start", "ID"],
                        action=SplitArg)
    return parser.parse_args()


def process_tsv(args, snapshot_func):
    '''
    Reads tsv line by line, extracts chromosome, position and relevant ID for each variant.
    Searches the bam folder for any bam files corresponding to the given ID, continues if no
    matching bam files are found.
    Passes the list of matching bams, variant information and the ID to the script generation
    snapshot function and extends the script array with the result.

    Returns properly formatted IGV script to snapshot all variants.
    '''
    igv_script = []
    with open(args.inputtsv, 'r') as inputtsv:
        header = {c: i for i, c in enumerate(inputtsv.readline().rstrip('\n').split('\t'))}
        for line in inputtsv:
            l = line.rstrip('\n').split('\t')
            variant = (l[header[args.cols[0]]], l[header[args.cols[1]]])
            bam_ids = [i.strip() for i in l[header[args.cols[2]]].split(',')]
            bams = [os.path.abspath(args.bamdir) + '/' + f for bam_id in bam_ids for f in os.listdir(args.bamdir)
                    if f.endswith(".bam") and bam_id in f]
            if not bams: continue
            igv_script.extend(snapshot_func(variant, bams, bam_ids))
    return igv_script


def calculate_window(pos, size):
    '''Calculates start and end of the window to snapshot based on windowsize and
    variant position'''
    start = int(float(pos) - float(size) / 2)
    end   = int(float(pos) + float(size) / 2)
    return (start, end)


def create_snapshot_func(args):
    '''
    Creates and returns a function to generate the IGV script to snapshot a specific
    variant.
    Args are accessible by snapshot_var function since they're passed to the outer scope
    so it can access necessary variables (windowsize, windowheight, etc.)
    '''
    def snapshot_var(variant, bams, bam_ids):
        '''
        Creates a chunk of IGV script to snapshot a given variant in a given list of bam files.
        Calculates the start and end of the view position based on the desired window size.
        '''
        script = ["new",
                  "genome b37",
                  "snapshotDirectory " + os.path.abspath(args.snapshotdirectory),
                  "maxPanelHeight "    + args.panelheight]
        script.extend(["load " + b for b in bams])
        script.append("goto {}:{}-{}".format(variant[0], *calculate_window(variant[1], args.windowsize)))
        script.append("snapshot {}_chr{}_pos{}.png".format('-'.join(bam_ids), *variant))
        # TODO: Add checking of filename in snapshot directory to allow resuming if interrupted
        return script
    return snapshot_var


def main():
    args = parse_args()
    snapshot_func = create_snapshot_func(args)
    igv_script = process_tsv(args, snapshot_func)
    with open(args.batchoutput, 'w') as o:
        o.write('\n'.join(igv_script))


if __name__ == "__main__":
    main()



