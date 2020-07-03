rule fastp_trimmer:
    input:
        sample = unpack(fq_pairs_w)
    output:
        trimmed = [
            "fastp/trimmed/{sample}.R1.fastq.gz",
            "fastp/trimmed/{sample}.R2.fastq.gz"
        ],
        html = report(
            "fastp/html/{sample}.fastp.html",
            captions="../report/fastp.rst",
            category="Quality controls"
        ),
        json = temp("fastp/json/{sample}.fastp.json")
    message:
        "Trimming and controling quality of {wildcards.sample}"
    threads:
        min(config.get("threads", 10), 10)
    params:
        extra = config["params"].get("fastp_extra", "")
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048, 20480)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 20, 200)
        )
    log:
        "logs/fastp/{sample}.log"
    wrapper:
        f"{git}/bio/fastp"
