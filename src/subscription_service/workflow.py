import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio import activity

from subscription_service.common import Subscription, UpdateSubscription
import logging

log = logging.getLogger(__name__)


@workflow.defn
class SubscriptionWorkflow:
    def __init__(self) -> None:
        self._cancelled = False
        self._billing_period_number = 1
        self._total_charged = 0
        self._billing_period_charge_amount = 0

    @workflow.run
    async def run(self, subscription: Subscription) -> str:
        self._billing_period_charge_amount = subscription.billing_period_charge_amount

        # Send welcome email to customer
        await workflow.execute_activity(
            send_welcome_email,
            subscription,
            start_to_close_timeout=timedelta(seconds=5),
        )

        try:
            await workflow.wait_condition(
                lambda: self._cancelled, timeout=subscription.trial_period
            )
            await workflow.execute_activity(
                send_subscription_cancelled_during_trial_period_email,
                subscription,
                start_to_close_timeout=timedelta(seconds=5),
            )
            return f"Subscription cancelled during trial period for: {subscription.id}"
        except asyncio.TimeoutError:
            pass

        while True:
            if self._billing_period_number > subscription.max_billing_periods:
                break
            if self._cancelled:
                await workflow.execute_activity(
                    send_subscription_cancelled_email,
                    subscription,
                    start_to_close_timeout=timedelta(seconds=5),
                )
                return f"Subscription cancelled for: {subscription.id}, total charged: {self._total_charged}"

            workflow.logger.info(
                "Charging %s amount %d",
                subscription.id,
                self._billing_period_charge_amount,
            )

            await workflow.execute_activity(
                charge_customer_for_billing_period,
                args=(subscription, self._billing_period_charge_amount),
                start_to_close_timeout=timedelta(seconds=5),
            )
            self._total_charged += self._billing_period_charge_amount
            self._billing_period_number += 1

            # Wait for the next billing period or until the subscription is cancelled
            await workflow.sleep(subscription.billing_period)

        # If the subscription period is over and not cancelled, notify the customer to buy a new subscription
        await workflow.execute_activity(
            send_subscription_completed_email,
            subscription,
            start_to_close_timeout=timedelta(seconds=5),
        )
        return f"Subscription completed for: {subscription.id}, total charged: {self._total_charged}"

    @workflow.signal
    async def cancel(self) -> None:
        self._cancelled = True

    @workflow.signal
    async def update(self, update: UpdateSubscription) -> None:
        self._billing_period_charge_amount = update.billing_period_charge_amount

    @workflow.query
    def billing_period_number(self) -> int:
        return self._billing_period_number

    @workflow.query
    def billing_period_charge_amount(self) -> int:
        return self._billing_period_charge_amount

    @workflow.query
    def total_charged(self) -> int:
        return self._total_charged


@activity.defn
async def send_welcome_email(subscription: Subscription):
    log.info("Sending welcome email to %s", subscription.customer.email)


@activity.defn
async def send_subscription_cancelled_during_trial_period_email(
    subscription: Subscription,
):
    log.info("Sending trial cancellation email to %s", subscription.customer.email)


@activity.defn
async def charge_customer_for_billing_period(subscription: Subscription, amount: int):
    log.info(
        "Charging %s amount %d for their billing period",
        subscription.customer.email,
        amount,
    )


@activity.defn
async def send_subscription_cancelled_email(subscription: Subscription):
    log.info("Sending subscription cancelled email to %s", subscription.customer.email)


@activity.defn
async def send_subscription_completed_email(subscription: Subscription):
    log.info("Sending subscription completed email to %s", subscription.customer.email)
