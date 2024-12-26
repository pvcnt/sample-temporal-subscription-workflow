from temporalio.client import Client
from temporalio.worker import Worker

from subscription_service.common import TASK_QUEUE_NAME
from subscription_service.workflow import SubscriptionWorkflow


import json
from typing import Any, Optional

from pydantic.json import pydantic_encoder
from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DataConverter,
    DefaultPayloadConverter,
    JSONPlainPayloadConverter,
)


async def make_client() -> Client:
    return await Client.connect(
        "localhost:7233",
        data_converter=DataConverter(payload_converter_class=PydanticPayloadConverter),
    )


class PydanticJSONPayloadConverter(JSONPlainPayloadConverter):
    def to_payload(self, value: Any) -> Optional[Payload]:
        return Payload(
            metadata={"encoding": self.encoding.encode()},
            data=json.dumps(
                value, separators=(",", ":"), sort_keys=True, default=pydantic_encoder
            ).encode(),
        )


class PydanticPayloadConverter(CompositePayloadConverter):
    def __init__(self) -> None:
        super().__init__(
            *(
                (
                    c
                    if not isinstance(c, JSONPlainPayloadConverter)
                    else PydanticJSONPayloadConverter()
                )
                for c in DefaultPayloadConverter.default_encoding_payload_converters
            )
        )
