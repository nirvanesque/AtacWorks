#!/usr/bin/env python

#
# Copyright (c) 2019, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

r"""Script to generate peak labels from MACS2 output or BED file.

Workflow:
    1. Reads narrowPeak file generated by MACS2 or BED file
    2. Subsets to given chromosomes
    3. Adds a score of 1 for all bases in peaks
    4. Writes to bedGraph file
    5. Converts bedGraph to bigWig file using bedGraphToBigWig
    6. Deletes bedGraph

Output:
    bigWig file containing score of 1 at peak positions

Example:
    python peak2bw.py --input peaks.narrowPeak \
    --sizes example/reference/hg19.chrom.sizes \
    --skip 1

"""

import argparse
import logging

from claragenomics.io.bedgraphio import df_to_bedGraph
from claragenomics.io.bigwigio import bedgraph_to_bigwig

import pandas as pd

# Set up logging
log_formatter = logging.Formatter(
    '%(levelname)s:%(asctime)s:%(name)s] %(message)s')
_logger = logging.getLogger('AtacWorks-peak2bw')
_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_handler.setFormatter(log_formatter)
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)


def parse_args():
    """Parse command line arguments.

    Return:
        args : parsed argument object.

    """
    parser = argparse.ArgumentParser(
        description='Convert BED file or MACS2 narrowPeak file \
        to bigWig file')
    parser.add_argument('--input', type=str,
                        help='Path to narrowPeak or BED file',
                        required=True)
    parser.add_argument('--sizes', type=str,
                        help='Path to chromosome sizes file. \
                        Only peaks in these chromosomes will \
                        be encoded in the output bigWig file.',
                        required=True)
    parser.add_argument('--out_dir', type=str, help='Directory \
                        to write output file.', required=True)
    parser.add_argument('--prefix', type=str, help='Output file \
                        prefix. Output file name will be \
                        prefix.bw. If not supplied, the name \
                        of the input BED file will be used as \
                        the prefix.')
    parser.add_argument('--skip', type=int, default=0,
                        help='Number of rows of the input file \
                        to skip. Use --skip 1 if the first line \
                        is a header. .narrowPeak files produced \
                        by MACS2 will require --skip 1.')
    args = parser.parse_args()
    return args


def main():
    """Convert peak files to bigwig."""
    args = parse_args()

    # Read input files
    _logger.info('Reading input files')
    peaks = pd.read_csv(args.input, sep='\t', header=None,
                        usecols=[0, 1, 2], skiprows=args.skip)
    sizes = pd.read_csv(args.sizes, sep='\t', header=None)

    # Subset to peaks in sizes file
    # TODO: Move this test into the df_to_bedGraph function
    peaks_filtered = peaks[peaks[0].isin(sizes[0])].copy()
    _logger.info('Retaining ' + str(
        len(peaks_filtered)) + ' of ' + str(
        len(peaks)) + ' peaks in given chromosomes.')

    # Add score of 1 for all peaks
    _logger.info('Adding score')
    peaks_filtered[3] = 1

    # Set name for output file
    if args.prefix is None:
        # Output file gets name from input
        prefix = args.out_dir + '/' + args.input
    else:
        prefix = args.out_dir + '/' + args.prefix

    # Write bedGraph
    _logger.info('Writing peaks to bedGraph file')
    df_to_bedGraph(peaks_filtered, prefix + '.bedGraph')

    # Write bigWig and delete bedGraph
    _logger.info('Writing peaks to bigWig file {}'.format(prefix + '.bw'))
    bedgraph_to_bigwig(prefix + '.bedGraph', args.sizes, deletebg=True)
    _logger.info('Done!')


if __name__ == "__main__":
    main()
