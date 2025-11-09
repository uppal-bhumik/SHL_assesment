"""
SHL Assessment Recommendation Engine
RAG-based system for recommending tests based on recruiter queries
"""

import os
import re
import re
import json
import pandas as pd
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class RecommendationEngine:
    """
    The AI "brain" for the SHL Recommendation System.
    Uses a RAG (Retrieval-Augmented Generation) chain to provide recommendations.
    """
    
    def __init__(self):
        """
        Initializes the engine on server startup.
        Loads data, builds the vector store, and sets up the RAG chain.
        """
        print("\n" + "="*70)
        print("Initializing SHL Recommendation Engine")
        print("="*70)
        
        self.csv_path = "data/Book1.xlsx - Sheet1.csv"
        
        # Load data and store both retriever and dataframe
        self.retriever, self.dataframe = self._load_and_index_data()
        
        # 1. Initialize the LLM (Cost-effective model)
        print("  [1/3] Initializing LLM (gpt-3.5-turbo)...")
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        print("        ✓ LLM initialized")

        # 2. Define our RAG Prompt (The "context")
        print("  [2/3] Building RAG prompt...")
        rag_prompt_template = """
        You are an expert SHL assessment recommender. A user is asking for help hiring.
        Use the following pieces of retrieved context to answer the user's query.
        Your goal is to recommend 5-10 assessments that match the user's needs.
        You MUST adhere to the "Balance Requirement": If the query mentions both technical skills 
        (e.g., 'Java', 'SQL') and behavioral skills (e.g., 'collaboration', 'leadership'), 
        you MUST recommend a mix of both "Knowledge & Skills" tests and "Personality & Behavior" tests.
        
        Return your answer as a clean list of names. **Only return the names and nothing else.** Do not add any extra text, descriptions, or test types to your answer.
        Do not make up any names.
        
        Query: {query}
        
        Context: {context}
        
        Answer:
        """
        self.prompt = PromptTemplate.from_template(rag_prompt_template)
        print("        ✓ Prompt built")

        # 3. Define the full RAG chain
        print("  [3/3] Building RAG chain...")
        self.rag_chain = (
            {"context": self.retriever, "query": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        print("        ✓ RAG chain built")
        print("\n✓ Engine initialized successfully!\n")
    
    def _load_and_index_data(self):
        """
        Private method to load, process, and index the data from our Excel file.
        Returns both the retriever and the dataframe for lookups.
        """
        print(f"Data source: {self.csv_path}")
        print("Loading and indexing data...")

        print("  [1/4] Loading Excel data...")
        try:
            # Use read_excel, not read_csv
            df = pd.read_excel(self.csv_path, engine='openpyxl')
            # Filter out empty/bad rows
            df = df[df['name'].notna()].copy()
            print(f"        ✓ Loaded {len(df)} products")
        except Exception as e:
            print(f"  ✗ FAILED to read Excel file: {e}")
            raise e

        print("  [2/4] Creating documents from data...")
        documents = []
        for idx, row in df.iterrows():
            # Combine only the relevant text fields for the AI to "read"
            page_content = f"Name: {row['name']}\n"
            page_content += f"Description: {row['description']}\n"
            page_content += f"Test Type: {row['test_type']}"
            
            # Store the original row data as metadata
            metadata = row.to_dict()
            metadata['source'] = self.csv_path
            metadata['row'] = idx
            
            documents.append(Document(page_content=page_content, metadata=metadata))
        
        print(f"        ✓ Created {len(documents)} documents")

        print("  [3/4] Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)
        print(f"        ✓ Created {len(splits)} chunks")

        print("  [4/4] Building vector store...")
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        print("        ✓ Vector store created")
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
        return retriever, df
    
    def _parse_llm_answer(self, llm_answer: str) -> List[str]:
        """
        Parse the LLM's text response into a clean list of assessment names.
        """
        print("\n  Parsing LLM answer...")
        
        lines = llm_answer.strip().split('\n')
        
        names = []
        for line in lines:
            if not line.strip():
                continue
            
            # Remove prefixes like "1.", "-", "*"
            cleaned = re.sub(r'^\s*[\d]+[\.)]\s*', '', line)  
            cleaned = re.sub(r'^\s*[-*•]\s*', '', cleaned)
            
            # --- THIS IS THE FIX ---
            # Remove any text in parentheses, like "(New)"
            cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned).strip()
            
            # --- ADD THIS NEW LINE ---
            # Remove any " - ..." junk the AI adds
            cleaned = re.sub(r'\s*-\s*.*$', '', cleaned).strip()
            # --- END OF NEW LINE ---

            if cleaned:
                names.append(cleaned)
        
        print(f"        ✓ Extracted {len(names)} assessment names")
        return names
    
    def _find_data_by_names(self, names: List[str]) -> List[Dict[str, Any]]:
        """
        Look up full product data for each assessment name.
        Returns a list of properly formatted dictionaries matching our API schema.
        """
        print("\n  Looking up full data for assessments...")
        
        results = []
        
        for name in names:
            # Search for matching rows (case-insensitive partial match)
            matches = self.dataframe[
                self.dataframe['name'].str.contains(name, case=False, na=False)
            ]
            
            if matches.empty:
                print(f"        ⚠ No match found for: {name}")
                continue
            
            # Take the first match
            row = matches.iloc[0]
            
            # --- THIS IS THE CRITICAL FIX ---
            # Convert to properly formatted dictionary matching our Pydantic model
            product_dict = {
                "name": str(row['name']) if pd.notna(row['name']) else "",
                "url": str(row['url']) if pd.notna(row['url']) else "",
                "description": str(row['description']) if pd.notna(row['description']) else "",
                "adaptive_support": str(row['adaptive_support']) if pd.notna(row['adaptive_support']) else "No",
                "duration": int(row['duration']) if pd.notna(row['duration']) else 0,
                "remote_support": str(row['remote_support']) if pd.notna(row['remote_support']) else "No",
                "test_type": self._parse_test_type(row['test_type'])
            }
            # --- END OF FIX ---
            
            results.append(product_dict)
            print(f"        ✓ Found: {product_dict['name']}")
        
        print(f"\n  ✓ Successfully retrieved {len(results)} full product records")
        return results
    
    def _parse_test_type(self, test_type_value) -> List[str]:
        """
        Convert test_type from string representation to actual list.
        Handles formats like: "['Knowledge & Skills']" or "['Personality & Behavior'; 'Knowledge & Skills']"
        """
        if pd.isna(test_type_value):
            return []
        
        # If it's already a list, return it
        if isinstance(test_type_value, list):
            return test_type_value
        
        # If it's a string representation of a list, parse it
        if isinstance(test_type_value, str):
            try:
                # First, try to replace semicolons (our fix) and parse as JSON
                return json.loads(test_type_value.replace(";", ","))
            except json.JSONDecodeError:
                try:
                    # Fallback for simple strings or other formats
                    cleaned = test_type_value.strip("[]'\"")
                    if ';' in cleaned: # Our manual format
                        return [item.strip().strip("'\"") for item in cleaned.split(';')]
                    elif ',' in cleaned: # Standard list-as-string format
                        return [item.strip().strip("'\"") for item in cleaned.split(',')]
                    else:
                        return [cleaned] if cleaned else []
                except Exception:
                    return [] # Failsafe
        
        return []
    
    def get_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """
        Runs the full RAG chain to get smart recommendations.
        Returns a list of full product dictionaries with all details.
        """
        print("\n" + "="*70)
        print(f"Processing Query: {query}")
        print("="*70)
        
        # Step A: Call the RAG chain
        print("\nStep A: Invoking RAG chain (Retrieval + Generation)...")
        llm_answer = self.rag_chain.invoke(query)
        print(f"LLM Answer:\n{llm_answer}")
        
        # Step B: Parse the text answer into a list of names
        print("\nStep B: Parsing LLM answer...")
        assessment_names = self._parse_llm_answer(llm_answer)
        
        # Step C: Look up the full data for each name
        print("\nStep C: Looking up full product data...")
        full_products = self._find_data_by_names(assessment_names)
        
        # Step D: Return the list of full data dictionaries
        print("\n" + "="*70)
        print(f"✓ Successfully found {len(full_products)} complete product records")
        print("="*70)
        
        return full_products

# This main block is just for testing the logic.py file directly
def main():
    """
    Test the recommendation engine.
    """
    print("=" * 70)
    print("SHL Recommendation Engine - Test Run")
    print("=" * 70 + "\n")
    
    try:
        # Initialize engine
        engine = RecommendationEngine()
        
        # Test queries
        test_queries = [
            "I need a Java developer who is also a good collaborator",
            "Looking for someone with strong leadership and communication skills",
            "Python programmer with problem-solving abilities"
        ]
        
        for query in test_queries:
            results = engine.get_recommendations(query)
            print(f"\n{'='*70}")
            print(f"Query: {query}")
            print(f"Found {len(results)} recommendations:")
            for i, product in enumerate(results, 1):
                print(f"\n  {i}. {product['name']}")
                print(f"     Duration: {product['duration']} mins")
                print(f"     Type: {product['test_type']}")
                print(f"     URL: {product['url']}")
            print('='*70)
        
        print("\n" + "=" * 70)
        print("Test complete!")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from dotenv import load_dotenv
    # Load .env file for direct testing
    load_dotenv()
    main()