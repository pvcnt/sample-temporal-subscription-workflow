import asyncio
import uvicorn
from uvicorn.loops.uvloop import uvloop_setup
import logging


from subscription_service.client import make_client
from subscription_service.rest import make_app
from subscription_service.worker import make_worker


async def serve():
    client = await make_client()
    worker = make_worker(client)

    app = make_app(client)
    config = uvicorn.Config(app, loop="uvloop", port=8080)
    server = uvicorn.Server(config)

    tasks = [
        asyncio.create_task(server.serve(), name="Server"),
        asyncio.create_task(worker.run(), name="Worker"),
    ]
    await asyncio.wait(tasks)


def main():
    logging.basicConfig(level="INFO")
    uvloop_setup()
    asyncio.run(serve())
