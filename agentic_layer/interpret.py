"""
Orchestrator for the agentic interpretation layer.

Reads top DE genes -> fetches MyGene.info annotations -> generates one
LLM summary per gene via concurrent requests (I/O-bound, independent calls,
bounded by MAX_WORKERS and NIM's rate limit) -> generates one closing
synthesis paragraph -> writes output/interpretation.md.
"""

import os
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from mygene_client import fetch_gene_annotations
from llm_client import generate_interpretation

MAX_WORKERS = 5
MAX_RETRIES = 2

PROJECT_DIR = os.environ.get("PROJECT_DIR")
if not PROJECT_DIR:
    raise ValueError("PROJECT_DIR not set. Ensure .env is loaded / direnv is active.")

TOP_GENES_CSV = os.path.join(PROJECT_DIR, "results", "top_genes.csv")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "agentic_layer", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "interpretation.md")


def load_top_genes(csv_path):
    genes = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            genes.append({
                "ensembl_id": row["ensembl_id"],
                "log2FoldChange": float(row["log2FoldChange"]),
                "padj": float(row["padj"]),
                "baseMean": float(row["baseMean"]),
            })
    return genes


def build_gene_prompt(gene, ann):
    symbol = ann.get("symbol") or "Unknown symbol"
    name = ann.get("name") or "Unknown name"
    summary = ann.get("summary") or "No functional summary available."
    direction = "upregulated" if gene["log2FoldChange"] > 0 else "downregulated"

    return (
        "You are assisting with interpretation of a single RNA-seq differential "
        "expression result from an airway smooth muscle dexamethasone-response "
        "experiment (Himes et al. 2014 dataset).\n\n"
        f"Gene: {symbol} ({gene['ensembl_id']}) — {name}\n"
        f"Result: log2FoldChange = {gene['log2FoldChange']:.2f} ({direction}), "
        f"padj = {gene['padj']:.2e}, baseMean = {gene['baseMean']:.1f}\n"
        f"Known function (MyGene.info): {summary}\n\n"
        "Write a short (2-3 sentence) grounded summary connecting this gene's "
        "statistical result (direction and magnitude of change) to its known "
        "biological function, based ONLY on the annotation provided above. "
        "Do not invent function not present in the annotation. Do not speculate "
        "beyond what the annotation supports."
    )


def build_synthesis_prompt(gene_summaries):
    joined = "\n\n".join(
        f"{s['symbol']}: {s['summary_text']}" for s in gene_summaries
    )
    return (
        "Below are individual gene-level summaries from an RNA-seq differential "
        "expression analysis (airway smooth muscle, dexamethasone response).\n\n"
        f"{joined}\n\n"
        "Write ONE short closing paragraph, clearly labeled "
        "'Possible patterns (hypothesis, not confirmed):', that cautiously notes "
        "any shared themes across these genes (e.g. common pathway, tissue "
        "process, biological theme) -- explicitly framed as a hypothesis worth "
        "further investigation via proper enrichment analysis (e.g. "
        "clusterProfiler/GO), not a confirmed finding. If no clear shared theme "
        "is apparent, say so honestly rather than forcing a connection."
    )


def summarize_gene(gene, annotations):
    ann = annotations.get(gene["ensembl_id"], {})
    symbol = ann.get("symbol") or gene["ensembl_id"]
    prompt = build_gene_prompt(gene, ann)

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            summary_text = generate_interpretation(prompt, max_tokens=250)
            return {
                "ensembl_id": gene["ensembl_id"],
                "symbol": symbol,
                "summary_text": summary_text.strip(),
            }
        except Exception as e:
            last_error = e
            print(f"  [{symbol}] attempt {attempt} failed: {e}")
            time.sleep(2 * attempt)  # simple backoff

    # All retries exhausted — return a placeholder rather than crashing the whole run
    return {
        "ensembl_id": gene["ensembl_id"],
        "symbol": symbol,
        "summary_text": f"[Generation failed after {MAX_RETRIES} attempts: {last_error}]",
    }


def main():
    genes = load_top_genes(TOP_GENES_CSV)
    print(f"Loaded {len(genes)} genes from {TOP_GENES_CSV}")

    ensembl_ids = [g["ensembl_id"] for g in genes]
    annotations = fetch_gene_annotations(ensembl_ids)
    print(f"Fetched annotations for {len(annotations)} genes from MyGene.info")

    gene_summaries_by_id = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(summarize_gene, gene, annotations): gene
            for gene in genes
        }
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            gene_summaries_by_id[result["ensembl_id"]] = result
            completed += 1
            print(f"  [{completed}/{len(genes)}] Done: {result['symbol']}")

    # Preserve original gene order (padj-ranked), not thread completion order
    gene_summaries = [gene_summaries_by_id[g["ensembl_id"]] for g in genes]

    print("Generating closing synthesis paragraph...")
    synthesis_prompt = build_synthesis_prompt(gene_summaries)
    synthesis = generate_interpretation(synthesis_prompt, max_tokens=400)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("# LLM-Based Interpretation of Top Differentially Expressed Genes\n\n")
        f.write(
            "*Generated via MyGene.info annotation retrieval + "
            "meta/llama-3.3-70b-instruct (NVIDIA NIM), using concurrent "
            "per-gene calls (ThreadPoolExecutor, max 5 workers, retry with "
            "backoff on failure). This is a v1 single-source retrieval + "
            "synthesis layer; multi-source cross-referencing (NCBI, UniProt) "
            "and autonomous tool orchestration are planned extensions, not "
            "yet implemented.*\n\n"
        )
        for s in gene_summaries:
            f.write(f"**{s['symbol']}** ({s['ensembl_id']}): {s['summary_text']}\n\n")
        f.write(synthesis)

    print(f"Interpretation written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()