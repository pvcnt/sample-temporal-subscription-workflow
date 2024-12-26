#!/bin/bash -ex

subscription_id=${1:-1}

curl -X POST \
    -d '{"id": "'$subscription_id'", "trial_period": 60, "billing_period": 60, "max_billing_periods": 12, "billing_period_charge_amount": 100, "customer": {"first_name": "Arsène", "last_name": "Lupin", "email": "a@lupin.fr"}}' \
    -H 'Content-Type: application/json' \
    http://localhost:8080/api/subscription