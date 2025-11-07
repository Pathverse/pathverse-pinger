"""
Atlassian Statuspage API client.
Handles component status updates.
"""
import os
import requests
import sys

class StatuspageClient:
    """Client for interacting with Atlassian Statuspage API."""
    
    def __init__(self, api_key=None, page_id=None):
        """
        Initialize Statuspage client.
        
        Args:
            api_key: Statuspage API key (defaults to STATUSPAGE_API_KEY env var)
            page_id: Statuspage page ID (defaults to STATUSPAGE_PAGE_ID env var)
        """
        self.api_key = api_key or os.environ.get('STATUSPAGE_API_KEY')
        self.page_id = page_id or os.environ.get('STATUSPAGE_PAGE_ID')
        
        if not self.api_key:
            raise ValueError("STATUSPAGE_API_KEY not set")
        if not self.page_id:
            raise ValueError("STATUSPAGE_PAGE_ID not set")
        
        self.base_url = f"https://api.statuspage.io/v1/pages/{self.page_id}"
        self.headers = {
            'Authorization': f'OAuth {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def update_component_status(self, component_id, status):
        """
        Update component status on Statuspage.
        
        Args:
            component_id: Component ID from Statuspage
            status: New status (operational, partial_outage, major_outage, etc.)
        
        Returns:
            dict: API response
        
        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        url = f"{self.base_url}/components/{component_id}"
        payload = {
            'component': {
                'status': status
            }
        }
        
        response = requests.patch(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        return response.json()

def main():
    """CLI interface for testing Statuspage client."""
    if len(sys.argv) < 3:
        print("Usage: python statuspage.py <component_id> <status>")
        print("Status options: operational, degraded_performance, partial_outage, major_outage")
        sys.exit(1)
    
    component_id = sys.argv[1]
    status = sys.argv[2]
    
    client = StatuspageClient()
    result = client.update_component_status(component_id, status)
    print(f"Updated component {component_id} to {status}")
    print(f"Response: {result}")

if __name__ == '__main__':
    main()
