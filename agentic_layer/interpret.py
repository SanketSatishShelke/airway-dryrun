"""
Orchestrator for the agentic interpretation layer.

Reads top DE genes -> fetches MyGene.info annotations -> synthesizes
an LLM-based interpretation -> writes output/interpretation.md.
"""

import os
import csv
from mygene_client import fetch_gene_annotations
from llm_client import generate_interpretation

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


def build_prompt(genes, annotations):
    lines = [
        "You are assisting with interpretation of RNA-seq differential expression "
        "results from an airway smooth muscle dexamethasone-response experiment "
        "(Himes et al. 2014 dataset). Below are the top differentially expressed "
        "genes ranked by adjusted p-value, along with their known function from "
        "MyGene.info.\n",
        "For EACH gene, write a short (2-3 sentence) grounded summary connecting "
        "its statistical result (direction and magnitude of change) to its known "
        "biological function, based ONLY on the annotation provided. Do not invent "
        "function not present in the annotation.\n",
        "After all individual gene summaries, add ONE closing paragraph, clearly "
        "labeled 'Possible patterns (hypothesis, not confirmed):', that cautiously "
        "notes any shared themes across genes (e.g. common pathway, tissue process) "
        "-- explicitly framed as a hypothesis worth further investigation via proper "
        "enrichment analysis (e.g. clusterProfiler/GO), not a confirmed finding.\n",
        "---\n",
    ]

    for gene in genes:
        ann = annotations.get(gene["ensembl_id"], {})
        symbol = ann.get("symbol") or "Unknown symbol"
        name = ann.get("name") or "Unknown name"
        summary = ann.get("summary") or "No functional summary available."
        direction = "upregulated" if gene["log2FoldChange"] > 0 else "downregulated"

        lines.append(
            f"Gene: {symbol} ({gene['ensembl_id']}) — {name}\n"
            f"Result: log2FoldChange = {gene['log2FoldChange']:.2f} ({direction}), "
            f"padj = {gene['padj']:.2e}, baseMean = {gene['baseMean']:.1f}\n"
            f"Known function: {summary}\n"
        )

    return "\n".join(lines)


def main():
    genes = load_top_genes(TOP_GENES_CSV)
    print(f"Loaded {len(genes)} genes from {TOP_GENES_CSV}")

    ensembl_ids = [g["ensembl_id"] for g in genes]
    annotations = fetch_gene_annotations(ensembl_ids)
    print(f"Fetched annotations for {len(annotations)} genes from MyGene.info")

    prompt = build_prompt(genes, annotations)
    print("Sending prompt to LLM...")
    interpretation = generate_interpretation(prompt, max_tokens=2048)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("# LLM-Based Interpretation of Top Differentially Expressed Genes\n\n")
        f.write(
            "*Generated via MyGene.info annotation retrieval + "
            "meta/llama-3.3-70b-instruct (NVIDIA NIM). "
            "This is a v1 single-source retrieval + synthesis layer; "
            "multi-source cross-referencing (NCBI, UniProt) and autonomous "
            "tool orchestration are planned extensions, not yet implemented.*\n\n"
        )
        f.write(interpretation)

    print(f"Interpretation written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()