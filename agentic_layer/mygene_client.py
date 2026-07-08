"""
MyGene.info client — batch-resolves Ensembl gene IDs to gene symbol,
name, and functional summary in a single HTTP request.
"""

import requests

MYGENE_BATCH_URL = "https://mygene.info/v3/query"


def fetch_gene_annotations(ensembl_ids: list[str]) -> dict:
    """
    Given a list of Ensembl gene IDs, return a dict mapping
    ensembl_id -> {symbol, name, summary}.

    Uses MyGene.info's batch query endpoint (POST with comma-separated ids)
    instead of one request per gene.
    """
    if not ensembl_ids:
        return {}

    response = requests.post(
        MYGENE_BATCH_URL,
        data={
            "q": ",".join(ensembl_ids),
            "scopes": "ensembl.gene",
            "fields": "symbol,name,summary",
            "species": "human",
        },
        timeout=30,
    )
    response.raise_for_status()
    results = response.json()

    annotations = {}
    for entry in results:
        query_id = entry.get("query")
        if not query_id:
            continue

        if entry.get("notfound"):
            annotations[query_id] = {
                "symbol": None,
                "name": None,
                "summary": "No annotation found in MyGene.info.",
            }
            continue

        annotations[query_id] = {
            "symbol": entry.get("symbol"),
            "name": entry.get("name"),
            "summary": entry.get("summary", "No functional summary available."),
        }

    # Ensure every requested ID has an entry, even if MyGene.info dropped it silently
    for gene_id in ensembl_ids:
        if gene_id not in annotations:
            annotations[gene_id] = {
                "symbol": None,
                "name": None,
                "summary": "No annotation found in MyGene.info.",
            }

    return annotations


if __name__ == "__main__":
    # Quick standalone test — run this file directly to sanity-check the client
    test_ids = ["ENSG00000103196", "ENSG00000162493"]  # CRISPLD2, PELI2
    result = fetch_gene_annotations(test_ids)
    for gene_id, info in result.items():
        print(f"{gene_id}: {info['symbol']} — {info['name']}")
        print(f"  {info['summary'][:150]}...\n")