
## Tool versions
- sra-tools (prefetch/fasterq-dump): 3.4.1
- FastQC: 0.12.1

## Data acquisition note
Raw FASTQ obtained via direct download from ENA (European Nucleotide Archive),
which serves pre-converted FASTQ.gz directly (no SRA-format intermediate).
Equivalent underlying sequencing data to SRA accessions SRR1039508/09/12/13/16/17/20/21.
Switched from SRA-tools (prefetch/fasterq-dump) due to local disk I/O bottleneck
during SRA-to-FASTQ conversion.
