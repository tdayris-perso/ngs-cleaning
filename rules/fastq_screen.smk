rule fastq_screen:
    input:
        "fastp/trimmed/{rsample}.fastq.gz"
    output:
        txt = temp("fqscreen/{rsample}.fastq_screen.txt"),
        png = temp("fqscreen/{rsample}.fastq_screen.png")
    message:
        "Screening {wildcards.rsample}"
    params:
        subset = config["params"].get("fastq_screen_subset", 100000),
        fastq_screen_config = config["params"].get(
            "fastq_screen_config", "fastq_screen_config.tsv"
        ),
        # fastq_screen_config = {
        #     "database": {
        #         "Human": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Human/Homo_sapiens.GRCh38"},
        #         "Mouse": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Mouse/Mus_musculus.GRCm38"},
        #         "Rat": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Rat/Rnor_6.0"},
        #         "Drosophila": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Drosophila/BDGP6"},
        #         "Worm": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Worm/Caenorhabditis_elegans.WBcel235"},
        #         "Yeast": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Yeast/Saccharomyces_cerevisiae.R64-1-1"},
        #         "Arabidopsis": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Arabidopsis/Arabidopsis_thaliana.TAIR10"},
        #         "Ecoli": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/E_coli/Ecoli"},
        #         "rRNA": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/rRNA/GRCm38_rRNA"},
        #         "MT": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Mitochondria/mitochondria"},
        #         "PhiX": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/PhiX/phi_plus_SNPs"},
        #         "Lambda": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Lambda/Lambda"},
        #         "Vectors": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Vectors/Vectors"},
        #         "Adapters": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Adapters/Contaminants"},
        #         "SalmoSalar": {"bowtie2": "/mnt/beegfs/database/bioinfo/Index_DB/FastQ_Screen/0.13.0/Salmo_salar/SalmoSalar.ICSASGv2"},
        #     },
        #     "aligner_paths": {'bowtie': 'bowtie', 'bowtie2': 'bowtie2'}
        # },
        aligner = config["params"].get("fastq_screen_aligner", 'bowtie2')
    threads:
        min(config.get("threads", 20), 20)
    resources:
        mem_mb = (
                lambda wildcards, attempt: min(10240 * attempt, 15360)
            ),
        time_min = (
            lambda wildcards, attempt: 115 * attempt
        )
    log:
        "logs/fastq_screen/{rsample}.log"
    wrapper:
        f"{git}/bio/fastq_screen"
