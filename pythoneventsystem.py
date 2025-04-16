
from typing import (Callable, Optional, Any, Set)
from dataclasses import dataclass
import asyncio
import timeloop

class tasknotfounderror(Exception):
    def __init__(self, _input: Optional, expected: Optional, errorstring: Optional[str]):
        super().__init__(input, expected, errorstring)
        if errorstring:
            print(errorstring)
        else:
            print(f'taskerror: {_input} was an error')
def maketask(func: Callable = print,
             args: Optional[list] = None,
             parametercount: int = 0,
             kwargs: dict[str, Any] = None,
             kwargslist:list[str] = None,
             priority: int = 1,
             dependencies: Set[str] = {''},
             completed: bool = False,
             retries: int = 0,
             max_retries: int = 1,
             timeout: Optional[float] = None,
             expedited: bool = False,
             asyncronous: bool = False):
   task = Task(func.__name__, func, args, kwargs, kwargslist, priority, dependencies, parametercount, completed, retries, max_retries, timeout, expedited, asyncronous)
   return task
@dataclass
class Task:
    name: str
    func: Callable
    args: list[Any] | None
    kwargs: dict[str, Any] | None
    kwargnamelist: list[str]
    priority: int
    depends_on: Set[str]
    paramcount: int = 0
    completed: bool = False
    retries: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None
    expedited: bool = False
    asyncronous: bool = False
    def __post_init__(self):
        if not callable(self.func):
            raise ValueError(f"{self.func} is not callable")
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("Timeout must be positive")
    def __lt__(self, other):
        if not isinstance(other, Task):
            raise TypeError(f"Cannot compare Task with {type(other).__name__}")
        return self.priority < other.priority
    def __gt__(self, other):
        if not isinstance(other, Task):
            raise TypeError(f"Cannot compare Task with {type(other).__name__}")
        return self.priority > other.priority
    def __eq__(self, other):
        if not isinstance(other, Task):
            raise TypeError(f"Cannot compare Task with {type(other).__name__}")
        return isinstance(other, Task) and self.name == other.name
    def __hash__(self):
        return hash(self.name)


class tasklist:
    tasks: list[Task | None]
    def __init__(self, initialtasks: list[Task]):
        self.tasks = initialtasks
    def __contains__(self, item):
        for i in self.tasks:
            if item in i:
                return True
            else:
                continue
        return False

    def __iter__(self):
        return iter(self.tasks)
    def __getitem__(self, item):
        return self.tasks[item]
    def addtask(self, task: Task):
        for taska in range(len(self.tasks)):
            if self.tasks[taska] < task:
                continue
            elif self.tasks[taska] > task:
                self.tasks.insert(taska-1, task)
                return
            else:
                continue
        self.tasks.append(task)
        return
    def addexpeditedtask(self, task: Task):
        self.tasks.insert(0, task)
        return
    def expeditetaskbyname(self, name: str):
        for i in range(len(self.tasks)):
            if self.tasks[i].name == name:
                currenttask = self.tasks[i]
                if currenttask.paramcount == 0:
                    if len(currenttask.kwargnamelist) == 0:
                        if currenttask.asyncronous:
                            asyncio.run(currenttask.func())
                        else:
                            currenttask.func()
                        return
                    else:
                        if currenttask.asyncronous:
                            asyncio.run(currenttask.func(**currenttask.kwargs))
                        else:
                            currenttask.func(**currenttask.kwargs)

                        return
                else:
                    if len(currenttask.kwargnamelist) == 0:
                        if currenttask.asyncronous:
                            asyncio.run(currenttask.func(*currenttask.args))
                        else:

                            currenttask.func(*currenttask.args)
                        return
                    else:
                        if currenttask.asyncronous:
                            asyncio.run(currenttask.func(*currenttask.args, **currenttask.kwargs))
                        else:
                            currenttask.func(*currenttask.args, **currenttask.kwargs)
                        return

    def poptaskbyindex(self, index: int):
        if index > len(self.tasks):
            raise IndexError
        if index < 0:
            raise IndexError
        if self.tasks[index].completed is True:
            try:
                runnabletask = self.tasks.pop(index)
                return runnabletask.func, runnabletask.args
            except:
                raise tasknotfounderror
    def poptaskbypriority(self, priority: int):
        for i in range(len(self.tasks)):
            if self.tasks[i].priority == priority:
                return self.poptaskbyindex(i)
        raise tasknotfounderror


class eventloop:
    running: bool
    def __init__(self, tasks: tasklist, running: bool = True):
        self.running = running
        self.tasks = tasks
        self.timer = None
    def startloop(self):
        if self.running is not True:
            self.running = True
        while self.running is True:
            current_task = self.tasks[0]
            try:
                if current_task.paramcount > 0:
                    if current_task.kwargs is not None:
                        if current_task.asyncronous:
                            result = asyncio.run(current_task.func())
                        else:
                            result = current_task.func(*current_task.args, **current_task.kwargs)
                    else:
                        result = current_task.func(*current_task.args)
                else:
                    result = current_task.func()
                self.timer = timeloop.TimeoutTimer()
                self.timer.start(current_task.timeout)
                if self.timer.timed_out() != current_task.completed:
                    if (self.timer.timed_out(), current_task.completed) is (True, False):
                        if current_task.max_retries > current_task.retries:
                            current_task.retries = current_task.retries + 1
                            continue
                        else:
                            raise timeloop.timeoutexception

                    elif (self.timer.timed_out(), current_task.completed) is (False, True):
                        return result
                    elif (self.timer.timed_out(), current_task.completed) is (True, True):
                        return result
                    else:
                        continue
                current_task.completed = True
                self.tasks.poptaskbyindex(0)
            except Exception as e:
                if current_task.max_retries > current_task.retries:
                    current_task.retries = current_task.retries + 1
                print(f"Error occurred: {str(e)}")
                raise
    def stoploop(self):
        self.running = False

if __name__ == '__main__':
    printtask = maketask(print, ['hello', 'this is the event system', 'it works well'], 4, {'sep': '\n'}, [], 1 )

    tasks = tasklist([printtask])
    loop = eventloop(tasks, True)

    tasks.addtask(maketask(loop.stoploop, priority=99))
    loop.startloop()























