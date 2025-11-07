# Technical Context

## Technology Stack

### Runtime
- **Python 3.x**: Core scripting language
- **GitHub Actions**: Scheduling and automation platform
- **PowerShell**: Windows environment shell

### Key Libraries (requirements.txt)
- `requests`: HTTP client for Statuspage API
- Standard library only for core logic (os, json, subprocess)

### APIs
- **Atlassian Statuspage API v2**
  - Endpoint: `https://api.statuspage.io/v1/`
  - Authentication: API Key (via headers)
  - Component status updates

## Project Structure

```
pathverse-pinger/
├── .github/
│   └── workflows/
│       └── check-services.yml       # GitHub Action workflow
├── pings/
│   └── {service-name}/
│       ├── config.json              # { "componentKey": "key" }
│       └── ping.py                  # Returns 1 (up) or 0 (down)
├── cache/
│   └── status.json                  # Persisted status cache
├── memory-bank/                     # Project documentation
├── main.py                          # Orchestrator
├── statuspage.py                    # Statuspage API client
├── requirements.txt                 # Python dependencies
└── README.md
```

## Environment Variables / Secrets

Required GitHub Secrets:
- `STATUSPAGE_API_KEY`: Atlassian Statuspage API key
- `STATUSPAGE_PAGE_ID`: Your Statuspage page identifier

## Development Setup

1. Python 3.x installed
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables for local testing
4. Run: `python main.py`

## Deployment

### GitHub Actions Configuration
- **Trigger**: Schedule (cron expression)
- **Runner**: `ubuntu-latest` (or Windows if needed)
- **Python Setup**: actions/setup-python@v4
- **Cache**: GitHub Actions cache for status.json
- **Secrets**: Access via `${{ secrets.SECRET_NAME }}`

## Technical Constraints

### ping.py Requirements
- Must be executable with Python
- Must print status string to stdout (operational, partial_outage, major_outage, etc.)
- Should handle its own errors and return appropriate status
- Should execute quickly (recommend < 30 seconds)
- Exit with code 0 (success is expected even on service failure - failure is a valid status)

### Cache Persistence
- GitHub Actions: Use actions/cache to persist between runs
- Local: File system storage in `cache/` directory
- Format: JSON
- Must handle missing cache gracefully (first run)

### API Rate Limits
- Statuspage API has rate limits
- Change-based updates minimize API calls
- No parallel updates to same component

## Tool Usage Patterns

### Service Discovery
```python
import os
services = [d for d in os.listdir('pings') if os.path.isdir(f'pings/{d}')]
```

### Executing ping.py
```python
import subprocess
result = subprocess.run(['python', f'pings/{service}/ping.py'], 
                       capture_output=True, text=True)
status = result.stdout.strip()  # Get status string from stdout
```

### Status Comparison
```python
current_status = execute_ping(service)  # Returns status string
cached_status = load_from_cache(service)
if current_status != cached_status:
    update_statuspage(service, current_status)
    update_cache(service, current_status)
```

## Dependencies

### External Services
- Atlassian Statuspage (API availability required)
- GitHub (for Actions execution)

### Runtime Dependencies
- Python 3.7+ (for subprocess, json, os modules)
- Network connectivity for API calls
- File system write access for cache
