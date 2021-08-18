from aiohttp import ClientSession
from asyncio import run as asyncio_run
from multiprocessing import JoinableQueue, Process, Queue


SERVER_URL = "http://127.0.0.1:5000/"
PROCESSES_COUNT = 1


class ReceiverProcess(Process):
    def __init__(self, task_queue, result_queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    async def post(self, session, task):
        resp = await session.post(SERVER_URL, data=task)
        return await resp.json()

    async def asyncio_sessions(self):
        async with ClientSession() as session:
            # You can change self.task_queue.qsize() to True, if you want to run it forever
            while self.task_queue.qsize():
                task = self.task_queue.get()
                resp = await self.post(session, task)
                self.result_queue.put(resp)

    def run(self):
        asyncio_run(self.asyncio_sessions())


def main():
    task_queue = JoinableQueue()
    result_queue = Queue()

    for receiver in [ReceiverProcess(task_queue, result_queue) for _ in range(PROCESSES_COUNT)]:
        receiver.start()


if __name__ == '__main__':
    main()
