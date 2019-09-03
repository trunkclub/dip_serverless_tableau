# Serverless Tableau

## Purpose
Repo for Lambda functions related to our Tableau servers.

## Endpoints
1. `/queue_extracts/{payload}` PUT <br>
For queuing Tableau extracts to run. <br>
Expected payload:
```
{
  "payload": [
    {
      "database": "reporting",
      "extracts": [
        "Employee Metrics"
      ]
    },
    {
      "database": "analyst",
      "extracts": [
        "Employee Timesheet by Day Metrics",
        "Transfer Summary"
      ]
    }
  ]
}
```

