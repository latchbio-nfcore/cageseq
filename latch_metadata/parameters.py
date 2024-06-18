
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input': NextflowParameter(
        type=str,
        default='data/*R1.fastq.gz',
        section_title='Input/output options',
        description='Input FastQ files.',
    ),
    'outdir': NextflowParameter(
        type=typing.Optional[typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})]],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'bigwig': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Specifies if TSS-bigwigs should be generated, additionally to the TSS-bed files',
    ),
    'aligner': NextflowParameter(
        type=typing.Optional[str],
        default='star',
        section_title='Alignment options',
        description='Alignment tool to be used',
    ),
    'min_aln_length': NextflowParameter(
        type=typing.Optional[int],
        default='15',
        section_title=None,
        description='Minimum number of aligned basepairs of a read to be kept',
    ),
    'genome': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Reference genome options',
        description='Name of iGenomes reference.',
    ),
    'fasta': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to FASTA genome file.',
    ),
    'gtf': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to gtf file.',
    ),
    'star_index': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to star index directory.',
    ),
    'bowtie_index': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to bowtie index directory.',
    ),
    'save_reference': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='All generated reference files will be saved to the results folder if this flag is set.',
    ),
    'save_trimmed': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Trimming options',
        description=None,
    ),
    'trim_ecop': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description="Set to cut the enzyme binding site at the 5' end",
    ),
    'trim_linker': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description="Select to cut the linker at the 3' end",
    ),
    'trim_5g': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description="Trim the first `G` at the 5' end, if available",
    ),
    'trim_artifacts': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Artifacts, generated in the sequencing process, are cut if this flag is not set to false.',
    ),
    'eco_site': NextflowParameter(
        type=typing.Optional[str],
        default='CAGCAG',
        section_title=None,
        description="Sequence of the ecoP15 site at the 5' end",
    ),
    'linker_seq': NextflowParameter(
        type=typing.Optional[str],
        default='TCGTATGCCGTCTTC',
        section_title=None,
        description="Sequence of the linker at the 3' end",
    ),
    'artifacts_5end': NextflowParameter(
        type=typing.Optional[str],
        default='$projectDir/assets/artifacts_5end.fasta',
        section_title=None,
        description="Path to 5' end artifacts",
    ),
    'artifacts_3end': NextflowParameter(
        type=typing.Optional[str],
        default='$projectDir/assets/artifacts_3end.fasta',
        section_title=None,
        description="Path to 3' end artifacts",
    ),
    'remove_ribo_rna': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Ribosomal RNA removal options',
        description='Select to remove ribosoamal reads with SortMeRNA',
    ),
    'save_non_ribo_reads': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Select to save the ribosomal-free reads',
    ),
    'ribo_database_manifest': NextflowParameter(
        type=typing.Optional[str],
        default='$projectDir/assets/rrna-db-defaults.txt',
        section_title=None,
        description='Path to SortMeRNA database file',
    ),
    'min_cluster': NextflowParameter(
        type=typing.Optional[int],
        default=30,
        section_title='CAGE-tag clustering options',
        description='Minimum cluster size',
    ),
    'tpm_cluster_threshold': NextflowParameter(
        type=typing.Optional[float],
        default=0.2,
        section_title=None,
        description='Minimum tags per million a cluster has to have',
    ),
    'skip_initial_fastqc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Process skipping options',
        description='Skip FastQC run on input reads.',
    ),
    'skip_trimming': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip all trimming steps.',
    ),
    'skip_trimming_fastqc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip FastQC run on trimmed reads.',
    ),
    'skip_alignment': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip alignment step.',
    ),
    'skip_samtools_stats': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip samtools stats QC step of aligned reads',
    ),
    'skip_ctss_generation': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip steps generating CTSS files including clustering, bed/bigwig and count table output generation.',
    ),
    'skip_ctss_qc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description="Skip running RSeQC's read distribution QC step on the clustered CTSS.",
    ),
}

