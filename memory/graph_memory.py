import json
import re
import networkx as nx
import spacy
from pathlib import Path

class GraphMemory:
    def __init__(self, graph_path="data/memory_graph.jsonl"):
        self.graph_path = Path(graph_path)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = nx.MultiDiGraph()
        self.nlp = spacy.load("en_core_web_trf")  # transformer-based NER
        self._load()

    def _load(self):
        if self.graph_path.exists():
            with open(self.graph_path, "r", encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    self.graph.add_edge(
                        record["source"], record["target"],
                        relation=record["relation"], meta=record["meta"]
                    )

    def _save_edge(self, source, target, relation, meta):
        with open(self.graph_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "source": source,
                "target": target,
                "relation": relation,
                "meta": meta
            }) + "\n")

    #def add_chunk(self, url, chunk_id, text):
    #    doc = self.nlp(text)
#
    #    tokens = set()
#
    #    for ent in doc.ents:
    #        tokens.add(self._normalize(ent.text))
#
    #    for chunk in doc.noun_chunks:
    #        tokens.add(self._normalize(chunk.text))
#
    #    tokens = list(tokens)
    #    if len(tokens) < 2:
    #        return
#
    #    for i in range(len(tokens)):
    #        for j in range(i + 1, len(tokens)):
    #            t1, t2 = tokens[i], tokens[j]
    #            meta = {"url": url, "chunk_id": chunk_id}
#
    #            self.graph.add_edge(t1, t2, relation="co-occurs", meta=meta)
    #            self.graph.add_edge(t2, t1, relation="co-occurs", meta=meta)
#
    #            self._save_edge(t1, t2, "co-occurs", meta)
    #            self._save_edge(t2, t1, "co-occurs", meta)

    def add_chunk(self, url, chunk_id, text, max_tokens=20):
        doc = self.nlp(text)
    
        # collect normalized tokens
        tokens = list({
            self._normalize(ent.text) for ent in doc.ents
        } | {
            self._normalize(chunk.text) for chunk in doc.noun_chunks
        })
    
        # filter trivial tokens
        tokens = [t for t in tokens if len(t.split()) > 1][:max_tokens]
    
        if len(tokens) < 2:
            return
    
        # build edges in memory
        edges_to_save = []
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                t1, t2 = tokens[i], tokens[j]
                meta = {"url": url, "chunk_id": chunk_id}
                self.graph.add_edge(t1, t2, relation="co-occurs", meta=meta)
                edges_to_save.append((t1, t2, "co-occurs", meta))
    
        # batch save to disk
        with open(self.graph_path, "a", encoding="utf-8") as f:
            for src, tgt, rel, meta in edges_to_save:
                f.write(json.dumps({
                    "source": src, "target": tgt, "relation": rel, "meta": meta
                }) + "\n")


    def query_entities(self, entity):
        """
        Return all edges where the normalized entity is either source or target.
        """
        entity = self._normalize(entity)  
    
        edges_out = list(self.graph.edges(entity, data=True))
        edges_in = list(self.graph.in_edges(entity, data=True))
    
        results = []
        for src, tgt, data in edges_out + edges_in:
            results.append({
                "source": src,
                "target": tgt,
                "relation": data.get("relation", "unknown"),
                "meta": data.get("meta", {})
            })
        return results
    
    def _normalize(self, ent):
        ent = ent.lower().strip()
        ent = re.sub(r"[^a-z0-9\s]+", "", ent)
        return ent

    def query_edges_by_chunk(self, chunk_id):
        """
        Optional: return all edges that came from a specific chunk
        """
        edges = []
        for src, tgt, data in self.graph.edges(data=True):
            if data["meta"].get("chunk_id") == chunk_id:
                edges.append((src, tgt, data))
        return edges
