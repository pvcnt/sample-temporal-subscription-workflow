#!/bin/bash -ex

subscription_id=${1:-1}

curl -X DELETE http://localhost:8080/api/subscription/$subscription_id