# python-event-system
a featured event system for python

once this package it released youll be able to get it with:
this currently doesnt work because i have no pypi acc as of yet.
```pip install pyeventsystem```

this library uses a setup i came up with on a whim while stoned.
we start by building a tasklist
```
printtask = maketask(print, ['hello', 'this is the event system', 'it works well'], 4, {'sep': '\n'}, [], 1 )

    tasks = tasklist([printtask])
```
for now we can work with just this. 

next we instantiate the loop:
```
loop = eventloop(tasks, True)
```

now we either add to the loop or we start it, this tim,e we will start it:
```
loop.startloop()
```

but if we leave it like that it will be an infinite loop... so lets end it after its done with that task:
```
tasks.addtask(maketask(loop.stoploop, priority=99))
```

