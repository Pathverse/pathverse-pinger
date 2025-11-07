# Project Brief: Pathverse Pinger

## Purpose
Automated service monitoring system that pings multiple service components and reports status changes to Atlassian Statuspage.

## Core Requirements

### Service Monitoring
- Check health of multiple services/components
- Each service has its own directory under `pings/{service-name}/`
- Each service contains:
  - `config.json` - Contains only `componentKey` for Statuspage
  - `ping.py` - Custom health check script that returns 1 (up) or 0 (down)

### Status Management
- Cache service status (1/0) between checks
- Compare current status with previous cached status
- Only call Atlassian Statuspage API when status changes
- Update cache after each check

### Universal GitHub Action
- Single GitHub Action workflow that:
  1. Discovers all services in `pings/` directory
  2. Sets up Python environment
  3. Executes each service's `ping.py` script
  4. Manages status comparison and caching
  5. Calls Statuspage API only on status changes

### API Integration
- Atlassian Statuspage API v2
- Update component status when service state changes
- Use componentKey from config to identify which component to update

## Design Principles
- **Universal Design**: One action handles all services
- **Minimal Config**: Only componentKey needed per service
- **Change Detection**: Only act when status changes
- **Extensible**: Easy to add new services by creating new directory

## Current State
- Repository initialized
- One service configured: `webapp` with componentKey

## Out of Scope
- Service names and descriptions in config (handled by Statuspage)
- Multiple status types (only up/down binary state)
- Historical status tracking
- Manual status overrides
