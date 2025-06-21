#!/usr/bin/env python3
"""
Check Feedly API rate limit status and estimate downtime.
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_rate_limit_status():
    """Check the current rate limit status of your Feedly API token"""
    
    # Get access token
    access_token = os.getenv("FEEDLY_ACCESS_TOKEN")
    if not access_token:
        print("Error: FEEDLY_ACCESS_TOKEN not found in environment variables")
        print("Please set your Feedly access token in .env file")
        sys.exit(1)
    
    # Feedly API base URL
    base_url = "https://cloud.feedly.com/v3"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Checking rate limit status at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        # Make a simple API call to check status
        response = requests.get(
            f"{base_url}/profile",
            headers=headers,
            timeout=10
        )
        
        # Check response headers for rate limit info
        rate_limit_headers = {
            "X-RateLimit-Limit": response.headers.get("X-RateLimit-Limit"),
            "X-RateLimit-Remaining": response.headers.get("X-RateLimit-Remaining"),
            "X-RateLimit-Reset": response.headers.get("X-RateLimit-Reset"),
            "Retry-After": response.headers.get("Retry-After")
        }
        
        if response.status_code == 200:
            print("✅ API is accessible - No rate limit issues")
            print(f"Status Code: {response.status_code}")
            
            # Display rate limit headers if available
            if any(rate_limit_headers.values()):
                print("\nRate Limit Information:")
                for header, value in rate_limit_headers.items():
                    if value:
                        print(f"  {header}: {value}")
                        
                        # If reset time is provided, calculate time remaining
                        if header == "X-RateLimit-Reset" and value:
                            try:
                                reset_time = datetime.fromtimestamp(int(value))
                                time_remaining = reset_time - datetime.now()
                                if time_remaining.total_seconds() > 0:
                                    print(f"  Reset Time: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}")
                                    print(f"  Time Until Reset: {time_remaining}")
                            except:
                                pass
            else:
                print("\nNo rate limit headers found in response")
                print("(Feedly may not expose rate limit information in headers)")
                
        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded!")
            print(f"Status Code: {response.status_code}")
            
            # Check for Retry-After header
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    # Retry-After might be in seconds or a date
                    if retry_after.isdigit():
                        wait_seconds = int(retry_after)
                        wait_until = datetime.now() + timedelta(seconds=wait_seconds)
                        print(f"\nRetry-After: {wait_seconds} seconds")
                        print(f"You can retry at: {wait_until.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"Time to wait: {timedelta(seconds=wait_seconds)}")
                    else:
                        # It might be a date string
                        wait_until = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S GMT")
                        time_to_wait = wait_until - datetime.now()
                        print(f"\nRetry-After: {retry_after}")
                        print(f"Time to wait: {time_to_wait}")
                except Exception as e:
                    print(f"\nRetry-After header: {retry_after}")
                    print(f"(Could not parse: {e})")
            else:
                print("\nNo Retry-After header found")
                print("Default wait time is typically 60 seconds")
                
            # Display all rate limit headers
            print("\nAll Rate Limit Headers:")
            for header, value in rate_limit_headers.items():
                if value:
                    print(f"  {header}: {value}")
                    
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking API status: {e}")
        
    print("\n" + "-" * 50)
    print("Tips:")
    print("- Feedly API typically has a rate limit of 250 requests per hour")
    print("- Rate limit resets on a rolling basis")
    print("- If rate limited, wait at least 60 seconds before retrying")
    print("- Consider implementing exponential backoff for production use")

if __name__ == "__main__":
    check_rate_limit_status()