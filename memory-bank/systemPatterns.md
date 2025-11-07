# System Patterns

## Architecture Overview

```
GitHub Action (Scheduler)
    ↓
main.py (Orchestrator)
    ↓
├── Service Discovery (scan pings/ directory)
├── For each service:
│   ├── Load config.json → get componentKey
│   ├── Execute ping.py → get status (1/0)
│   ├── Load cache → get previous status
│   ├── Compare statuses
│   └── If changed → statuspage.py → Atlassian API
└── Update cache
```

## Key Design Patterns

### 1. Plugin Architecture
Each service is self-contained:
- Directory: `pings/{service-name}/`
- Config: `config.json` (minimal - just componentKey)
- Logic: `ping.py` (service-specific health check)

Services are discovered dynamically - no central registration needed.

### 2. Status Caching Pattern
```
Current Check → Compare with Cache → Action Decision
                                    ↓
                            Changed: API Call + Update Cache
                            Same: Skip API + Update Cache
```

Cache structure:
```json
{
    "service-name": {
        "status": "operational",  // status string
        "last_check": "ISO timestamp",
        "last_change": "ISO timestamp"
    }
}
```

### 3. Status String Model
- ping.py prints status string to stdout
- Supported statuses: operational, partial_outage, major_outage, degraded_performance, under_maintenance
- Enables multi-level health checking
- Example: webapp checks critical endpoint first, falls back to secondary

### 4. Separation of Concerns

**main.py** - Orchestration
- Service discovery
- Status comparison
- Cache management
- Coordination

**ping.py** - Health Check
- Service-specific logic
- Prints status string to stdout
- Self-contained
- No dependencies on orchestrator

**statuspage.py** - API Client
- Atlassian Statuspage integration
- Authentication
- Status updates
- Error handling

**GitHub Action** - Scheduling
- Trigger on schedule (every 5 minutes)
- Environment setup
- Secret management
- Execution coordination

## Critical Implementation Paths

### Adding a New Service
1. Create `pings/{service-name}/` directory
2. Add `config.json` with componentKey
3. Implement `ping.py` with health check logic
4. Print status string to stdout (operational, partial_outage, major_outage, etc.)
5. Automatic discovery on next run

### Status Change Detection
1. Execute service ping.py
2. Capture stdout for status string
3. Load service status from cache
4. Compare current vs cached
5. If different: trigger API update
6. Update cache with new status and timestamp

### API Integration Flow
1. Load componentKey from config.json
2. Get status string from ping.py
3. Call Atlassian Statuspage API with:
   - Page ID (from environment)
   - Component Key (from config)
   - New Status (from ping.py output)
4. Handle API response and errors
5. Update cache only if successful

### Multi-Level Health Check Example (webapp)
```python
# Check critical endpoint first
try:
    response = requests.get('https://testweb.pathverse.ca/version.json')
    if response.status_code == 200:
        print('operational')  # All good
        sys.exit(0)
except:
    pass  # Fall through to secondary check

# Check secondary endpoint
try:
    response = requests.get('https://testweb.pathverse.ca/login')
    if response.status_code == 200:
        print('partial_outage')  # Login works but version.json failed
        sys.exit(0)
except:
    pass

# Both failed
print('major_outage')
sys.exit(0)
```
