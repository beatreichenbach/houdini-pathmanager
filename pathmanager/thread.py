from __future__ import annotations

import enum
import logging
from typing import Callable

from qtpy import QtCore

logger = logging.getLogger(__name__)


class WorkerTask(QtCore.QObject):
    queued = QtCore.Signal(object)
    started = QtCore.Signal()
    finished = QtCore.Signal()
    succeeded = QtCore.Signal(object)
    progress = QtCore.Signal(float)

    class State(enum.Enum):
        NEW = 'New'
        IN_PROGRESS = 'In Progress'
        SUCCEEDED = 'Succeeded'
        CANCELLED = 'Cancelled'
        FAILED = 'Failed'

    def __init__(self, func: Callable, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        self.func = func
        self.state = WorkerTask.State.NEW
        self.running = False
        self.args = ()
        self.kwargs = {}

    def queue(self) -> None:
        self.queued.emit(self)

    def start(self) -> None:
        self.state = WorkerTask.State.IN_PROGRESS
        self.started.emit()

    def run(self) -> None:
        self.running = True
        result = self.func(*self.args, **self.kwargs)
        self.state = WorkerTask.State.SUCCEEDED
        self.succeeded.emit(result)

    def fail(self) -> None:
        self.state = WorkerTask.State.FAILED

    def cancel(self) -> None:
        self.state = WorkerTask.State.CANCELLED

    def finish(self) -> None:
        self.running = False
        self.finished.emit()
        # Ensure all finished are processed before cleaning up
        QtCore.QTimer.singleShot(0, self.cleanup)

    def cleanup(self) -> None:
        self.setParent(None)


class Worker(QtCore.QObject):
    def run(self, task: WorkerTask) -> None:
        if self.thread().isInterruptionRequested():
            task.cancel()
            return
        task.start()
        try:
            task.run()
        except Exception as e:
            logger.exception(e)
            task.fail()
        finally:
            task.finish()


class ThreadManager(QtCore.QObject):
    _instance: ThreadManager | None = None

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent=parent)
        self.worker_thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.worker_thread)

    @classmethod
    def instance(cls) -> ThreadManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def create_task(cls, func: Callable) -> WorkerTask:
        """
        Create a new WorkerTask from a function.
        The ThreadManager takes ownership of the task and will clean it up when the task
        is finished.
        """

        instance = cls.instance()
        if not instance.worker_thread.isRunning():
            logger.debug(f'Starting the worker thread.')
            instance.worker_thread.start()
        task = WorkerTask(func)
        task.setParent(instance)
        task.queued.connect(instance.worker.run)
        return task

    @classmethod
    def stop(cls) -> None:
        instance = cls.instance()
        if instance.worker_thread.isRunning():
            logger.debug('Stopping the worker thread.')
            instance.worker_thread.quit()
            instance.worker_thread.wait()

    @classmethod
    def terminate(cls) -> None:
        instance = cls.instance()
        if instance.worker_thread.isRunning():
            logger.debug('Terminating the worker thread.')
            instance.worker_thread.terminate()
            instance.worker_thread.wait()
