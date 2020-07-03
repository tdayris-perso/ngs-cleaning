rule multiqc:
    input:
        fastp_json = expand(
            "fastp/{format}/{sample}.{format}",
            sample=design.Sample_id,
            format=["json", "html"]
        ),
        fq_screen = expand(
            "fqscreen/{rsample}.fastq_screen.{format}",
            rsample=rsample_list,
            format=["png", "txt"]
        )
    output:
        report(
            "multiqc/report.html",
            caption="../report/multiqc.rst",
            category="Results"
        )
    message:
        "Building quality report"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 1024, 10240)
        ),
        time_min = (
            lambda wildcards, attempt: attempt * 30
        )
    params:
        extra = config["params"].get("multiqc_extra", "")
    log:
        "logs/multiqc.log"
    wrapper:
        f"{git}/bio/multiqc"
