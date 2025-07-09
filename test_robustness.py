#!/usr/bin/env python3
"""
Test script to demonstrate the robustness improvements of the price comparison tool.
"""

import sys
import json
from main import fetch_prices, normalize_query, clean_price, llm_product_match

def test_price_cleaning():
    """Test the price cleaning functionality."""
    print("Testing price cleaning...")
    
    test_cases = [
        ("$1,234.56", "1234.56"),
        ("₹2,500", "2500"),
        ("1,234", "1234"),
        ("$999.99", "999.99"),
        ("Invalid", None),
        ("", None),
        ("$1,234,567.89", "1234567.89"),
    ]
    
    for input_price, expected in test_cases:
        result = clean_price(input_price)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_price}' -> '{result}' (expected: '{expected}')")

def test_query_normalization():
    """Test the query normalization functionality."""
    print("\nTesting query normalization...")
    
    test_cases = [
        ("iPhone 14 Pro, 128GB", "iphone 14 pro 128gb"),
        ("boAt Airdopes 311 Pro!", "boat airdopes 311 pro"),
        ("Samsung Galaxy S23 Ultra", "samsung galaxy s23 ultra"),
        ("", ""),
    ]
    
    for input_query, expected in test_cases:
        result = normalize_query(input_query)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_query}' -> '{result}' (expected: '{expected}')")

def test_product_matching():
    """Test the product matching functionality."""
    print("\nTesting product matching...")
    
    test_cases = [
        ("iPhone 14 Pro", "Apple iPhone 14 Pro 128GB Space Black", True),
        ("iPhone 14 Pro", "Samsung Galaxy S23 Ultra", False),
        ("boAt Airdopes", "boAt Airdopes 311 Pro Wireless Earbuds", True),
        ("boAt Airdopes", "Sony WH-1000XM4 Headphones", False),
        ("", "Some Product", False),
        ("iPhone", "", False),
    ]
    
    for query, title, expected in test_cases:
        result = llm_product_match(query, title)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Query: '{query}' | Title: '{title}' -> {result} (expected: {expected})")

def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\nTesting error handling...")
    
    # Test with empty country
    print("  Testing empty country...")
    try:
        results = fetch_prices("", "iPhone")
        print(f"    Result: {len(results)} items (should be 0)")
    except Exception as e:
        print(f"    Error caught: {e}")
    
    # Test with empty query
    print("  Testing empty query...")
    try:
        results = fetch_prices("US", "")
        print(f"    Result: {len(results)} items (should be 0)")
    except Exception as e:
        print(f"    Error caught: {e}")
    
    # Test with invalid country
    print("  Testing invalid country...")
    try:
        results = fetch_prices("XX", "iPhone")
        print(f"    Result: {len(results)} items (should be 0)")
    except Exception as e:
        print(f"    Error caught: {e}")

def run_live_tests():
    """Run live tests with real queries."""
    print("\nRunning live tests...")
    
    test_queries = [
        {"country": "US", "query": "laptop", "description": "Generic laptop search"},
        {"country": "US", "query": "wireless headphones", "description": "Headphones search"},
        {"country": "IN", "query": "mobile phone", "description": "Mobile phone search"},
    ]
    
    for test in test_queries:
        print(f"\n  Testing: {test['description']}")
        print(f"  Country: {test['country']}, Query: '{test['query']}'")
        
        try:
            results = fetch_prices(test['country'], test['query'])
            print(f"  Results: {len(results)} items found")
            
            if results:
                print("  Sample results:")
                for i, result in enumerate(results[:3]):  # Show first 3 results
                    print(f"    {i+1}. {result['productName'][:50]}... - {result['price']} {result['currency']}")
            
        except Exception as e:
            print(f"  Error: {e}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("ROBUSTNESS TEST SUITE")
    print("=" * 60)
    
    # Unit tests
    test_price_cleaning()
    test_query_normalization()
    test_product_matching()
    test_error_handling()
    
    # Live tests (optional - can be slow)
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        run_live_tests()
    else:
        print("\nSkipping live tests (use --live flag to run them)")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main() 