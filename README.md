
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

## Quantification (featureCounts)

All 8 samples quantified with featureCounts v2.1.1, using `-p --countReadPairs`
(fragment-level counting; note this changed from `-p` alone in subread v2.0.2+)
and `-s 0` (unstranded, per RSeQC inference above), against the same Ensembl
release 84 GTF used for alignment.

SRR1039508 (validated in detail): 77.5% assigned. Remaining unassigned reads
distributed across expected categories — multi-mapping (~12.5%, expected given
paralogous genes/repetitive elements), no-feature (~4%, intronic/intergenic
background), and ambiguity (~4.6%, real biological gene overlap). All 8 samples
show consistent Assigned % and category proportions (confirmed via MultiQC),
no outlier samples.

## R Environment

R package management handled via `renv` (renv.lock committed), separate from
the conda environment used for command-line tools (HISAT2, samtools,
featureCounts, etc. — see environment.yml). This split reflects standard
practice: conda/bioconda for the pipeline toolchain, renv for the R/statistics
layer, since RStudio's ecosystem is built natively around renv.

**System dependencies required** (Ubuntu) for R graphics packages (ggplot2 and
its dependencies systemfonts/textshaping): `libfontconfig1-dev`,
`libharfbuzz-dev`, `libfribidi-dev`, `libfreetype6-dev`, `libpng-dev`,
`libtiff5-dev`, `libjpeg-dev`. Install via apt before running `renv::restore()`
on a fresh machine.

## Validation: CRISPLD2 upregulation under dexamethasone

Himes et al. 2014 identified **CRISPLD2** as significantly upregulated under
dexamethasone treatment in airway smooth muscle cells, confirmed by qPCR and
Western blot. This serves as the primary validation target for this dry-run
pipeline — reproducing this specific, published result from raw FASTQ files
confirms the full pipeline (acquisition → alignment → quantification →
differential expression) behaves correctly end to end.

```{r crispld2-check}
crispld2 <- res["ENSG00000103196", ]
crispld2
```

**Result:** log2FoldChange = `r round(crispld2$log2FoldChange, 3)`
(≈ `r round(2^crispld2$log2FoldChange, 1)`x higher expression in treated vs.
untreated), padj = `r format(crispld2$padj, scientific = TRUE, digits = 3)`.

This confirms the expected direction and magnitude of upregulation, with
padj several orders of magnitude below any conventional significance
threshold (0.05/0.1) — consistent with the original paper's qPCR/Western
blot validation.
