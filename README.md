
## Tool versions
- sra-tools (prefetch/fasterq-dump): 3.4.1
- FastQC: 0.12.1

## Data acquisition note
Raw FASTQ obtained via direct download from ENA (European Nucleotide Archive),
which serves pre-converted FASTQ.gz directly (no SRA-format intermediate).
Equivalent underlying sequencing data to SRA accessions SRR1039508/09/12/13/16/17/20/21.
Switched from SRA-tools (prefetch/fasterq-dump) due to local disk I/O bottleneck
during SRA-to-FASTQ conversion.

## Day 1 QC interpretation

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
