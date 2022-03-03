[Back to Table of Contents](../README.md#table-of-contents)

# File I/O

Files are handled through file I/O objects, which can be in one of several modes: read, write, read & write, append, and as either text or binary for each of these.
File I/O objects have a cursor, which is updated whenever data is written to/read from the object.
The current cursor position can be gotten like so:

<p align="left">
    <img src="images/36fileio.png" style="transform: scale(0.6)">
</p>

## Creating

Files can be created with the unary `?~>` operator.
`?~> "file.txt"` will create an empty file called `file.txt` in the program directory.

Note: files will also be created if they are opened in write or append mode.

## Reading

Files can be opened for reading in two ways:

<p align="left">
    <img src="images/37fileio.png" style="transform: scale(0.6)">
</p>

These file I/O objects can be read into a variable (a string for text mode, and an array of integers for binary mode) for use in the program.

<p align="left">
    <img src="images/38fileio.png" style="transform: scale(0.6)">
</p>

## Writing

Files can be opened for writing in two ways:

<p align="left">
    <img src="images/39fileio.png" style="transform: scale(0.6)">
</p>

These file I/O objects can be written to from a variable (a string for text mode, and an array of integers for binary mode).

<p align="left">
    <img src="images/40fileio.png" style="transform: scale(0.6)">
</p>

## Appending

Files can be opened for appending in two ways:

<p align="left">
    <img src="images/41fileio.png" style="transform: scale(0.6)">
</p>

The contents of these file I/O objects can be added to from a variable (a string for text mode, and an array of integers for binary mode).

<p align="left">
    <img src="images/42fileio.png" style="transform: scale(0.6)">
</p>

## Closing

Files can be closed with the `~` operator.
If files are not closed manually by the user, they will be automatically closed once the program terminates.
Note that the file I/O object will not be released from memory, but it still cannot be used.

<p align="left">
    <img src="images/43fileio.png" style="transform: scale(0.6)">
</p>

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

<p align="left">
    <img src="images/44fileio.png" style="transform: scale(0.6)">
</p>
