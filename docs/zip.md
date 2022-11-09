# Zipping

Samarium's zip operator `><` allow for easy zipping, that is, iterating through multiple iterables at once:
```sm
names: ["Alice", "Bob", "Charlie"];
ages: [/\\\\, /\\\/, ////];

... i ->? names >< ages {
    "$0 is $1 years old" --- i!;
}
```
```
Alice is 16 years old
Bob is 17 years old
Charlie is 15 years old
```

Enumerating iterables can be simulated by using an empty slice object:
```sm
x: ["Alpha", "Beta", "Gamma"];

... i, v ->? <<>> >< x {
    "x<<$0>> :: $1" --- [i, v]!;
}
```
```
x<<0>> :: Alpha
x<<1>> :: Beta
x<<2>> :: Gamma
```