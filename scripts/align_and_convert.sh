#!/bin/bash
# Paths hardcoded (not using $DATA_DIR) since this script may run outside
# the direnv-managed project directory context.
set -euo pipefail

cd /mnt/data/airway-dryrun/raw

for srr in SRR1039508 SRR1039509 SRR1039512 SRR1039513 SRR1039516 SRR1039517 SRR1039520 SRR1039521; do
  echo "Aligning $srr..."
  hisat2 -p 4 \
    -x /mnt/data/airway-dryrun/reference/grch38_tran/genome_tran \
    -1 ${srr}_1.fastq.gz \
    -2 ${srr}_2.fastq.gz \
    -S /mnt/data/airway-dryrun/aligned/${srr}.sam \
    --summary-file /mnt/data/airway-dryrun/aligned/${srr}_align_summary.txt
  echo "$srr alignment done."
done

echo "All alignments complete. Starting SAM to BAM conversion..."

for srr in SRR1039508 SRR1039509 SRR1039512 SRR1039513 SRR1039516 SRR1039517 SRR1039520 SRR1039521; do
  echo "Converting $srr..."
  samtools sort -@ 4 -o /mnt/data/airway-dryrun/aligned/${srr}.sorted.bam /mnt/data/airway-dryrun/aligned/${srr}.sam
  samtools index /mnt/data/airway-dryrun/aligned/${srr}.sorted.bam
  rm /mnt/data/airway-dryrun/aligned/${srr}.sam
  echo "$srr converted, SAM removed."
done

echo "Pipeline stage complete: all 8 samples aligned and converted to sorted, indexed BAM."
