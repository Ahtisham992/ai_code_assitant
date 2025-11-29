"""
Codebase Retrieval-Augmented Generation (RAG) System
Allows AI to retrieve similar code from user's codebase for context-aware suggestions
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class CodebaseRetrieval:
    """
    Retrieval system for finding similar code snippets from user's codebase
    Uses sentence-transformers for embeddings and FAISS for similarity search
    """
    
    def __init__(self, codebase_dir: str = "./user_codebase", model_name: str = "microsoft/codebert-base"):
        """
        Initialize the retrieval system
        
        Args:
            codebase_dir: Directory containing user's code files
            model_name: Embedding model to use (CodeBERT recommended for code)
        """
        self.codebase_dir = Path(codebase_dir)
        self.index_file = self.codebase_dir / "faiss_index.bin"
        self.metadata_file = self.codebase_dir / "metadata.json"
        
        # Create codebase directory if it doesn't exist
        self.codebase_dir.mkdir(exist_ok=True)
        
        # Load embedding model
        print(f"Loading embedding model: {model_name}...")
        try:
            self.embedding_model = SentenceTransformer(model_name)
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"⚠️ Failed to load {model_name}, falling back to simpler model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Fallback model loaded")
        
        # Initialize FAISS index
        self.dimension = 768  # CodeBERT dimension (or 384 for MiniLM)
        if model_name == 'all-MiniLM-L6-v2':
            self.dimension = 384
            
        self.index = None
        self.metadata = []
        
        # Load existing index if available
        if self.index_file.exists() and self.metadata_file.exists():
            self.load_index()
        else:
            print("No existing index found. Will create new index when codebase is indexed.")
    
    def index_codebase(self, force_reindex: bool = False):
        """
        Index all Python files in the codebase directory
        
        Args:
            force_reindex: If True, reindex even if index exists
        """
        if not force_reindex and self.index_file.exists():
            print("Index already exists. Use force_reindex=True to rebuild.")
            return
        
        print(f"Indexing codebase from {self.codebase_dir}...")
        
        # Find all Python files
        python_files = list(self.codebase_dir.rglob("*.py"))
        
        if not python_files:
            print("⚠️ No Python files found in codebase directory")
            return
        
        print(f"Found {len(python_files)} Python files")
        
        # Extract code snippets and metadata
        all_snippets = []
        all_metadata = []
        
        for file_path in python_files:
            snippets, metadata = self._extract_functions_from_file(file_path)
            all_snippets.extend(snippets)
            all_metadata.extend(metadata)
        
        if not all_snippets:
            print("⚠️ No code snippets extracted from files")
            return
        
        print(f"Extracted {len(all_snippets)} code snippets")
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(all_snippets, show_progress_bar=True)
        
        # Create FAISS index
        print("Building FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        self.metadata = all_metadata
        
        # Save index and metadata
        self.save_index()
        
        print(f"✅ Indexed {len(all_snippets)} code snippets from {len(python_files)} files")
    
    def _extract_functions_from_file(self, file_path: Path) -> Tuple[List[str], List[Dict]]:
        """
        Extract function definitions from a Python file
        
        Returns:
            Tuple of (code_snippets, metadata)
        """
        snippets = []
        metadata = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple function extraction (could be improved with AST parsing)
            lines = content.split('\n')
            current_function = []
            function_name = None
            in_function = False
            indent_level = 0
            
            for i, line in enumerate(lines):
                # Detect function start
                if line.strip().startswith('def ') and ':' in line:
                    if current_function and function_name:
                        # Save previous function
                        snippet = '\n'.join(current_function)
                        snippets.append(snippet)
                        metadata.append({
                            'file': str(file_path.relative_to(self.codebase_dir)),
                            'function': function_name,
                            'line': i - len(current_function) + 1,
                            'type': 'function'
                        })
                    
                    # Start new function
                    function_name = line.strip().split('def ')[1].split('(')[0]
                    current_function = [line]
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                
                elif in_function:
                    if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.strip().startswith('#'):
                        # Function ended
                        snippet = '\n'.join(current_function)
                        snippets.append(snippet)
                        metadata.append({
                            'file': str(file_path.relative_to(self.codebase_dir)),
                            'function': function_name,
                            'line': i - len(current_function) + 1,
                            'type': 'function'
                        })
                        current_function = []
                        function_name = None
                        in_function = False
                    else:
                        current_function.append(line)
            
            # Save last function if exists
            if current_function and function_name:
                snippet = '\n'.join(current_function)
                snippets.append(snippet)
                metadata.append({
                    'file': str(file_path.relative_to(self.codebase_dir)),
                    'function': function_name,
                    'line': i - len(current_function) + 2,
                    'type': 'function'
                })
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return snippets, metadata
    
    def retrieve_similar_code(self, query_code: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve similar code snippets from the indexed codebase
        
        Args:
            query_code: The code to find similar examples for
            top_k: Number of similar examples to return
            
        Returns:
            List of similar code snippets with metadata
        """
        if self.index is None or len(self.metadata) == 0:
            print("⚠️ No codebase indexed. Please run index_codebase() first.")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_code])
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                results.append({
                    'rank': i + 1,
                    'similarity_score': float(1 / (1 + dist)),  # Convert distance to similarity
                    'metadata': self.metadata[idx],
                    'code': self._load_code_snippet(self.metadata[idx])
                })
        
        return results
    
    def _load_code_snippet(self, metadata: Dict) -> str:
        """Load the actual code snippet from file"""
        try:
            file_path = self.codebase_dir / metadata['file']
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start_line = metadata['line'] - 1
                
                # Find function end
                indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                end_line = start_line + 1
                
                while end_line < len(lines):
                    line = lines[end_line]
                    if line.strip() and not line.startswith(' ' * (indent + 1)):
                        break
                    end_line += 1
                
                return ''.join(lines[start_line:end_line])
        except Exception as e:
            print(f"Error loading snippet: {e}")
            return ""
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            print(f"✅ Index saved to {self.index_file}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        try:
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            print(f"✅ Loaded index with {len(self.metadata)} code snippets")
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.metadata = []


# Example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("CODEBASE RETRIEVAL DEMO")
    print("="*60 + "\n")
    
    # Initialize retrieval system
    retriever = CodebaseRetrieval()
    
    # Index codebase (run this once, or when codebase changes)
    retriever.index_codebase(force_reindex=True)
    
    # Example query
    query_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total
"""
    
    print("\n" + "="*60)
    print("Searching for similar code...")
    print("="*60 + "\n")
    
    results = retriever.retrieve_similar_code(query_code, top_k=3)
    
    if results:
        print(f"Found {len(results)} similar code snippets:\n")
        for result in results:
            print(f"Rank {result['rank']} (Similarity: {result['similarity_score']:.3f})")
            print(f"File: {result['metadata']['file']}")
            print(f"Function: {result['metadata']['function']}")
            print(f"Line: {result['metadata']['line']}")
            print(f"Code:\n{result['code']}")
            print("-" * 60 + "\n")
    else:
        print("No results found or codebase not indexed.")