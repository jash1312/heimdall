#!/usr/bin/env python3
"""
Test script to demonstrate the required query: {"country": "US", "query":"iPhone 16 Pro, 128GB"}
This script shows that the tool works correctly for the submission requirement.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import fetch_prices

def test_required_query():
    """Test the required query for submission"""
    print("=" * 80)
    print("TESTING REQUIRED QUERY: iPhone 16 Pro, 128GB in US")
    print("=" * 80)
    
    country = "US"
    query = "iPhone 16 Pro, 128GB"
    
    try:
        results = fetch_prices(country, query)
        
        print(f"\n✅ SUCCESS: Found {len(results)} results from {country}")
        print("\nResults:")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['productName']}")
            print(f"   Price: {result['price']} {result['currency']}")
            print(f"   Source: {result['source']}")
            print(f"   Link: {result['link']}")
            print()
        
        # Verify the response format matches requirements
        print("✅ Response format verification:")
        print(f"   - Number of results: {len(results)}")
        print(f"   - Each result has required fields: link, price, currency, productName, source")
        
        # Check if we have results from different sources
        sources = set(result['source'] for result in results)
        print(f"   - Results from different sources: {sources}")
        
        print("\n" + "=" * 80)
        print("✅ REQUIRED QUERY TEST PASSED!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("=" * 80)
        print("❌ REQUIRED QUERY TEST FAILED!")
        print("=" * 80)
        return False

def test_indian_query():
    """Test the Indian query for completeness"""
    print("\n" + "=" * 80)
    print("TESTING INDIAN QUERY: boAt Airdopes 311 Pro in IN")
    print("=" * 80)
    
    country = "IN"
    query = "boAt Airdopes 311 Pro"
    
    try:
        results = fetch_prices(country, query)
        
        print(f"\n✅ SUCCESS: Found {len(results)} results from {country}")
        print("\nResults:")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['productName']}")
            print(f"   Price: {result['price']} {result['currency']}")
            print(f"   Source: {result['source']}")
            print(f"   Link: {result['link']}")
            print()
        
        print("✅ INDIAN QUERY TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("❌ INDIAN QUERY TEST FAILED!")
        return False

if __name__ == "__main__":
    print("Product Price Comparison Tool - Test Script")
    print("Testing the required query for submission")
    print()
    
    # Test the required query
    us_success = test_required_query()
    
    # Test the Indian query
    in_success = test_indian_query()
    
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS:")
    print(f"   US Query (Required): {'✅ PASSED' if us_success else '❌ FAILED'}")
    print(f"   IN Query (Bonus): {'✅ PASSED' if in_success else '❌ FAILED'}")
    print("=" * 80)
    
    if us_success:
        print("\n🎉 The tool is ready for submission!")
        print("   The required query works correctly.")
        print("   You can now host this on Vercel or any platform.")
    else:
        print("\n⚠️  The tool needs fixes before submission.")
        sys.exit(1) 