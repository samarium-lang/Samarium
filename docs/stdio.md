# `io` module

The `io` module contains a few utilities for working with I/O.

### `io.Bytes`
Allows for easier working with files in binary mode:
```sm
<=io.Bytes;

=> * {
    b: Bytes("ball");
    b!;  == 62 61 6c 6c
    b+: "!";  == supports Strings, Integers, Arrays of Integers, and other Bytes objects
    b.export_string()!;  == ball!
    b.export()!;  == [98, 97, 108, 108, 33]
}
```

### `io.inputcast([prompt])`
Works just like `???`, but tries converting the input to a specific type.

Example (showing all available conversions):
```sm
<=io.inputcast;

=> * {
    .. {
        value: inputcast(">> ");
        "Type:", value?!!;
        "Value:", value!;
    }
}
```
```
>> hello
Type: String
Value: hello
>> hello there
Type: Array
Value: ["hello", "there"]
>> 1
Type: Integer
Value: 1
>> 1 2
Type: Array
Value: [1, 2]
>> 1, 2
Type: Array
Value: [1, 2]
>> 
Type: Null
Value: null
>> a=1, b=2
Type: Table
Value: {{"a" -> 1, "b" -> 2}}
>> 3..7
Type: Slice
Value: <<3..7>>
```

### `io.read_until([target])`
Keeps reading lines until the `target` (`""` by default) is entered.
The `target` is included in the output string.

Example:
```sm
=> * {
    "Enter your program:"!;
    program: <-io.read_until("}");
    name: "Enter file name: "???;
    program ~> name;
    "Your program was saved to " + name!;
}
```
```
Enter your program:
=> * {
    "Hello, World!"!;
}
Enter file name: ball.txt
Your program was saved to ball.txt
```