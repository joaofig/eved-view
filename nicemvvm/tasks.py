import asyncio

from nicemvvm.singleton import singleton


@singleton
class ManagedTasks:
    def __init__(self):
        self._tasks: set[asyncio.Task] = set()

    def create(self, coro, *, name=None, context=None):
        task = asyncio.create_task(coro, name=name, context=context)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def cancel_all(self):
        for task in self._tasks:
            task.cancel()
