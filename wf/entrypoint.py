import os
import shutil
import subprocess
import typing
from pathlib import Path

import requests
import typing_extensions
from flytekit.core.annotation import FlyteAnnotation
from latch.ldata.path import LPath
from latch.resources.tasks import custom_task, nextflow_runtime_task
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchDir
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)


@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(
    pvc_name: str,
    outdir: typing.Optional[
        typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})]
    ],
    email: typing.Optional[str],
    bigwig: typing.Optional[bool],
    genome: typing.Optional[str],
    fasta: typing.Optional[str],
    gtf: typing.Optional[str],
    star_index: typing.Optional[str],
    bowtie_index: typing.Optional[str],
    save_reference: typing.Optional[bool],
    save_trimmed: typing.Optional[bool],
    trim_ecop: typing.Optional[bool],
    trim_linker: typing.Optional[bool],
    trim_5g: typing.Optional[bool],
    trim_artifacts: typing.Optional[bool],
    remove_ribo_rna: typing.Optional[bool],
    save_non_ribo_reads: typing.Optional[bool],
    skip_initial_fastqc: typing.Optional[bool],
    skip_trimming: typing.Optional[bool],
    skip_trimming_fastqc: typing.Optional[bool],
    skip_alignment: typing.Optional[bool],
    skip_samtools_stats: typing.Optional[bool],
    skip_ctss_generation: typing.Optional[bool],
    skip_ctss_qc: typing.Optional[bool],
    input: str,
    aligner: typing.Optional[str],
    min_aln_length: typing.Optional[int],
    eco_site: typing.Optional[str],
    linker_seq: typing.Optional[str],
    artifacts_5end: typing.Optional[str],
    artifacts_3end: typing.Optional[str],
    ribo_database_manifest: typing.Optional[str],
    min_cluster: typing.Optional[int],
    tpm_cluster_threshold: typing.Optional[float],
) -> None:
    try:
        shared_dir = Path("/nf-workdir")

        ignore_list = [
            "latch",
            ".latch",
            "nextflow",
            ".nextflow",
            "work",
            "results",
            "miniconda",
            "anaconda3",
            "mambaforge",
        ]

        shutil.copytree(
            Path("/root"),
            shared_dir,
            ignore=lambda src, names: ignore_list,
            ignore_dangling_symlinks=True,
            dirs_exist_ok=True,
        )

        cmd = [
            "/root/nextflow",
            "run",
            str(shared_dir / "main.nf"),
            "-work-dir",
            str(shared_dir),
            "-profile",
            "docker",
            "-c",
            "latch.config",
            *get_flag("input", input),
            *get_flag("outdir", outdir),
            *get_flag("email", email),
            *get_flag("bigwig", bigwig),
            *get_flag("aligner", aligner),
            *get_flag("min_aln_length", min_aln_length),
            *get_flag("genome", genome),
            *get_flag("fasta", fasta),
            *get_flag("gtf", gtf),
            *get_flag("star_index", star_index),
            *get_flag("bowtie_index", bowtie_index),
            *get_flag("save_reference", save_reference),
            *get_flag("save_trimmed", save_trimmed),
            *get_flag("trim_ecop", trim_ecop),
            *get_flag("trim_linker", trim_linker),
            *get_flag("trim_5g", trim_5g),
            *get_flag("trim_artifacts", trim_artifacts),
            *get_flag("eco_site", eco_site),
            *get_flag("linker_seq", linker_seq),
            *get_flag("artifacts_5end", artifacts_5end),
            *get_flag("artifacts_3end", artifacts_3end),
            *get_flag("remove_ribo_rna", remove_ribo_rna),
            *get_flag("save_non_ribo_reads", save_non_ribo_reads),
            *get_flag("ribo_database_manifest", ribo_database_manifest),
            *get_flag("min_cluster", min_cluster),
            *get_flag("tpm_cluster_threshold", tpm_cluster_threshold),
            *get_flag("skip_initial_fastqc", skip_initial_fastqc),
            *get_flag("skip_trimming", skip_trimming),
            *get_flag("skip_trimming_fastqc", skip_trimming_fastqc),
            *get_flag("skip_alignment", skip_alignment),
            *get_flag("skip_samtools_stats", skip_samtools_stats),
            *get_flag("skip_ctss_generation", skip_ctss_generation),
            *get_flag("skip_ctss_qc", skip_ctss_qc),
        ]

        print("Launching Nextflow Runtime")
        print(" ".join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(
                    urljoins(
                        "latch:///your_log_dir/nf_nf_core_cageseq", name, "nextflow.log"
                    )
                )
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)


@workflow(metadata._nextflow_metadata)
def nf_nf_core_cageseq(
    outdir: typing.Optional[
        typing_extensions.Annotated[LatchDir, FlyteAnnotation({"output": True})]
    ],
    email: typing.Optional[str],
    bigwig: typing.Optional[bool],
    genome: typing.Optional[str],
    fasta: typing.Optional[str],
    gtf: typing.Optional[str],
    star_index: typing.Optional[str],
    bowtie_index: typing.Optional[str],
    save_reference: typing.Optional[bool],
    save_trimmed: typing.Optional[bool],
    trim_ecop: typing.Optional[bool],
    trim_linker: typing.Optional[bool],
    trim_5g: typing.Optional[bool],
    trim_artifacts: typing.Optional[bool],
    remove_ribo_rna: typing.Optional[bool],
    save_non_ribo_reads: typing.Optional[bool],
    skip_initial_fastqc: typing.Optional[bool],
    skip_trimming: typing.Optional[bool],
    skip_trimming_fastqc: typing.Optional[bool],
    skip_alignment: typing.Optional[bool],
    skip_samtools_stats: typing.Optional[bool],
    skip_ctss_generation: typing.Optional[bool],
    skip_ctss_qc: typing.Optional[bool],
    input: str = "data/*R1.fastq.gz",
    aligner: typing.Optional[str] = "star",
    min_aln_length: typing.Optional[int] = 15,
    eco_site: typing.Optional[str] = "CAGCAG",
    linker_seq: typing.Optional[str] = "TCGTATGCCGTCTTC",
    artifacts_5end: typing.Optional[str] = "$projectDir/assets/artifacts_5end.fasta",
    artifacts_3end: typing.Optional[str] = "$projectDir/assets/artifacts_3end.fasta",
    ribo_database_manifest: typing.Optional[
        str
    ] = "$projectDir/assets/rrna-db-defaults.txt",
    min_cluster: typing.Optional[int] = 30,
    tpm_cluster_threshold: typing.Optional[float] = 0.2,
) -> None:
    """
    nf-core/cageseq

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(
        pvc_name=pvc_name,
        input=input,
        outdir=outdir,
        email=email,
        bigwig=bigwig,
        aligner=aligner,
        min_aln_length=min_aln_length,
        genome=genome,
        fasta=fasta,
        gtf=gtf,
        star_index=star_index,
        bowtie_index=bowtie_index,
        save_reference=save_reference,
        save_trimmed=save_trimmed,
        trim_ecop=trim_ecop,
        trim_linker=trim_linker,
        trim_5g=trim_5g,
        trim_artifacts=trim_artifacts,
        eco_site=eco_site,
        linker_seq=linker_seq,
        artifacts_5end=artifacts_5end,
        artifacts_3end=artifacts_3end,
        remove_ribo_rna=remove_ribo_rna,
        save_non_ribo_reads=save_non_ribo_reads,
        ribo_database_manifest=ribo_database_manifest,
        min_cluster=min_cluster,
        tpm_cluster_threshold=tpm_cluster_threshold,
        skip_initial_fastqc=skip_initial_fastqc,
        skip_trimming=skip_trimming,
        skip_trimming_fastqc=skip_trimming_fastqc,
        skip_alignment=skip_alignment,
        skip_samtools_stats=skip_samtools_stats,
        skip_ctss_generation=skip_ctss_generation,
        skip_ctss_qc=skip_ctss_qc,
    )
