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

If you run the `samarium` command without any arguments,
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


## `color [color|save]`
Changes the prompt color. The available colors are [Dahlia codes] from `0` to
`e`, as well as their English names. Providing no argument will reset the
color. `:color save` will save the current color to the REPL config, making the
change permanent.

The English names can be checked by using the `:? color` command:
```
--> :? color
color [color]
providing no color will reset it to the default one

use :color save to save the current color to your config

0|black
1|blue
2|green
3|cyan
4|red
5|purple
6|orange
7|light gray
8|gray
9|light blue
a|lime
b|aquamarine
c|light red
d|pink
e|yellow
```


## `debug`
Toggles debug mode which shows the intermediary Python code that the Samarium
input is transpiled to before executing it (equivalent to using the
`samarium-debug` command).
```
--> /
1
--> :debug
--> /
Num(1)
1
```


## `exit`
> Aliases: `q`, `quit`

Exits the REPL and saves the session if [autosave](#autosave-truefalse) is
enabled. Appending a `!` or just using it as a command will "force quit" the
REPL without saving the session.
```
$ ls -1 ~/.cache/samarium | wc -l
       7
$ samarium
Samarium 0.6.0
--> :session autosave
Autosave is enabled
--> :!
$ ls -1 ~/.cache/samarium | wc -l
       7
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
t|time                  times the execution of the following statement
undo                    undoes the last statement
```


## `time <code>`
> Aliases: `t`

Runs a given piece of code and shows how much time it took to execute.
```
--> :t <-math.is_prime(/?!("2137"))
1
0.009 seconds
```


## `undo`
Undoes the last statement.
```
--> x: /\/\!
10
--> x+++:
--> x
100
--> :undo
--> x
10
```
This is done by rerunning all inputs except for the last one (simple value
lookups like `x` on lines 4 and 7 are excluded) and silencing all writes to
stdout/stderr.


## Sessions

Sessions provide a convenient way to save and restore your REPL state, allowing
you to pick up right where you left off.


## `autosave [true|false]`
Specifies whether sessions should be automatically saved on exit. Providing no
argument will display the current value.
```
--> :session autosave false
Autosave disabled
--> :session autosave
Autosave disabled
```


## `delete-all`
Deletes all saved sessions (both named and unnamed).
```
--> :session delete-all
Are you sure you want to delete all 27 sessions? (Y/n) 
Removed 1.7KB of session files
```


## `lifetime [time]`
Specifies the lifetime (in days) for unnamed sessions. Sessions that are too old
get removed on the next launch of the REPL. Providing no argument will display
the current value.
```
--> :session lifetime
Current session lifetime is 30 days
--> :session lifetime 20
Updated session lifetime to 20 days
```


## `list`
Displays a list of saved sessions and their sizes.
```
--> :session list
20230702193813.json                            (57.0B)
20230702163714.json                            (57.0B)
20230702194010.json                            (57.0B)
20230702163535.json                            (64.0B)
20230702193747.json                            (57.0B)
20230702210821.json                            (51.0B)
20230702170234.json                            (57.0B)
prime-sieve.json                               (2.7KB)
20230702171025.json                            (57.0B)
20230702193958.json                            (57.0B)
20230702171009.json                            (57.0B)
20230702193902.json                            (57.0B)
20230702192942.json                            (57.0B)
----------------------------------------------
Total                                           3.3KB
```


## `load <name>`
Loads a given session.
```
--> :session load sorting
--> quick_sort([/////?? ... _ ->? <<../\/\\>>])
[1, 2, 2, 3, 3, 4, 5, 11, 13, 14, 17, 18, 20, 20, 21, 21, 23, 24, 26, 29]
```


## `restore`
Loads the most recent unnamed session.
```
--> :session autosave
Autosave enabled
--> f * { ("!"++(///+++))! }
--> :q
$ samarium
Samarium 0.6.0
--> :session restore
--> f()
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```


## `save [name]`
Saves a sesssion under a given name. Becomes an unnamed session if no name is
supplied. Session names can consist of English letters, digits, hyphens, and
underscores.
```
--> pi * { * <-math.TAU--; }
--> :session save pi
--> :q
$ samarium
Samarium 0.6.0
--> :session load pi
--> pi()
3.141592653589793
```


[Dahlia codes]: https://github.com/dahlia-lib/spec/blob/main/SPECIFICATION.md#standard-formatting