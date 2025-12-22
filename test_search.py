#!/usr/bin/env python3
"""
Simple test script to search your neural search engine
"""
import requests
import json
from typing import Optional

API_URL = "http://localhost:8000"

def search(query: str, limit: int = 5, category: Optional[str] = None):
    """Search for articles"""
    payload = {
        "query": query,
        "limit": limit
    }
    if category:
        payload["category"] = category
    
    response = requests.post(f"{API_URL}/search", json=payload)
    
    if response.status_code == 200:
        results = response.json()
        print(f"\n🔍 Search results for: '{query}'")
        print(f"Found {len(results)} results\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Score: {result['score']:.4f} | Category: {result['category']}")
            print(f"Title: {result['title']}")
            print(f"Content: {result['content'][:200]}...")
            print("-" * 80)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def get_stats():
    """Get collection statistics"""
    response = requests.get(f"{API_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print("\n📊 Collection Statistics:")
        print(f"   Total articles indexed: {stats['points_count']}")
        print(f"   Collection status: {stats['status']}")
    else:
        print(f"Error getting stats: {response.text}")

def get_categories():
    """Get all categories"""
    response = requests.get(f"{API_URL}/categories")
    if response.status_code == 200:
        cats = response.json()
        print("\n📁 Available Categories:")
        for cat in cats['categories']:
            print(f"   - {cat}")
    else:
        print(f"Error getting categories: {response.text}")

if __name__ == "__main__":
    print("=" * 80)
    print("NEURAL SEARCH ENGINE - TEST SCRIPT")
    print("=" * 80)
    
    # Get stats first
    get_stats()
    get_categories()
    
    # Example searches
    print("\n" + "=" * 80)
    print("EXAMPLE SEARCHES")
    print("=" * 80)
    
    # Search 1: General tech
    search("artificial intelligence and machine learning")
    
    # Search 2: Crypto
    search("cryptocurrency and blockchain technology")
    
    # Search 3: Security
    search("cybersecurity threats and data protection")
    
    # Search 4: With category filter
    print("\n\n🎯 Filtered search (AI category only):")
    search("technology innovations", limit=3, category="AI")
    
    print("\n" + "=" * 80)
    print("Test complete! Try your own searches:")
    print("  python test_search.py")
    print("=" * 80)