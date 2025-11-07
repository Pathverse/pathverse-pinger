# Product Context

## Problem Statement
Services and components can go down without immediate awareness, leading to poor user experience and delayed incident response. Manual monitoring is time-consuming and unreliable.

## Solution
Automated monitoring system that:
- Continuously checks service health
- Detects status changes instantly
- Automatically updates public status page
- Reduces manual monitoring overhead

## User Experience

### For Operations Team
- Add new service monitoring by creating a directory with two files
- No complex configuration required
- Automatic status page updates
- Status changes trigger appropriate actions

### For End Users (via Statuspage)
- Real-time service status visibility
- Automatic notifications when services go down
- Transparent incident communication

## How It Works

1. **Service Discovery**: System scans `pings/` directory for all services
2. **Health Checks**: Each service defines its own ping logic (HTTP, database, API, etc.)
3. **Status Tracking**: Results cached to detect changes
4. **Incident Reporting**: Status changes pushed to Atlassian Statuspage
5. **Efficiency**: Only API calls made when status actually changes

## Key Benefits
- **Automated**: No manual intervention required
- **Scalable**: Easy to add/remove services
- **Efficient**: Minimal API calls (only on changes)
- **Flexible**: Each service defines its own health check logic
- **Transparent**: Public status page keeps users informed
