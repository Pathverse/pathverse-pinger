# Pathverse Pinger

Automated service monitoring system that pings service components and reports status changes to Atlassian Statuspage.

## How It Works

1. **GitHub Action** runs every 5 minutes
2. **Discovers services** in the `pings/` directory
3. **Executes health checks** via each service's `ping.py`
4. **Compares status** with cached previous status
5. **Updates Statuspage** only when status changes
6. **Caches results** for next run

## Project Structure

```
pathverse-pinger/
├── .github/workflows/
│   └── check-services.yml    # GitHub Action (runs every 5 minutes)
├── pings/
│   └── {service-name}/
│       ├── config.json       # { "componentKey": "key" }
│       └── ping.py           # Returns status to stdout
├── cache/
│   └── status.json           # Cached service statuses
├── main.py                   # Orchestrator
├── statuspage.py             # Statuspage API client
└── requirements.txt          # Python dependencies
```

## Setup

### 1. Configure GitHub Secrets

Add these secrets to your repository:
- `STATUSPAGE_API_KEY` - Your Atlassian Statuspage API key
- `STATUSPAGE_PAGE_ID` - Your Statuspage page ID
- `{service}_key` - Component ID for each service (e.g., `webapp_key`, `api_key`)

**The workflow automatically passes all secrets to the script - no manual updates needed!**

### 2. Install Dependencies (for local testing)

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables (for local testing)

```bash
export STATUSPAGE_API_KEY="your-api-key"
export STATUSPAGE_PAGE_ID="your-page-id"
export webapp_key="your-webapp-component-id"
```

## Adding a New Service

1. Create a directory: `pings/{service-name}/`
2. Add `config.json` with a secret key name:
   ```json
   {
     "componentKey": "myservice_key"
   }
   ```
3. Add GitHub Secret `myservice_key` with the actual component ID from Statuspage
4. **That's it!** The action automatically discovers and monitors it.
3. Add `ping.py` that prints status to stdout:
   ```python
   import sys
   
   def check_service():
       # Your health check logic
       if service_is_healthy:
           return 'operational'
       elif partially_degraded:
           return 'partial_outage'
       else:
           return 'major_outage'
   
   if __name__ == '__main__':
       status = check_service()
       print(status)
       sys.exit(0)
   ```

## Status Levels

Your `ping.py` can return any valid Statuspage status:
- `operational` - Service fully functional
- `degraded_performance` - Service slow but working
- `partial_outage` - Some features down
- `major_outage` - Service completely down
- `under_maintenance` - Planned maintenance

## Running Locally

```bash
python main.py
```

## Example: webapp Service

The `webapp` service demonstrates multi-level health checking:
1. Checks `https://testweb.pathverse.ca/version.json` - if fails → `major_outage`
2. Falls back to `https://testweb.pathverse.ca/login` - if fails → `partial_outage`
3. If both succeed → `operational`
