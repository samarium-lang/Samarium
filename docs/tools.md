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
Samarium 0.5.2
--> 
```
Interacting with the REPL is a nice way to experiment with Samarium:
```txt
--> / + /\!
3
--> 1: "ball"##!
1083481267058749873
--> 1??!
443527852557841359
--> 1??!
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
--> x!
8
```
