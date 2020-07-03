Material and Methods:
#####################

Raw `fastq <https://en.wikipedia.org/wiki/FASTQ_format>`_ files were trimmed by `fastp <https://github.com/OpenGene/fastp>`_ using extra parameters shown below. In parallel, contamination was tested with `FastqScreen <https://www.bioinformatics.babraham.ac.uk/projects/fastq_screen/>`_ using optional parameters listed below.

* fastp optional parameters: `{{snakemake.config.params.fastp_extra}}`
* FastqScreen optional parameters: `{{snakemake.config.params.fastqscreen_extra}}`

The whole pipeline was powered by both `Snakemake <https://snakemake.readthedocs.io>`_ , and `Snakemake Wrappers <https://snakemake-wrappers.readthedocs.io/>`_ .


Citations:
##########

Fastp:

    Fastp is a tool which performs both quality control assessment and cleaning. It provides a convenient environment to compare before and after trimming qualities.

    Pearson, William R. "[5] Rapid and sensitive sequence comparison with FASTP and FASTA." (1990): 63-98.

    Chen, Shifu, et al. "fastp: an ultra-fast all-in-one FASTQ preprocessor." Bioinformatics 34.17 (2018): i884-i890.

FastQ Screen:

    FastQ Screen is a tool which maps a user-defined subset of reads to various genomes in order to guess if there is any contamination in a provided fastq file.

    Wingett, Steven W., and Simon Andrews. "FastQ Screen: A tool for multi-genome mapping and quality control." F1000Research 7 (2018).
