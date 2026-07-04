
## Tool versions
- sra-tools (prefetch/fasterq-dump): 3.4.1
- FastQC: 0.12.1

## Data acquisition note
Raw FASTQ obtained via direct download from ENA (European Nucleotide Archive),
which serves pre-converted FASTQ.gz directly (no SRA-format intermediate).
Equivalent underlying sequencing data to SRA accessions SRR1039508/09/12/13/16/17/20/21.
Switched from SRA-tools (prefetch/fasterq-dump) due to local disk I/O bottleneck
during SRA-to-FASTQ conversion.

## Quality Control — Interpretation

**Read length:** 63bp (paired-end), shorter than typical for the era. This is
expected — per the original study's processing notes, the first 12bp of each
75bp read were trimmed by the authors prior to SRA deposit due to 5' sequence
bias, hence the shorter deposited read length.

**Per-base sequence quality:** All 16 samples show Phred ≥30 across nearly the
full read length. No quality-based trimming required.

**Adapter content:** Near-zero across all samples (trivial rise to ~1% by
position 45), consistent with insert sizes longer than read length. No adapter
trimming required.

**Sequence duplication levels:** FastQC flags 46-57% duplication (red/amber)
for all 16 samples. This is expected for RNA-seq and is NOT treated as a
quality failure: duplication in RNA-seq reflects genuine differences in
transcript abundance rather than PCR artifacts (the DNA-seq assumption FastQC's
thresholds are calibrated for). The duplication-level distribution shows the
expected bimodal RNA-seq pattern — ~30-40% unique reads, sharp drop-off through
low duplication levels, then a distinct secondary peak (~15-20% of reads) in
the >10 to >100 duplication bins. This secondary peak is consistent with a
small number of highly-expressed transcripts (e.g. housekeeping and
structural/contractile genes, expected in airway smooth muscle cells)
each contributing many identical reads — not PCR over-amplification, which
would instead concentrate reads at extreme duplication levels (>1k, >10k+)
with little unique-read background.

**Decision: no deduplication step applied prior to alignment/quantification.**
Removing "duplicate" reads at this stage would discard genuine biological
signal from highly-expressed genes, which is the opposite of standard RNA-seq
practice. This is consistent with ENCODE RNA-seq processing standards and
general field convention (deduplication is applied in DNA-seq/variant-calling
contexts, not standard bulk RNA-seq differential expression workflows).

**Conclusion:** raw data quality is clean across all metrics. No trimming
needed before Day 2 alignment.

## Alignment Results (HISAT2, GRCh38 + Ensembl release 84 annotation)

| Sample | Overall Alignment Rate |
|---|---|
| SRR1039508 | 97.06% |
| SRR1039509 | 95.95% |
| SRR1039512 | 97.75% |
| SRR1039513 | 97.30% |
| SRR1039516 | 97.30% |
| SRR1039517 | 97.51% |
| SRR1039520 | 97.36% |
| SRR1039521 | 97.16% |

All 8 samples show consistent alignment rates (95.95%–97.75%), well within
expected range for clean human RNA-seq against a correctly matched reference.
No outlier samples flagged at this stage.

## Strandedness Inference (RSeQC infer_experiment.py)

All 8 samples show near-equal fractions (~40-45% each) between the two
strand-specific read categories, with no sample showing a dominant pattern
(which would indicate ~90%+ in one category). This confirms the library is
**unstranded**, consistent with standard (non-strand-specific) library prep
protocols common at the time of the original study (2014), predating the
widespread adoption of strand-specific kits.

**Decision:** featureCounts run with `-s 0` (unstranded) for all 8 samples.
