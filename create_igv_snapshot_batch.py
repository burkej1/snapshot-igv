'''
Script to generate an IGV script to snapshot all variants in a given tsv in the
relevant bam files.
NOTE: Python3
TODO: Detail expected input format
'''
import os
import argparse


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
    parser = argparse.ArgumentParser(description="Takes a tsv with a list of variants and BS numbers. Creates snapshot" \
                                                 "commands for all bam files matching the bs number.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--inputtsv", help="Input tsv file.", required=True)
    parser.add_argument("-b", "--bamdir", help="Directory containing bam files.", default="bams/")
    parser.add_argument("-d", "--snapshotdirectory", help="Where the snapshots should be saved.", default=os.getcwd())
    parser.add_argument("-o", "--batchoutput", help="Name of output batch file.", default="igvbatchscript.txt")
    parser.add_argument("-w", "--windowsize", help="Width of snapshot in number of bases.", default=150)
    parser.add_argument("-l", "--intervalfile", help="File containing intervals in BED format.", default=None)
    parser.add_argument("-H", "--panelheight", help="Max height for snapshots.", default="10000")
    return parser.parse_args()


def process_tsv(args, snapshot_func):
    '''
    Reads tsv line by line, extracts chromosome, position and relevant BSID for each variant.
    Searches the bam folder for any bam files corresponding to the given BSID, continues if no
    matching bam files are found.
    Passes the list of matching bams, variant information and the BSID to the script generation
    snapshot function and extends the script array with the result.

    Returns properly formatted IGV script to snapshot all variants.
    '''
    igv_script = []
    with open(args.inputtsv, 'r') as inputtsv:
        header = {c: i for i, c in enumerate(inputtsv.readline().rstrip('\n').split('\t'))}
        for line in inputtsv:
            l = line.rstrip('\n').split('\t')
            # TODO: Replace these with correct column names
            variant = (l[header["chrom"]], l[header["start"]])
            bsid = l[header["BS"]]
            # NOTE: abspath behaves strangely with symlinks, probably don't use
            # bams = [os.path.abspath(f) for f in os.listdir(args.bamdir) if f.endswith(".bam") and bsid in f]
            bams = [args.bamdir + f for f in os.listdir(args.bamdir) if f.endswith(".bam") and bsid in f]
            if not bams: continue
            igv_script.extend(snapshot_func(variant, bams, bsid))
    return igv_script


def create_snapshot_func(args):
    '''
    Creates and returns a function to generate the IGV script to snapshot a specific
    variant.
    Args are accessible by snapshot_var function since they're passed to the outer scope
    so it can access necessary variables (windowsize, windowheight, etc.)
    '''
    def snapshot_var(variant, bams, bsid):
        '''
        Creates a chunk of IGV script to snapshot a given variant in a given list of bam files.
        Calculates the start and end of the view position based on the desired window size.
        '''
        script = ["new",
                  "genome b37",
                  "snapshotDirectory " + args.snapshotdirectory,
                  "maxPanelHeight " + args.panelheight]
        script += ["load " + b for b in bams]
        start = int(float(variant[1]) - float(args.windowsize) / 2)
        end   = int(float(variant[1]) + float(args.windowsize) / 2)
        script.append("goto {}:{}-{}".format(variant[0], start, end))
        script.append("snapshot {}_chr{}_pos{}.png".format(bsid, variant[0], variant[1]))
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



