from pydantic import BaseModel


TASK_QUEUE_NAME = "subscriptions-task-queue"


class Customer(BaseModel):
    first_name: str
    last_name: str
    email: str


class Subscription(BaseModel):
    id: str
    trial_period: int
    billing_period: int
    max_billing_periods: int
    billing_period_charge_amount: int
    customer: Customer


class UpdateSubscription(BaseModel):
    billing_period_charge_amount: int
