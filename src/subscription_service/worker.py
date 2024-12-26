from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from temporalio import workflow

from subscription_service.common import TASK_QUEUE_NAME
from subscription_service.workflow import SubscriptionWorkflow

with workflow.unsafe.imports_passed_through():
    from subscription_service.workflow import (
        send_subscription_cancelled_during_trial_period_email,
        send_subscription_cancelled_email,
        send_subscription_completed_email,
        send_welcome_email,
        charge_customer_for_billing_period,
    )


def make_worker(client: Client) -> Worker:
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[SubscriptionWorkflow],
        activities=[
            send_subscription_cancelled_during_trial_period_email,
            send_subscription_cancelled_email,
            send_subscription_completed_email,
            send_welcome_email,
            charge_customer_for_billing_period,
        ],
        workflow_runner=UnsandboxedWorkflowRunner(),
    )
    return worker
