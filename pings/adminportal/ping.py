"""
Admin Portal health check script.
Returns status to stdout: operational or major_outage
"""
import requests
import sys

def check_adminportal():
    """
    Check admin portal health.
    
    Returns:
        str: Status level (operational or major_outage)
    """
    try:
        response = requests.get('https://admin.pathverse.ca/auth/login', timeout=10)
        if response.status_code == 200:
            return 'operational'
        else:
            return 'major_outage'
    except requests.exceptions.RequestException:
        return 'major_outage'

if __name__ == '__main__':
    status = check_adminportal()
    print(status)
    sys.exit(0)
