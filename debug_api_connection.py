#!/usr/bin/env python3
"""
Debug script to test CloudFront API routing
"""

import requests
import json

def test_cloudfront_api():
    """Test API endpoints through CloudFront"""
    
    cloudfront_url = "https://d173g01t5c4w0h.cloudfront.net"
    alb_url = "http://ai-recipes-generator-alb-staging-335153089.us-east-1.elb.amazonaws.com"
    
    endpoints = [
        "/health",
        "/api/stats", 
        "/api/recipes"
    ]
    
    print("🧪 Testing API connectivity...")
    print("=" * 60)
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}")
        
        # Test CloudFront
        try:
            response = requests.get(f"{cloudfront_url}{endpoint}", timeout=10)
            print(f"✅ CloudFront: {response.status_code} - {response.reason}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ CloudFront: Error - {str(e)}")
        
        # Test ALB directly
        try:
            response = requests.get(f"{alb_url}{endpoint}", timeout=10)
            print(f"✅ ALB Direct: {response.status_code} - {response.reason}")
        except Exception as e:
            print(f"❌ ALB Direct: Error - {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Recommendations:")
    print("1. If CloudFront fails but ALB works: CloudFront routing issue")
    print("2. If both fail: Backend service is down")
    print("3. If both work: Frontend configuration issue")

if __name__ == "__main__":
    test_cloudfront_api()
