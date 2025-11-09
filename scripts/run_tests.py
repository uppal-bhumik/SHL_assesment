"""
SHL Assessment Recommendation System - Test Runner
Automated script to test the API with queries from test_set.csv
and generate the final submission file
"""

import pandas as pd
import requests
import os
from typing import List, Dict, Any

# ============================================================================
# Configuration
# ============================================================================

API_URL = "http://127.0.0.1:8000/recommend"
TEST_FILE = "data/test_set.csv"
OUTPUT_FILE = "deliverables/final_submission.csv"

# ============================================================================
# Helper Functions
# ============================================================================

def test_api_health() -> bool:
    """
    Test if the API is running and accessible.
    
    Returns:
        bool: True if API is healthy, False otherwise
    """
    try:
        health_url = API_URL.replace("/recommend", "/health")
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except:
        return False


def process_query(query: str) -> List[Dict[str, Any]]:
    """
    Process a single query through the API.
    
    Args:
        query: The recruiter query to process
    
    Returns:
        List of recommendation dictionaries
    """
    try:
        payload = {"query": query}
        response = requests.post(API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("recommended_assessments", [])
        else:
            print(f"  ⚠️  API returned status code: {response.status_code}")
            return []
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection Error: Could not reach API")
        return []
    
    except requests.exceptions.Timeout:
        print(f"  ⏱️  Timeout: API took too long to respond")
        return []
    
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return []


# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """
    Main test runner function.
    Reads test queries, calls API, and generates submission file.
    """
    
    print("\n" + "=" * 70)
    print("SHL Assessment Recommendation System - Test Runner")
    print("=" * 70 + "\n")
    
    # Step 1: Check if API is running
    print("Step 1: Checking API health...")
    if not test_api_health():
        print("❌ ERROR: API is not running or not accessible!")
        print("\nPlease ensure:")
        print("  1. The backend is running: python main.py")
        print("  2. The API is accessible at:", API_URL)
        print("\n" + "=" * 70 + "\n")
        return
    print("✓ API is healthy and ready\n")
    
    # Step 2: Load test queries
    print("Step 2: Loading test queries...")
    try:
        # Try multiple encodings and CSV parsing strategies
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        df = None
        
        for encoding in encodings:
            try:
                # Try with different CSV parsing options to handle malformed files
                df = pd.read_csv(
                    TEST_FILE, 
                    encoding=encoding,
                    on_bad_lines='skip',  # Skip malformed lines
                    engine='python',       # More flexible parser
                    quoting=1,            # Quote all non-numeric fields
                    escapechar='\\'       # Handle escape characters
                )
                print(f"✓ Loaded {len(df)} test queries from {TEST_FILE} (encoding: {encoding})\n")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                # Try with even more lenient settings
                try:
                    df = pd.read_csv(
                        TEST_FILE,
                        encoding=encoding,
                        on_bad_lines='skip',
                        engine='python',
                        sep=',',
                        quotechar='"',
                        doublequote=True
                    )
                    print(f"✓ Loaded {len(df)} test queries from {TEST_FILE} (encoding: {encoding}, lenient mode)\n")
                    break
                except:
                    continue
        
        if df is None:
            print(f"❌ ERROR: Could not read test file with any parsing method")
            print(f"\n💡 Suggestion: Please check the CSV file format:")
            print(f"   1. Open {TEST_FILE} in a text editor")
            print(f"   2. Ensure it has a header row: Query")
            print(f"   3. Ensure queries with commas are properly quoted")
            print(f"   4. Example format:")
            print(f'      Query')
            print(f'      "I need a Java developer who is good at collaboration"')
            print(f'      "Looking for someone with leadership skills"\n')
            print("=" * 70 + "\n")
            return
        
        # Verify the DataFrame has the required 'Query' column
        if 'Query' not in df.columns:
            print(f"❌ ERROR: CSV file must have a 'Query' column")
            print(f"   Found columns: {list(df.columns)}\n")
            print("=" * 70 + "\n")
            return
            
    except FileNotFoundError:
        print(f"❌ ERROR: Test file not found: {TEST_FILE}")
        print("Please ensure the file exists and the path is correct.\n")
        print("=" * 70 + "\n")
        return
    except Exception as e:
        print(f"❌ ERROR: Could not read test file: {str(e)}\n")
        print("=" * 70 + "\n")
        return
    
    # Step 3: Process each query
    print("Step 3: Processing queries through API...")
    print("-" * 70)
    
    results_list = []
    
    for idx, query in enumerate(df['Query'], 1):
        # Display progress
        query_preview = query[:60] + "..." if len(query) > 60 else query
        print(f"\n[{idx}/{len(df)}] Testing query:")
        print(f"  📝 {query_preview}")
        
        # Call API
        recommendations = process_query(query)
        
        # Format results according to submission requirements
        # CRITICAL: One row per recommendation (Query + Assessment_url pairs)
        if not recommendations or len(recommendations) == 0:
            # No recommendations found - add row with None URL
            print(f"  ⚠️  No recommendations found")
            results_list.append({
                "Query": query,
                "Assessment_url": None
            })
        else:
            # Add one row per recommendation
            print(f"  ✅ Found {len(recommendations)} recommendation(s)")
            for rec in recommendations:
                results_list.append({
                    "Query": query,
                    "Assessment_url": rec.get('url', None)
                })
                # Print first few for verification
                if len([r for r in results_list if r['Query'] == query]) <= 3:
                    rec_name = rec.get('name', 'Unknown')
                    print(f"     • {rec_name}")
            
            if len(recommendations) > 3:
                print(f"     ... and {len(recommendations) - 3} more")
    
    print("\n" + "-" * 70)
    print(f"\n✓ Processed all {len(df)} queries")
    print(f"✓ Generated {len(results_list)} total recommendation rows\n")
    
    # Step 4: Create output DataFrame
    print("Step 4: Creating submission file...")
    output_df = pd.DataFrame(results_list)
    
    # Ensure the deliverables directory exists
    os.makedirs("deliverables", exist_ok=True)
    
    # Save to CSV
    output_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"✓ Submission file saved to: {OUTPUT_FILE}")
    
    # Step 5: Display summary statistics
    print("\n" + "=" * 70)
    print("Summary Statistics")
    print("=" * 70)
    
    total_queries = len(df)
    total_rows = len(output_df)
    queries_with_results = len(output_df[output_df['Assessment_url'].notna()]['Query'].unique())
    queries_without_results = total_queries - queries_with_results
    avg_recs_per_query = total_rows / total_queries if total_queries > 0 else 0
    
    print(f"  Total Test Queries:           {total_queries}")
    print(f"  Total Output Rows:            {total_rows}")
    print(f"  Queries with Results:         {queries_with_results}")
    print(f"  Queries without Results:      {queries_without_results}")
    print(f"  Avg Recommendations/Query:    {avg_recs_per_query:.2f}")
    
    # Show sample of output
    print("\n" + "-" * 70)
    print("Sample Output (first 5 rows):")
    print("-" * 70)
    print(output_df.head(5).to_string(index=False))
    print("-" * 70)
    
    print("\n✓ Test run complete!")
    print("\n📦 Submission file ready at: deliverables/final_submission.csv")
    print("\n" + "=" * 70 + "\n")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test run interrupted by user")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        print("=" * 70 + "\n")
        import traceback
        traceback.print_exc()