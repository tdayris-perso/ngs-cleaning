#!/usr/bin/python3.8
# -*- coding: utf-8 -*-


"""
This script contains functions that are to be called by any other scripts in
this pipeline.
"""

import argparse  # Argument parsing
import logging  # Logging behaviour
import pandas  # Handle large datasets
import pytest
import yaml  # Handle Yaml IO

import os.path as op  # Path and file system manipulation
import pandas  # Deal with TSV files (design)

from itertools import chain  # Chain iterators
from pathlib import Path  # Easily handle paths
from typing import Any, Dict, List, Optional, Union  # Type hints


# Building custom class for help formatter
class CustomFormatter(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter
    ):
    """
    This class is used only to allow line breaks in the documentation,
    without breaking the classic argument formatting.
    """


def write_yaml(output_yaml: Path, data: Dict[str, Any]) -> None:
    """
    Save given dictionnary as Yaml-formatted text file
    """
    with output_yaml.open("w") as outyaml:
        yaml.dump(data, outyaml, default_flow_style=False)


def fastq_pairs(design: pandas.DataFrame) -> Dict[str, List[str]]:
    """
    This function returns fastq files as pairs if the input design is paired,
    or single ended elsewise.
    """
    try:
        # Pair-ended case
        design_iterator = zip(
            design.Sample_id,
            design.Upstream_file,
            design.Downstream_file
        )

        return {
            sample: [up, down]
            for sample, up, down in design_iterator
        }
    except AttributeError:
        # Single ended case
        design_iterator = zip(
            design.Sample_id,
            design.Upstream_file
        )

        return {
            sample: [fq]
            for sample, fq in design_iterator
        }


def sample_stream(design: pandas.DataFrame) -> Dict[str, str]:
    """
    Return the name of the samples and their stream if necessary
    """
    if "Downstream_file" in design.columns.to_list():
        return  [
            f"{s}.R{r}"
            for s in design.Sample_id,
            for r in ["1", "2"]
        ]
    return design.Sample_id.tolist()


def fq_link(design: pandas.DataFrame) -> Dict[str, str]:
    """
    Return a dictionnary containing the file name as it is expected in the
    pipeline, and the original file path
    """
    fq_link_dict = {}
    try:
        # Pair-ended case
        design_iterator = zip(
            design.Sample_id,
            design.Upstream_file,
            design.Downstream_file
        )

        for sample, up, down in design_iterator:
            fq_link_dict[f"{sample}_R1.fastq.gz"] = up
            fq_link_dict[f"{sample}_R2.fastq.gz"] = down
    except AttributeError:
        fq_link_dict = {
            f"{sample}.fastq.gz": fq
            for sample, fq in zip(design.Sample_id, design.Upstream_file)
        }

    return fq_link_dict
