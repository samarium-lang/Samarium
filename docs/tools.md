# Shebang

You can easily use your Samarium scripts on Unix by putting an appropriate
shebang line at the top of your program, for instance
```sm
#!/usr/bin/env samarium

"Hi!"!;
```
and making it executable, e.g. with
```bash
$ chmod +x script
```


# Samarium REPL

If you run the `samarium` command without any other arguments,
you'll launch the REPL, an interactive shell that will read
and evaluate any Samarium code you enter.
```txt
$ samarium
Samarium 0.6.0
--> 
```
Interacting with the REPL is a nice way to experiment with Samarium:
```txt
--> / + /\
3
--> 1: "ball"##!
1083481267058749873
--> 1??
443527852557841359
--> 1??
894622914084910886
```
The REPL also supports compound statements:
```txt
--> x: /\/\??
--> ? x --- /\ :: \ {
  >     x -- /\!;
  > } ,, {
  >     3 ++ x + /!;
  > }
4
--> x
8
```

## Commands

Samarium 0.6.0 introduced commands to improve your REPL experience.
Commands are prefixed with a colon, use `:?` to see the list of all commands.


## `clear`
Clears the screen.


## `debug`
Toggles debug mode which shows the intermediary Python code that the Samarium
input is transpiled to before executing it (equivalent to using the `samarium-debug`
command).
```
--> /
1
--> :debug
--> /
Num(1)
1
```


## `help [section]`
> Aliases: `?`, `h`
Shows the help message.
```
--> :help
?|h|help                shows this message
exit|q|quit             saves the session and quits the repl
!|exit!|q!|quit!        force quits the repl
session                 manages sessions, see :? session for details
clear                   clears the screen
color                   changes the prompt color, see :? color for details
debug                   toggles debug mode
restore                 restores the previous session
time|t                  times the execution of the following statement
undo                    undoes the last statement (reruns the entire session without it)
```

