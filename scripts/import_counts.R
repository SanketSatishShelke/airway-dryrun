# Load count matrix and sample metadata, align them for DESeq2

counts_raw <- read.table(
  file.path(Sys.getenv("PROJECT_DIR"), "results/counts/all_samples_counts.txt"),
  header = TRUE, sep = "\t", skip = 1, row.names = 1
)

# Drop featureCounts' extra annotation columns (Chr, Start, End, Strand, Length)
# — only the actual count columns (one per BAM) are needed from here on
count_cols <- counts_raw[, 6:ncol(counts_raw)]

# Strip the .sorted.bam suffix from column names to get bare SRR accessions,
# matching sample_metadata.csv's run_accession column exactly
colnames(count_cols) <- sub("\\.sorted\\.bam$", "", colnames(count_cols))

metadata <- read.csv(file.path(Sys.getenv("PROJECT_DIR"), "sample_metadata.csv"), stringsAsFactors = TRUE)
rownames(metadata) <- metadata$run_accession

# Explicit key-based reordering: match count matrix columns to metadata rows
# by run_accession, rather than assuming positional order is already correct
count_cols <- count_cols[, metadata$run_accession]

# Sanity check before proceeding — this should be TRUE
stopifnot(all(colnames(count_cols) == rownames(metadata)))

cat("Count matrix dimensions:", dim(count_cols), "\n")
cat("Sample order check passed.\n")