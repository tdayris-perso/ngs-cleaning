#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

"""
This script aims to prepare the configuration file used
by the ngs-cleaning pipeline

It goes through the arguments passed in command line and
builds a yaml formatted text file used as a configuration
file for the snakemake pipeline.

You can test this script with:
pytest -v ./prepare_config.py

Usage example:
# Whole pipeline with default parameters
python3.7 ./prepare_config.py
"""


import argparse  # Parse command line
import logging  # Traces and loggings
import os  # OS related activities
import pytest  # Unit testing
import shlex  # Lexical analysis
import sys  # System related methods
import yaml  # Parse Yaml files

from pathlib import Path  # Paths related methods
from snakemake.utils import makedirs  # Easily build directories
from typing import Dict, Any  # Typing hints

from common_script_ngs_cleaning import CustomFormatter, write_yaml


def parser() -> argparse.ArgumentParser:
    """
    Build the argument parser object
    """
    main_parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter,
        epilog="This script does not make any magic. Please check the prepared"
        " configuration file!",
    )

    # Parsing optional arguments
    main_parser.add_argument(
        "--design",
        help="Path to design file (default: %(default)s)",
        type=str,
        metavar="PATH",
        default="design.tsv",
    )

    main_parser.add_argument(
        "--workdir",
        help="Path to working directory (default: %(default)s)",
        type=str,
        metavar="PATH",
        default=".",
    )

    main_parser.add_argument(
        "--threads",
        help="Maximum number of threads used (default: %(default)s)",
        type=int,
        default=1,
    )

    main_parser.add_argument(
        "--singularity",
        help="Docker/Singularity image (default: %(default)s)",
        type=str,
        default="docker://continuumio/miniconda3:4.4.10",
    )

    main_parser.add_argument(
        "--cold-storage",
        help="Space separated list of absolute path to "
        "cold storage mount points (default: %(default)s)",
        nargs="+",
        type=str,
        default=[" "],
    )

    main_parser.add_argument(
        "--copy-extra",
        help="Extra parameters for bash copy "
             "contaminations (default: %(default)s)",
        type=str,
        default="--verbose"
    )

    main_parser.add_argument(
        "--run-fqscreen",
        help="Whether to run fastq screen or not",
        default=False,
        action="store_true"
    )

    main_parser.add_argument(
        "--fastq-screen-subset",
        help="Number of reads that FastQ Screen will use while looking for "
             "contaminations (default: %(default)s)",
        type=int,
        default=100000
    )

    main_parser.add_argument(
        "--fastq-screen-aligner",
        help="Name of the mapper used by FastQ Screen (default: %(default)s)",
        type=str,
        default="bowtie2",
        choices={"bowtie2", "bowtie"}
    )

    main_parser.add_argument(
        "--fastq-screen-config",
        help="Path to FastQ Screen tsv configuration file "
             "(default: %(default)s)",
        type=str,
        default="fastq_screen_config.tsv"
    )

    # Fastp options
    fastp = main_parser.add_mutually_exclusive_group()
    fastp.add_argument(
        "--fastp-extra",
        help="Extra parameters for fastp trimmer (default: %(default)s)",
        type=str,
        default="--overrepresentation_analysis"
    )

    fastp.add_argument(
        "--soft-trimmer",
        help="Use our preset for soft trimming: cut mean quality of 10 in a "
             "window of 6 bases, allow up to 50% of bases with qualities "
             "below 10, allow a most 7 Ns, no average quality threshold, "
             "minimum read length of 15.",
        action="store_true",
        default=False
    )

    fastp.add_argument(
        "--medium-trimmer",
        help="Use our preset for soft trimming: Cut mean quality of 15 in a "
             "window of 5 bases, allow 40% of bases with quality below 10, "
             "allow up to 7 Ns, remove reads with average quality of 10, "
             "minimum read length is 30, filter out reads with a "
             "complexity below 10%.",
        action="store_true",
        default=False
    )

    fastp.add_argument(
        "--hard-trimmer",
        help="Use our preset for soft trimming: Remove polyG, cut mean "
             "quality of 20 in a window of 5, remove reads with more than "
             "30% of reads with quality below 10, remove reads with at most "
             "5 Ns, remove reads with average quality below 15, remove reads"
             " smaller than 30 bases, remove reads with a complexity "
             "below 30%",
        action="store_true",
        default=False
    )

    # Logging options
    log = main_parser.add_mutually_exclusive_group()
    log.add_argument(
        "-d",
        "--debug",
        help="Set logging in debug mode",
        default=False,
        action="store_true",
    )

    log.add_argument(
        "-q",
        "--quiet",
        help="Turn off logging behaviour",
        default=False,
        action="store_true",
    )

    return main_parser


# Argument parsing functions
def parse_args(args: Any = sys.argv[1:]) -> argparse.ArgumentParser:
    """
    This function parses command line arguments

    Parameters
        args     Any             All command line arguments

    Return
                ArgumentParser   A object designed to parse the command line

    Example:
    >>> parse_args(shlex.split("/path/to/fasta --no-fastqc"))
    Namespace(aggregate=False, cold_storage=[' '], debug=False,
    design='design.tsv', fasta='/path/to/fasta', gtf=None, libType='A',
    no_fastqc=False, no_multiqc=False, quiet=False, salmon_index_extra='
    --keepDuplicates --gencode --perfectHash', salmon_quant_extra='
    --numBootstraps 100 --validateMappings --gcBias --seqBias',
    singularity='docker://continuumio/miniconda3:4.4.10',
    threads=1, workdir='.')
    """
    return parser().parse_args(args)


def test_parse_args() -> None:
    """
    This function tests the command line parsing

    Example:
    >>> pytest -v prepare_config.py -k test_parse_args
    """
    options = parse_args(shlex.split(""))
    expected = argparse.Namespace(
        cold_storage=[' '],
        copy_extra="--verbose",
        debug=False,
        design='design.tsv',
        fastp_extra='--overrepresentation_analysis',
        fastq_screen_aligner='bowtie2',
        fastq_screen_config='fastq_screen_config.tsv',
        fastq_screen_subset=100000,
        hard_trimmer=False,
        medium_trimmer=False,
        quiet=False,
        run_fqscreen=False,
        singularity='docker://continuumio/miniconda3:4.4.10',
        soft_trimmer=False,
        threads=1,
        workdir='.'
    )
    assert options == expected


# Building pipeline configuration from command line
def args_to_dict(args: argparse.ArgumentParser) -> Dict[str, Any]:
    """
    Parse command line arguments and return a dictionnary ready to be
    dumped into yaml

    Parameters:
        args        ArgumentParser      Parsed arguments from command line

    Return:
                    Dict[str, Any]      A dictionnary containing the parameters
                                        for the pipeline
    """
    fastp_extra = args.fastp_extra
    if args.soft_trimmer is True:
        fastp_extra = (
            "--cut_front "
            "--cut_tail "
            "--cut_window_size 6 "
            "--cut_mean_quality 10 "
            "--unqualified_percent_limit 50 "
            "--n_base_limit 7 "
            "--average_qual 0 "
            "--length_required 15 "
            "--overrepresentation_analysis"
        )
    elif args.medium_trimmer is True:
        fastp_extra = (
            "--cut_front "
            "--cut_tail "
            "--cut_window_size 5 "
            "--cut_mean_quality 15 "
            "--unqualified_percent_limit 40 "
            "--n_base_limit 7 "
            "--average_qual 10 "
            "--length_required 30 "
            "--low_complexity_filter "
            "--complexity_threshold 10 "
            "--overrepresentation_analysis"
        )
    elif args.hard_trimmer is True:
        fastp_extra = (
            "--trim_poly_g "
            "--cut_front "
            "--cut_tail "
            "--cut_window_size 5 "
            "--cut_mean_quality 20 "
            "--unqualified_percent_limit 30 "
            "--n_base_limit 5 "
            "--average_qual 15 "
            "--length_required 30 "
            "--low_complexity_filter "
            "--complexity_threshold 30 "
            "--overrepresentation_analysis"
        )

    result_dict = {
        "design": os.path.abspath(args.design),
        "config": os.path.abspath(os.path.join(args.workdir, "config.yaml")),
        "workdir": os.path.abspath(args.workdir),
        "threads": args.threads,
        "singularity_docker_image": args.singularity,
        "cold_storage": args.cold_storage,
        "run_fqscreen": args.run_fqscreen,
        "params": {
            "copy_extra": args.copy_extra,
            "fastp_extra": fastp_extra,
            "fastq_screen_subset": args.fastq_screen_subset,
            "fastq_screen_aligner": args.fastq_screen_aligner,
            "fastq_screen_config": args.fastq_screen_config
        },
    }
    logging.debug(result_dict)
    return result_dict


@pytest.mark.parametrize(
    "options, expected", [
        (
            argparse.Namespace(
                cold_storage=[' '],
                copy_extra="--verbose",
                debug=False,
                design='design.tsv',
                fastp_extra='--overrepresentation_analysis',
                fastq_screen_aligner='bowtie2',
                fastq_screen_config='fastq_screen_config.tsv',
                fastq_screen_subset=100000,
                hard_trimmer=False,
                medium_trimmer=False,
                quiet=False,
                singularity='docker://continuumio/miniconda3:4.4.10',
                soft_trimmer=False,
                run_fqscreen=True,
                threads=1,
                workdir='.'
            ),
            {
                "design": os.path.abspath('design.tsv'),
                "config": os.path.abspath("config.yaml"),
                "workdir": os.path.abspath("."),
                "threads": 1,
                "singularity_docker_image": 'docker://continuumio/miniconda3:4.4.10',
                "cold_storage": [' '],
                "run_fqscreen": True,
                "params": {
                    "copy_extra": "--verbose",
                    "fastp_extra": '--overrepresentation_analysis',
                    "fastq_screen_subset": 100000,
                    "fastq_screen_aligner": 'bowtie2',
                    "fastq_screen_config": 'fastq_screen_config.tsv'
                },
            }
        ),

        (
            argparse.Namespace(
                cold_storage=[' '],
                copy_extra="--verbose",
                debug=False,
                design='design.tsv',
                fastp_extra='--overrepresentation_analysis',
                fastq_screen_aligner='bowtie2',
                fastq_screen_config='fastq_screen_config.tsv',
                fastq_screen_subset=100000,
                hard_trimmer=False,
                medium_trimmer=True,
                run_fqscreen=True,
                quiet=False,
                singularity='docker://continuumio/miniconda3:4.4.10',
                soft_trimmer=False,
                threads=1,
                workdir='.'
            ),
            {
                "design": os.path.abspath('design.tsv'),
                "config": os.path.abspath("config.yaml"),
                "workdir": os.path.abspath("."),
                "threads": 1,
                "singularity_docker_image": 'docker://continuumio/miniconda3:4.4.10',
                "cold_storage": [' '],
                "run_fqscreen": True,
                "params": {
                    "copy_extra": "--verbose",
                    "fastp_extra": (
                        "--cut_front "
                        "--cut_tail "
                        "--cut_window_size 5 "
                        "--cut_mean_quality 15 "
                        "--unqualified_percent_limit 40 "
                        "--n_base_limit 7 "
                        "--average_qual 10 "
                        "--length_required 30 "
                        "--low_complexity_filter "
                        "--complexity_threshold 10 "
                        "--overrepresentation_analysis"
                    ),
                    "fastq_screen_subset": 100000,
                    "fastq_screen_aligner": 'bowtie2',
                    "fastq_screen_config": 'fastq_screen_config.tsv'
                },
            }
        ),
    ]
)
def test_args_to_dict(options: argparse.Namespace, expected: Dict[str, Any]) -> None:
    """
    This function simply tests the args_to_dict function with expected output

    Example:
    >>> pytest -v prepare_config.py -k test_args_to_dict
    """
    assert args_to_dict(options) == expected


# Yaml formatting
def dict_to_yaml(indict: Dict[str, Any]) -> str:
    """
    This function makes the dictionnary to yaml formatted text

    Parameters:
        indict  Dict[str, Any]  The dictionnary containing the pipeline
                                parameters, extracted from command line

    Return:
                str             The yaml formatted string, directly built
                                from the input dictionnary

    Examples:
    >>> import yaml
    >>> example_dict = {
        "bar": "bar-value",
        "foo": ["foo-list-1", "foo-list-2"]
    }
    >>> dict_to_yaml(example_dict)
    'bar: bar-value\nfoo:\n- foo-list-1\n- foo-list-2\n'
    >>> print(dict_to_yaml(example_dict))
    bar: bar-value
    foo:
    - foo-list-1
    - foo-list-2
    """
    return yaml.dump(indict, default_flow_style=False)


def test_dict_to_yaml() -> None:
    """
    This function tests the dict_to_yaml function with pytest

    Example:
    >>> pytest -v prepare_config.py -k test_dict_to_yaml
    """
    expected = "bar: bar-value\nfoo:\n- foo-list-1\n- foo-list-2\n"
    example_dict = {"bar": "bar-value", "foo": ["foo-list-1", "foo-list-2"]}
    assert dict_to_yaml(example_dict) == expected


# Core of this script
def main(args: argparse.ArgumentParser) -> None:
    """
    This function performs the whole configuration sequence

    Parameters:
        args    ArgumentParser      The parsed command line

    Example:
    >>> main(parse_args(shlex.split("/path/to/fasta")))
    """
    # Building pipeline arguments
    logging.debug("Building configuration file:")
    config_params = args_to_dict(args)
    output_path = Path(args.workdir) / "config.yaml"

    # Saving as yaml
    with output_path.open("w") as config_yaml:
        logging.debug(f"Saving results to {str(output_path)}")
        config_yaml.write(dict_to_yaml(config_params))


# Running programm if not imported
if __name__ == "__main__":
    # Parsing command line
    args = parse_args()
    makedirs("logs/prepare")

    # Build logging object and behaviour
    logging.basicConfig(
        filename="logs/prepare/config.log", filemode="w", level=logging.DEBUG
    )

    try:
        logging.debug("Preparing configuration")
        main(args)
    except Exception as e:
        logging.exception("%s", e)
        raise
    sys.exit(0)
