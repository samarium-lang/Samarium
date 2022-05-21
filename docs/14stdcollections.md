# `collections` module

The `collections` module implements a few different data structure classes: [Stack](#stack), [Queue](#queue), [Set](#set), [Deque](#deque) and [StaticArray](#staticarray).

## Stack

A stack is a collection of items that the user may "push" a new item on top of, or "pop" the most recently added/top item from, following a last in first out order (LIFO).

Method            | Use
---               | ---
`create([size])`  | Initializes an empty Stack object with capacity `size`. If `size` is unspecified it will default to `-1`, giving the stack unbounded capacity.
`push(item)`      | Pushes `item` on top of the stack. If the stack is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`pushAll(items)`  | Pushes each element of `items` on top of the stack, one at a time.
`pop()`           | Pops/removes an item from the top of the stack, and returns it. If the stack is empty, this will instead throw an error.
`peek()`          | Returns the value of the item on top of the stack without popping it. If the stack is empty, this will instead throw an error.
`isFull()`        | Returns `1` if the number of items in the stack is equal to the specified capacity, otherwise returns `0`.[<sup>a</sup>](#note-a)
`isEmpty()`       | Returns `1` if the number of items in the stack is equal to 0, otherwise returns `0`.
`special()`       | Returns the number of items in the stack.
`toBit()`         | Returns `1` if the stack is not empty, otherwise returns `0`.[<sup>b</sup>](#note-b)
`toString()`      | Returns some information about the stack as a string; its capacity, number of items, and the value of the top item.

## Queue

A queue is a collection of items that the user may "put" ("enqueue") an item at the back of, or "get" ("dequeue") an item from the front of, following a first in first out order (FIFO).

Method           | Use
---              | ---
`create([size])` | Initializes an empty Queue object with capacity `size`. If `size` is unspecified it will default to `-1`, giving the queue unbounded capacity.
`put(item)`      | Puts `item` at the back of the queue. If the queue is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`putAll(items)`  | Puts each element of `items` at the back of the queue, one at a time.
`get()`          | Gets/removes an item from the front of the queue, and returns it. If the queue is empty, this will instead throw an error.
`first()`        | Returns the value of the item at the front of the queue, without removing it. If the queue is empty, this will instead throw an error.
`last()`         | Returns the value of the item at the back of the queue, without removing it. If the queue is empty, this will instead throw an error.
`isFull()`       | Returns `1` if the number of items in the queue is equal to the specified capacity, otherwise returns `0`.[<sup>a</sup>](#note-a)
`isEmpty()`      | Returns `1` if the number of items in the queue is equal to 0, otherwise returns `0`.
`special()`      | Returns the number of items in the queue.
`toBit()`        | Returns `1` if the queue is not empty, otherwise returns `0`.[<sup>b</sup>](#note-b)
`toString()`     | Returns some information about the queue as a string; its capacity, number of items, and the values of its items. Note that if there are more than 5 items in the queue, the string will be truncated.

## Deque

A deque is a data structure similar to a queue, but where insertion and removal of elements can be performed from both the front and the back.

Method               | Use
---                  | ---
`create([size])`     | Initializes an empty Deque object with capacity `size`. If `size` is unspecified it will default to `-1`, giving the deque unbounded capacity.
`putFront(item)`     | Puts `item` at the front of the deque. If the deque is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`put(item)`          | Puts `item` at the back of the deque. If the deque is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`putFrontAll(items)` | Puts each element of `items` at the front of the deque, one at a time.
`putAll(items)`      | Puts each element of `items` at the back of the deque, one at a time.
`getFront()`         | Gets/removes an item from the front of the deque, and returns it. If the deque is empty, this will instead throw an error.
`get()`              | Gets/removes an item from the back of the deque, and returns it. If the deque is empty, this will instead throw an error.
`front()`            | Returns the value of the item at the front of the deque, without removing it. If the deque is empty, this will instead throw an error.
`back()`             | Returns the value of the item at the back of the deque, without removing it. If the deque is empty, this will instead throw an error.
`isFull()`           | Returns `1` if the number of items in the deque is equal to the specified capacity, otherwise returns `0`.[<sup>a</sup>](#note-a)
`isEmpty()`          | Returns `1` if the number of items in the deque is equal to 0, otherwise returns `0`.
`special()`          | Returns the number of items in the deque.
`toBit()`            | Returns `1` if the deque is not empty, otherwise returns `0`.[<sup>b</sup>](#note-b)
`toString()`         | Returns some information about the deque as a string; its capacity, number of items, and the values of its items. Note that if there are more than 5 items in the deque, the string will be truncated.

## Set

A set is an unordered collection of items, with no duplicates.

Method                        | Use
---                           | ---
`create([items[, capacity]])` | Initializes a `Set` object, with its contents being `items` with any duplicate elements removed, and its capacity being `capacity`. If `items` is unspecified it will default to an empty array. If `capacity` is unspecified it will default to `-1`, giving the set unbounded capacity.
`add(value)`                  | Adds `value` to the set, provided it doesn't already exist in the set, and returns a status code (`0` or `1`) based on whether it was added. If `value` isn't already in the set, and the set is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`remove(value)`               | Removes `value` from the set, provided it exists in the set.
`clear()`                     | Removes every element from the set.
`union(other)`                | Returns the union of the current set and `other`, i.e. the two sets' items added together with duplicates again removed.
`intersection(other)`         | Returns the intersection of the current set and `other`, i.e. a new set containing all items that the two sets share.
`difference(other)`           | Returns the difference of the current set and `other`, i.e. a new set containing all items that the current set contains but `other` does not.
`values()`                    | Returns the contents of the set as an array.
`has(value)`                  | Returns `1` if `value` is contained in the set, otherwise returns `0`.
`isFull()`                    | Returns `1` if the number of items in the set is equal to the specified capacity, otherwise returns `0`.[<sup>a</sup>](#note-a)
`isEmpty()`                   | Returns `1` if the number of items in the set is equal to 0, otherwise returns `0`.
`isSubset(other)`             | Returns `1` if the current set is a subset of `other`, i.e. every element of the current set is contained in `other`.
`special()`                   | Returns the number of items in the set.
`toBit()`                     | Returns `1` if the deque is not empty, otherwise returns `0`.[<sup>b</sup>](#note-b)
`toString()`                  | Returns some information about the set as a string; its capacity, number of items, and the values of its items.

## StaticArray

A static array is like a normal array, but with a fixed size. They may also enforce all elements to be of a certain type.

Method                   | Use
---                      | ---
`create(value[, type])`  | Initializes a `StaticArray` object. If `type` is specified, it defines the enforced type of the static array. If `value` is an integer, it defines the size of the static array. If `value` is an array, its size defines the size of the static array, and its elements are copied into the static array. If `type` is not specified, the static array will not enforce elements to be of any particular type.
`getItem(index)`         | Returns the `index`th item in the static array. If `index` is outside the bounds of the static array, an error is thrown.
`setItem(index, value)`  | Sets the `index`th item in the static array to `value`. If `index` is outside the bounds of the static array, or `value` is not of the correct type for the array, provided it enforces a particular type, an error is thrown.
`special()`              | Returns an array containing all items in the static array, with any unassigned indices ignored.
`toBit()`                | Returns `1` if the static array is not empty, otherwise returns `0`.
`toString()`             | Returns some information about the static array as a string; its size, its type ("null" if it doesn't enforce one), and a table mapping each item's index to its value.


<sup id="note-a">a</sup> Note that this will always return `0` if the specified capacity is negative, or if the user does not provide a capacity.

<sup id="note-b">b</sup> `toBit()` is functionally the opposite of `isEmpty()`.