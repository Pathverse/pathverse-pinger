"""
Webapp health check script.
Returns status to stdout: operational, partial_outage, or major_outage
"""
import requests
import sys

def check_webapp():
    """
    Check webapp health with multi-level status detection.
    
    Returns:
        str: Status level (operational, partial_outage, major_outage)
    """
    # First check: version.json (critical endpoint)
    try:
        response = requests.get('https://testweb.pathverse.ca/version.json', timeout=10)
        if response.status_code == 200:
            # If version.json works, service is fully operational
            return 'operational'
        else:
            # If version.json returns non-200, it's a major issue
            return 'major_outage'
    except requests.exceptions.RequestException:
        # Cannot reach version.json - this is major outage
        pass
    
    # Second check: login page (if version.json failed)
    try:
        response = requests.get('https://testweb.pathverse.ca/login', timeout=10)
        if response.status_code == 200:
            # Login works but version.json failed - partial outage
            return 'partial_outage'
        else:
            # Both failed - major outage
            return 'major_outage'
    except requests.exceptions.RequestException:
        # Cannot reach either endpoint - major outage
        return 'major_outage'

if __name__ == '__main__':
    status = check_webapp()
    print(status)
    sys.exit(0)
