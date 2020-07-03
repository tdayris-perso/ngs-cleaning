"""
While other .smk files contains rules and pure snakemake instructions, this
one gathers all the python instructions surch as config mappings or input
validations.
"""

from typing import Any, List

from common_ngs_cleaning import sample_stream, fastq_pairs


rsample_list = sample_stream(design)
fastq_pairs_dict = fastq_pairs(design)

wildcard_constraints:
    sample = "|"join(design.Sample_id),
    rsample = "|".join(rsample_list),
    stream = "R1|R2,
    format = "|".join(["txt", "png", "html", "json"])


def fq_pairs_w(wildcards: Any) -> List[str]:
    """
    Return the list of samples related to a given sample name
    """
    return fastq_pairs_dict[wildcards.sample]


def get_targets(get_trimmed: bool = False,
                get_fqscreen: bool = False,
                get_fastp: bool = False,
                get_multiqc: bool = False):
    targets = dict()

    if get_trimmed is True:
        targets["trimmed"] = expand(
            "fastp/trimmed/{rsample}.fastq.gz",
            rsample=rsample_list
        )

    if get_fastp is True:
        targets["fastp_reports"] = expand(
            "fastp/{format}/{sample}.{format}",
            sample=design.Sample_id,
            format=["json", "html"]
        )

    if get_fqscreen is True:
        targets["fastq_screen"] = expand(
            "fqscreen/{rsample}.fastq_screen.{format}",
            rsample=rsample_list,
            format=["png", "txt"]
        )

    if get_multiqc is True:
        targets["multiqc"] = "multiqc/report.html"

    return targets
