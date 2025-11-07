"""
Main orchestrator for Pathverse service monitoring.
Discovers services, executes health checks, and updates Statuspage.
"""
import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from statuspage import StatuspageClient

# Paths
PINGS_DIR = Path(__file__).parent / 'pings'
CACHE_DIR = Path(__file__).parent / 'cache'
CACHE_FILE = CACHE_DIR / 'status.json'

def load_secrets():
    """
    Load all secrets from environment.
    GitHub Actions passes secrets as SECRETS_JSON.
    For local dev, reads from individual env vars.
    
    Returns:
        dict: All available secrets
    """
    secrets = {}
    
    # Try to load from SECRETS_JSON (GitHub Actions)
    secrets_json = os.environ.get('SECRETS_JSON')
    if secrets_json:
        try:
            secrets = json.loads(secrets_json)
        except json.JSONDecodeError:
            print("Warning: Could not parse SECRETS_JSON")
    
    # Also check individual env vars (for local dev or fallback)
    for key, value in os.environ.items():
        if value:
            secrets[key] = value
    
    return secrets

def discover_services():
    """
    Discover all services in the pings directory.
    
    Returns:
        list: List of service names
    """
    if not PINGS_DIR.exists():
        return []
    
    services = []
    for item in PINGS_DIR.iterdir():
        if item.is_dir() and (item / 'ping.py').exists() and (item / 'config.json').exists():
            services.append(item.name)
    
    return sorted(services)

def load_service_config(service_name):
    """
    Load configuration for a service.
    
    Args:
        service_name: Name of the service
    
    Returns:
        dict: Service configuration
    """
    config_path = PINGS_DIR / service_name / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def execute_ping(service_name):
    """
    Execute ping.py for a service and get status.
    
    Args:
        service_name: Name of the service
    
    Returns:
        str: Status (operational, partial_outage, major_outage, etc.)
    """
    ping_script = PINGS_DIR / service_name / 'ping.py'
    
    try:
        result = subprocess.run(
            [sys.executable, str(ping_script)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Get status from stdout
        status = result.stdout.strip()
        
        if not status:
            print(f"Warning: {service_name} ping.py returned empty output, assuming major_outage")
            return 'major_outage'
        
        return status
    
    except subprocess.TimeoutExpired:
        print(f"Error: {service_name} ping.py timed out, assuming major_outage")
        return 'major_outage'
    except Exception as e:
        print(f"Error executing {service_name} ping.py: {e}, assuming major_outage")
        return 'major_outage'

def load_cache():
    """
    Load status cache from disk.
    
    Returns:
        dict: Cached service statuses
    """
    if not CACHE_FILE.exists():
        return {}
    
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load cache: {e}")
        return {}

def save_cache(cache):
    """
    Save status cache to disk.
    
    Args:
        cache: Cache dictionary to save
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, indent=2, fp=f)

def process_service(service_name, statuspage_client, cache, secrets):
    """
    Process a single service: check status, compare with cache, update if changed.
    
    Args:
        service_name: Name of the service
        statuspage_client: StatuspageClient instance
        cache: Cache dictionary
        secrets: Dictionary of all secrets
    
    Returns:
        bool: True if status changed, False otherwise
    """
    print(f"\n[{service_name}] Checking status...")
    
    # Load service config
    config = load_service_config(service_name)
    component_key = config.get('componentKey')
    
    if not component_key:
        print(f"Error: {service_name} config missing componentKey")
        return False
    
    # Get component ID from secrets using the key (case-insensitive)
    component_id = secrets.get(component_key) or secrets.get(component_key.upper())
    
    if not component_id:
        print(f"Error: {service_name} component ID not found in secrets (tried: {component_key}, {component_key.upper()})")
        return False
    
    print(f"[{service_name}] Component ID: {component_id}")
    
    # Execute ping
    current_status = execute_ping(service_name)
    print(f"[{service_name}] Current status: {current_status}")
    
    # Get cached status
    cached_entry = cache.get(service_name, {})
    cached_status = cached_entry.get('status')
    
    # Check if status changed
    status_changed = current_status != cached_status
    
    if status_changed:
        print(f"[{service_name}] Status changed from {cached_status} to {current_status}")
        
        # Update Statuspage
        try:
            statuspage_client.update_component_status(component_id, current_status)
            print(f"[{service_name}] Successfully updated Statuspage")
        except Exception as e:
            print(f"[{service_name}] Error updating Statuspage: {e}")
            return False
    else:
        print(f"[{service_name}] Status unchanged, skipping Statuspage update")
    
    # Update cache
    now = datetime.utcnow().isoformat() + 'Z'
    cache[service_name] = {
        'status': current_status,
        'last_check': now,
        'last_change': now if status_changed else cached_entry.get('last_change', now)
    }
    
    return status_changed

def main():
    """Main orchestration function."""
    print("=== Pathverse Service Monitor ===")
    print(f"Time: {datetime.utcnow().isoformat()}Z\n")
    
    # Load secrets
    secrets = load_secrets()
    print(f"Loaded {len(secrets)} secrets from environment\n")
    
    # Discover services
    services = discover_services()
    print(f"Discovered {len(services)} service(s): {', '.join(services)}")
    
    if not services:
        print("No services found. Exiting.")
        return
    
    # Initialize Statuspage client
    try:
        statuspage_client = StatuspageClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set STATUSPAGE_API_KEY and STATUSPAGE_PAGE_ID environment variables")
        sys.exit(1)
    
    # Load cache
    cache = load_cache()
    
    # Process each service
    changes = 0
    for service_name in services:
        try:
            if process_service(service_name, statuspage_client, cache, secrets):
                changes += 1
        except Exception as e:
            print(f"[{service_name}] Unexpected error: {e}")
    
    # Save cache
    save_cache(cache)
    
    print("\n=== Summary ===")
    print(f"Services checked: {len(services)}")
    print(f"Status changes: {changes}")
    print(f"Cache saved to: {CACHE_FILE}")

if __name__ == '__main__':
    main()
