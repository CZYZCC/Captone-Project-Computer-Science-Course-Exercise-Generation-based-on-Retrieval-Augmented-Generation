import json
import os
import re
import statistics
import random
import time
from collections import defaultdict
from typing import List, Dict, Set
from openai import OpenAI

# ==========================================
# Logger Utility
# ==========================================
class Logger:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.log_file = os.path.join(output_dir, "experiment_log.txt")
        self.json_dir = os.path.join(output_dir, "generated_questions")
        os.makedirs(self.json_dir, exist_ok=True)
        
        # Clear previous log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"Experiment Started at {time.ctime()}\n{'='*50}\n")

    def log(self, message: str):
        """Print to console and append to file."""
        print(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + "\n")

    def save_artifact(self, filename: str, data: dict):
        """Save JSON artifact."""
        path = os.path.join(self.json_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# ==========================================
# Knowledge Graph
# ==========================================
class SimpleKnowledgeGraph:
    def __init__(self, logger: Logger):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.node_metadata = {}
        self.node_topics = defaultdict(set)
        self.topic_index = defaultdict(set)
        self.logger = logger
    
    def add_node(self, node_id: str, content: str, metadata: dict = None):
        self.nodes[node_id] = content
        if metadata:
            self.node_metadata[node_id] = metadata
        
        topics = self._extract_topics(content, metadata)
        self.node_topics[node_id] = topics
        for topic in topics:
            self.topic_index[topic].add(node_id)
    
    def add_edge(self, from_id: str, to_id: str, relation: str = "related"):
        existing = [e['to'] for e in self.edges[from_id]]
        if to_id not in existing and from_id != to_id:
            self.edges[from_id].append({'to': to_id, 'relation': relation})
            self.edges[to_id].append({'to': from_id, 'relation': relation})
    
    def get_node_content(self, node_id: str) -> str:
        return self.nodes.get(node_id, "")
    
    def get_neighbors(self, node_id: str) -> List[str]:
        return [edge['to'] for edge in self.edges.get(node_id, [])]
    
    def _extract_topics(self, content: str, metadata: dict) -> Set[str]:
        topics = set()
        text_to_scan = content.lower()
        if metadata:
            text_to_scan += " " + str(metadata.get('title', '')).lower()
        
        blocklist = {
            "algorithm", "data", "structure", "system", "computer", "science", 
            "programming", "method", "function", "input", "output", "problem",
            "value", "number", "set", "list", "array"
        }
        important_terms = {
            "recursion", "complexity", "quicksort", "mergesort", "heapsort", 
            "binary_search", "dfs", "bfs", "dijkstra", "dynamic_programming", 
            "memoization", "hashing", "collision", "pointer", "linked_list", 
            "stack", "queue", "heap", "tree", "graph", "vertex", "edge", 
            "np_complete", "backtracking", "greedy", "amortized"
        }
        
        for term in important_terms:
            if term in text_to_scan:
                topics.add(term)

        words = re.findall(r'\b[a-z]{5,}\b', text_to_scan)
        for w in words:
            if w not in blocklist and w not in important_terms:
                pass 
        return topics

    def build_semantic_edges(self):
        self.logger.log("   >>> Building Semantic Edges...")
        edge_count = 0
        sorted_topics = sorted(self.topic_index.items(), key=lambda x: len(x[1]))
        
        for topic, node_ids in sorted_topics:
            nodes_list = list(node_ids)
            if len(nodes_list) > 30: continue
            limit = 8
            nodes_list = nodes_list[:limit]
            
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    self.add_edge(nodes_list[i], nodes_list[j], relation=f"shares_topic_{topic}")
                    edge_count += 1
        self.logger.log(f"   >>> Added {edge_count} semantic edges.")

    def build_from_multiple_textbooks(self, textbook_dir: str, max_textbooks: int = 20):
        self.logger.log(f"\n{'='*60}\nBuilding Knowledge Graph\n{'='*60}")
        total_nodes = 0
        for i in range(1, max_textbooks + 1):
            textbook_path = os.path.join(textbook_dir, f"textbook{i}", f"textbook{i}_structured.json")
            if not os.path.exists(textbook_path): continue
            
            try:
                with open(textbook_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    nodes_added = 0
                    for j, item in enumerate(data):
                        node_id = f"tb{i}_node{j}"
                        content = str(item.get('content', str(item)))
                        metadata = item if isinstance(item, dict) else {}
                        metadata.update({'textbook_id': i, 'node_index': j})
                        
                        self.add_node(node_id, content, metadata)
                        if j > 0: 
                            self.add_edge(f"tb{i}_node{j-1}", node_id, "follows")
                        nodes_added += 1
                    total_nodes += nodes_added
                    self.logger.log(f"Textbook {i}: Added {nodes_added} nodes")
            except Exception as e:
                self.logger.log(f"Error loading textbook {i}: {e}")
        
        self.build_semantic_edges()
        return total_nodes

# ==========================================
# Retrievers
# ==========================================
class BaselineRetriever:
    def __init__(self, kg: SimpleKnowledgeGraph):
        self.kg = kg

    def retrieve(self, keyword: str, top_k: int = 5) -> List[Dict]:
        # Standard Keyword Matching Baseline (Not random)
        scored_nodes = []
        for node_id, content in self.kg.nodes.items():
            score = 0
            if keyword.lower() in content.lower(): score += 10
            if score > 0: scored_nodes.append((score, node_id))
        
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        top_nodes = [n[1] for n in scored_nodes[:top_k]]
        
        self.kg.logger.log(f"   [Baseline] Retrieving '{keyword}': Found {len(top_nodes)} nodes.")
        
        return [{
            'node_id': nid, 
            'content': self.kg.get_node_content(nid),
            'metadata': self.kg.node_metadata.get(nid, {})
        } for nid in top_nodes]

class GraphRetriever:
    def __init__(self, kg: SimpleKnowledgeGraph):
        self.kg = kg
    
    def retrieve_subgraph(self, topic: str, seed_limit: int = 3, hops: int = 2) -> List[Dict]:
        seeds = []
        for nid, topics in self.kg.node_topics.items():
            if any(topic.lower() in t for t in topics):
                seeds.append(nid)
        
        if not seeds:
            for nid, content in self.kg.nodes.items():
                if topic.lower() in content.lower():
                    seeds.append(nid)
        
        seeds = seeds[:seed_limit]
        self.kg.logger.log(f"   [GraphRAG] Found {len(seeds)} seed nodes for '{topic}'.")
        
        visited = set(seeds)
        current_level = set(seeds)
        
        for _ in range(hops):
            next_level = set()
            for node in current_level:
                neighbors = self.kg.get_neighbors(node)
                if len(neighbors) > 5:
                    neighbors = random.sample(neighbors, 5)
                next_level.update(neighbors)
            visited.update(next_level)
            current_level = next_level
        
        results = []
        for nid in list(visited)[:15]: 
            results.append({
                'node_id': nid,
                'content': self.kg.get_node_content(nid),
                'metadata': self.kg.node_metadata.get(nid, {})
            })
        return results

# ==========================================
# Generator & Evaluator
# ==========================================
class GraphRAGGenerator:
    def __init__(self, api_key: str):
        self.llm = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    def generate_question(self, topic: str, context: List, method: str) -> str:
        context_str = "\n".join([f"[{i+1}] {c['content'][:300]}..." for i, c in enumerate(context)])
        
        if method == "graphrag":
            system_prompt = f"""You are an expert Computer Science Examiner.
Context contains graph-connected snippets about "{topic}".
Task: Create a Multi-Hop Question that requires synthesizing information from AT LEAST TWO different snippets.
- The question MUST connect a concept from one snippet to a concept in another.
- Do NOT ask simple definition questions.
"""
        else:
            system_prompt = f"""You are an expert Computer Science Examiner.
Task: Create a Multiple Choice Question about "{topic}" based on the context.
"""

        prompt = f"""{system_prompt}
Topic: {topic}
Context:
{context_str}

Return JSON:
{{
    "question": "...",
    "correct_answer": "...",
    "distractors": ["...", "...", "..."],
    "rationale": "Explain step-by-step how snippets were combined."
}}
"""
        try:
            response = self.llm.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({"question": "Error", "rationale": str(e)})

class AutomatedEvaluator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def evaluate(self, question_json: str, context: List, topic: str) -> Dict:
        try:
            q_data = json.loads(question_json)
        except:
            return {'overall': 0}

        context_text = "\n".join([c['content'][:200] for c in context])
        
        prompt = f"""Evaluate this CS Question.

Topic: {topic}
Question: {q_data.get('question')}
Rationale: {q_data.get('rationale')}
Context: {context_text}

Criteria:
1. Relevance (0-1): Is it about {topic}?
2. Faithfulness (0-1): Is the answer fully supported by Context?
3. Integration (0-1): Does answering REQUIRE combining info from multiple snippets? (1.0 = multi-hop, 0.0 = single-hop).
4. Complexity (0-1): Does the question require deep reasoning, comparison, or synthesis? (1.0 = deep analysis, 0.0 = simple recall/lookup).

Output JSON: {{ "relevance": float, "faithfulness": float, "integration": float, "complexity": float }}
"""
        try:
            response = self.llm.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            scores = json.loads(response.choices[0].message.content)
            
            # Weighted Score: High emphasis on Integration and Complexity for GraphRAG
            scores['overall'] = (
                scores.get('relevance', 0) * 0.1 + 
                scores.get('faithfulness', 0) * 0.2 + 
                scores.get('integration', 0) * 0.4 + 
                scores.get('complexity', 0) * 0.3
            )
            return scores
        except:
            return {'overall': 0}

# ==========================================
# Main Pipeline
# ==========================================
class Pipeline:
    def __init__(self, api_key: str, output_dir: str):
        self.logger = Logger(output_dir)
        self.kg = SimpleKnowledgeGraph(self.logger)
        self.generator = GraphRAGGenerator(api_key)
        self.evaluator = AutomatedEvaluator(self.generator.llm)
        self.base_retriever = None
        self.graph_retriever = None

    def run(self, textbook_dir: str, topics: List[str]):
        self.kg.build_from_multiple_textbooks(textbook_dir)
        self.base_retriever = BaselineRetriever(self.kg)
        self.graph_retriever = GraphRetriever(self.kg)
        
        results = []
        
        self.logger.log(f"\n{'='*60}\nStarting Experiment\n{'='*60}")
        
        for i, topic in enumerate(topics, 1):
            self.logger.log(f"\n>>> Topic {i}/{len(topics)}: {topic}")
            
            # 1. Baseline
            base_ctx = self.base_retriever.retrieve(topic)
            base_json = self.generator.generate_question(topic, base_ctx, "baseline")
            base_score = self.evaluator.evaluate(base_json, base_ctx, topic)
            
            self._log_result("BASELINE", topic, base_json, base_score)
            self.logger.save_artifact(f"{topic.replace(' ','_')}_baseline.json", {
                "context": base_ctx, "output": json.loads(base_json), "score": base_score
            })

            # 2. GraphRAG
            graph_ctx = self.graph_retriever.retrieve_subgraph(topic)
            graph_json = self.generator.generate_question(topic, graph_ctx, "graphrag")
            graph_score = self.evaluator.evaluate(graph_json, graph_ctx, topic)
            
            self._log_result("GRAPHRAG", topic, graph_json, graph_score)
            self.logger.save_artifact(f"{topic.replace(' ','_')}_graphrag.json", {
                "context": graph_ctx, "output": json.loads(graph_json), "score": graph_score
            })
            
            results.append({
                "topic": topic,
                "baseline": base_score['overall'],
                "graphrag": graph_score['overall']
            })

        self._print_summary(results)

    def _log_result(self, method, topic, json_str, scores):
        try:
            data = json.loads(json_str)
            self.logger.log(f"   [{method}] Score: {scores['overall']:.2f} "
                            f"(Rel: {scores.get('relevance',0):.1f}, "
                            f"Faith: {scores.get('faithfulness',0):.1f}, "
                            f"Integ: {scores.get('integration',0):.1f}, "
                            f"Comp: {scores.get('complexity',0):.1f})")
            self.logger.log(f"   Q: {data.get('question')}")
            self.logger.log(f"   Rationale: {data.get('rationale')[:100]}...")
        except:
            self.logger.log(f"   [{method}] Error parsing JSON")

    def _print_summary(self, results):
        base_avg = statistics.mean([r['baseline'] for r in results])
        graph_avg = statistics.mean([r['graphrag'] for r in results])
        self.logger.log(f"\n{'='*60}\nFinal Summary\n{'='*60}")
        self.logger.log(f"Baseline Avg: {base_avg:.3f}")
        self.logger.log(f"GraphRAG Avg: {graph_avg:.3f}")
        self.logger.log(f"Improvement:  {graph_avg - base_avg:.3f}")

def main():
    api_key = os.getenv("DEEPSEEK_API_KEY") or "sk-579409f87c4f44d0b3cd5b2d7e527618"
    
    pipeline = Pipeline(api_key, "./experiment_logs_v4")
    
    topics = [
        "recursion", "sorting algorithm", "graph traversal", 
        "dynamic programming", "hash table"
    ]
    
    textbook_path = "./GraphRAG-Bench/textbooks"
    if os.path.exists(textbook_path):
        pipeline.run(textbook_path, topics)
    else:
        print(f"Error: Path {textbook_path} not found.")

if __name__ == "__main__":
    main()