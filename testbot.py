# test_without_embeddings.py
import time
import re
from chatbot import load_scholarships

def simple_search(query, scholarships):
    """Simple keyword search - NO embeddings, NO API"""
    query_lower = query.lower()
    results = []
    for s in scholarships:
        if query_lower in s['content'].lower() or query_lower in s['name'].lower():
            results.append(s)
    return results

def simple_response(scholarship):
    """Simple response - NO API call"""
    if not scholarship:
        return "No matching scholarship found."
    return scholarship['content'][:500]

# Load data
scholarships = load_scholarships()

test_questions = [
    "DAAD scholarship requirements",
    "Bilkent University scholarship",
    "PhD scholarships"
]

print("Testing WITHOUT Embeddings (Simple Search)")
print("=" * 50)

for q in test_questions:
    start = time.time()
    results = simple_search(q, scholarships)
    search_time = time.time() - start
    
    response = simple_response(results[0] if results else None)
    
    print(f"\n🔍 {q}")
    print(f"⏱️ Search Time: {search_time:.3f}s")
    print(f"📚 Results: {len(results)} scholarship(s)")
    print(f"📝 Response: {response[:150]}...")