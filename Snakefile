import snakemake.utils  # Load snakemake API
import sys              # System related operations

# Python 3.8 is required
if sys.version_info < (3, 8):
    raise SystemError("Please use Python 3.8 or later.")

# Snakemake 5.14.0 at least is required
snakemake.utils.min_version("5.19.3")

include: "rules/common.smk"
include: "rules/copy.smk"
include: "rules/fastp.smk"
include: "rules/fastq_screen.smk"
include: "rules/multiqc.smk"


workdir: config["workdir"]
container: config["singularity_docker_image"]
localrules: copy_fastq


rule all:
    input:
        **get_targets(
            get_trimmed=True,
            get_fqscreen=True,
            get_fastp=True,
            get_multiqc=True
        )
    message:
        "Finishing the NGS Quality Control assessment and Cleaning pipeline"
