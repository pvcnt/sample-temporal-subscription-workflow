from fastapi import FastAPI
from temporalio.client import Client

from subscription_service.common import (
    TASK_QUEUE_NAME,
    Subscription,
    UpdateSubscription,
)
from subscription_service.workflow import SubscriptionWorkflow


def make_app(client: Client) -> FastAPI:
    app = FastAPI()

    @app.post("/api/subscription")
    async def start_subscription(subscription: Subscription):
        await client.start_workflow(
            SubscriptionWorkflow.run,
            subscription,
            task_queue=TASK_QUEUE_NAME,
            id=f"subscription-{subscription.id}",
        )
        return {"status": "OK"}

    @app.get("/api/subscription/{id}")
    async def get_subscription(id: str):
        handle = client.get_workflow_handle(f"subscription-{id}")
        billing_period_number = await handle.query(
            SubscriptionWorkflow.billing_period_number
        )
        billing_period_charge_amount = await handle.query(
            SubscriptionWorkflow.billing_period_charge_amount
        )
        total_charged = await handle.query(SubscriptionWorkflow.total_charged)
        return {
            "billing_period_number": billing_period_number,
            "billing_period_charge_amount": billing_period_charge_amount,
            "total_charged": total_charged,
        }

    @app.delete("/api/subscription/{id}")
    async def cancel_subscription(id: str):
        handle = client.get_workflow_handle(f"subscription-{id}")
        await handle.signal(SubscriptionWorkflow.cancel)
        return {"status": "OK"}

    @app.post("/api/subscription/{id}")
    async def update_subscription(id: str, update: UpdateSubscription):
        handle = client.get_workflow_handle(f"subscription-{id}")
        await handle.signal(SubscriptionWorkflow.update, update)
        return {"status": "OK"}

    return app
