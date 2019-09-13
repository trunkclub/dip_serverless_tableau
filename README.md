# Serverless Tableau

## Purpose
Repo for Lambda functions related to our Tableau servers.

## Endpoints
1. `/queue_extracts` PUT <br>
For queuing Tableau extracts to run. <br>
Expected payload:
```
{
  "payload": [
    {
      "server": "reporting",
      "extracts": [
        "Employee Metrics"
      ]
    },
    {
      "server": "analyst",
      "extracts": [
        "Employee Timesheet by Day Metrics",
        "Transfer Summary"
      ]
    }
  ]
}
```

