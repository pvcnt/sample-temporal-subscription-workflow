# sample-temporal-subscription-workflow

```bash
temporal server start-dev
```

```bash
uv sync
uv pip install -e .
uv run python -m subscription_service
```

Edit `charge_customer_for_billing_period`: 
```python
raise RuntimeError("ERROR")
```

Edit `charge_customer_for_billing_period`:
```python
raise temporalio.exceptions.ApplicationError("ERROR", non_retryable=True)
```