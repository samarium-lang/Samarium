# File I/O

Files are handled through file I/O objects, which can be in one of several modes: read, write, read & write, append, and as either text or binary for each of these.
File I/O objects have a cursor, which is updated whenever data is written to/read from the object.
The current cursor position can be gotten like so:

```sm
pos: f<<>>;
== assuming `f` is a file I/O object
```

## Creating

Files can be created with the unary `?~>` operator.
`?~> "file.txt"` will create an empty file called `file.txt` in the program directory.

Note: files will also be created if they are opened in write or append mode.

## Reading

Files can be opened for reading in two ways:

```sm
f <~~ "file.txt";
== opens `file.txt` for reading, in text mode,
== and stores the file I/O object in `f`.

f <~% "file.bin:
== opens `file.bin` for reading, in binary mode,
== and stores the file I/O object in `f`.
```

These file I/O objects can be read into a variable (a string for text mode, and an array of integers for binary mode) for use in the program.

```sm
string <~ f;
== reading the full contents of the file I/O object `f`
== into `string` (assuming `f` is in text read mode)

array <~ f;
== reading the full contents of the file I/O object `f`
== into `array` (assuming `f` is in text binary mode)
```

## Writing

Files can be opened for writing in two ways:

```sm
f ~~> "file.txt";
== opens/creates `file.txt` for writing, in text
== mode, and stores the file I/O object in `f`.

f %-> "file.bin";
== opens/creates `file.bin` for writing, in binary
== mode, and stores the file I/O object in `f`.
```

These file I/O objects can be written to from a variable (a string for text mode, and an array of integers for binary mode).

```sm
string ~> f;
== writes the entirety of `string` into the file I/O
== object `f` (assuming `f` is in text write mode)

array %> f;
== writes the entirety of `array` into the file I/O
== object `f` (assuming `f` is in binary write mode)

```

## Appending

Files can be opened for appending in two ways:

```sm
f &~~> "file.txt";
== opens/creates `file.txt` fpr appending, in text
== mode, and stores the file I/O object in `f`.

f &%~> "file.bin";
== opens/creates `file.bin` fpr appending, in binary
== mode, and stores the file I/O object in `f`.

```
The contents of these file I/O objects can be added to from a variable (a string for text mode, and an array of integers for binary mode).

```sm
string &-> f;
== appends the entirety of `string` to the current contents of
== the file I/O object `f` (assuming `f` is in text append mode)

array &%> f;
== appends the entirety of `array` to the current contents of
== the file I/O object `f` (assuming `f` is in binary append mode)
```
## Closing

Files can be closed with the `~` operator.
If files are not closed manually by the user, they will be automatically closed once the program terminates.
Note that the file I/O object will not be released from memory, but it still cannot be used.

```sm
~f;
== closes the file I/O object `f`
```
## Quick Operations

Files can be read from, written to or appended to directly using the filename, with quick operations.
These will open the file in the relevant mode, perform the operation, and close it, all in one.

Mode          | Operator
---           | ---
Text read     | `<~`
Text write    | `~>`
Text append   | `&~>`
Binary read   | `<%`
Binary write  | `%>`
Binary append | `&%>`

For example:

```sm
string ~> "file.txt";
== writes the entirety of `string` directly into `file.txt`

array <% "file.bin";
== reads the full contents of `file.bin` directly into `array`
```