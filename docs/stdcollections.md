# `collections` module

The `collections` module implements a few different data structure classes: [Stack](#stack), [Queue](#queue), [Set](#set), [Deque](#deque) and [StaticArray](#staticarray).

## Stack

A stack is a collection of items that the user may "push" a new item on top of, or "pop" the most recently added/top item from, following a last in first out order (LIFO).

Method            | Use
---               | ---
`create([size])`  | Initializes an empty Stack object with capacity `size`.<br>If `size` is unspecified it will default to `-1`, giving the stack unbounded capacity.
`is_empty()`      | Returns `1` if the number of items in the stack is equal to 0, otherwise returns `0`.
`is_full()`       | Returns `1` if the number of items in the stack is equal to the specified capacity, otherwise returns `0`.[^1]
`peek()`          | Returns the value of the item on top of the stack without popping it.<br>If the stack is empty, this will instead throw an error.
`pop()`           | Pops/removes an item from the top of the stack, and returns it.<br>If the stack is empty, this will instead throw an error.
`push(item)`      | Pushes `item` on top of the stack. If the stack is full,<br>i.e. its size is equal to the specified capacity, this will instead throw an error.
`push_all(items)` | Pushes each element of `items` on top of the stack, one at a time.
`special()`       | Returns the number of items in the stack.
`to_bit()`        | Returns `1` if the stack is not empty, otherwise returns `0`.[^2]
`to_string()`     | Returns some information about the stack as a string;<br>its capacity, number of items, and the value of the top item.

## Queue

A queue is a collection of items that the user may "put" ("enqueue") an item at the back of, or "get" ("dequeue") an item from the front of, following a first in first out order (FIFO).

Method           | Use
---              | ---
`create([size])` | Initializes an empty Queue object with capacity `size`.<br>If `size` is unspecified it will default to `-1`, giving the queue unbounded capacity.
`first()`        | Returns the value of the item at the front of the queue, without removing it.<br>If the queue is empty, this will instead throw an error.
`get()`          | Gets/removes an item from the front of the queue, and returns it.<br>If the queue is empty, this will instead throw an error.
`is_empty()`     | Returns `1` if the number of items in the queue is equal to 0, otherwise returns `0`.
`is_full()`      | Returns `1` if the number of items in the queue is equal to the specified capacity, otherwise returns `0`.[^1]
`last()`         | Returns the value of the item at the back of the queue, without removing it.<br>If the queue is empty, this will instead throw an error.
`put(item)`      | Puts `item` at the back of the queue. If the queue is full,<br>i.e. its size is equal to the specified capacity, this will instead throw an error.
`put_all(items)` | Puts each element of `items` at the back of the queue, one at a time.
`special()`      | Returns the number of items in the queue.
`to_bit()`       | Returns `1` if the queue is not empty, otherwise returns `0`.[^2]
`to_string()`    | Returns some information about the queue as a string;<br>its capacity, number of items, and the values of its items.<br>Note that if there are more than 5 items in the queue, the string will be truncated.

## Deque

A deque is a data structure similar to a queue, but where insertion and removal of elements can be performed from both the front and the back.

Method                 | Use
---                    | ---
`back()`               | Returns the value of the item at the back of the deque, without removing it.<br>If the deque is empty, this will instead throw an error.
`create([size])`       | Initializes an empty Deque object with capacity `size`.<br>If `size` is unspecified it will default to `-1`, giving the deque unbounded capacity.
`front()`              | Returns the value of the item at the front of the deque, without removing it.<br>If the deque is empty, this will instead throw an error.
`get()`                | Gets/removes an item from the back of the deque, and returns it.<br>If the deque is empty, this will instead throw an error.
`get_front()`          | Gets/removes an item from the front of the deque, and returns it.<br>If the deque is empty, this will instead throw an error.
`is_empty()`           | Returns `1` if the number of items in the deque is equal to 0, otherwise returns `0`.
`is_full()`            | Returns `1` if the number of items in the deque is equal to the specified capacity, otherwise returns `0`.[^1]
`put(item)`            | Puts `item` at the back of the deque. If the deque is full,<br>i.e. its size is equal to the specified capacity, this will instead throw an error.
`put_all(items)`       | Puts each element of `items` at the back of the deque, one at a time.
`put_front(item)`      | Puts `item` at the front of the deque. If the deque is full,<br>i.e. its size is equal to the specified capacity, this will instead throw an error.
`put_front_all(items)` | Puts each element of `items` at the front of the deque, one at a time.
`special()`            | Returns the number of items in the deque.
`to_bit()`             | Returns `1` if the deque is not empty, otherwise returns `0`.[^2]
`to_string()`          | Returns some information about the deque as a string; its capacity, number of items, and the values of its items.<br>Note that if there are more than 5 items in the deque, the string will be truncated.

## Set

A set is an unordered collection of items, with no duplicates.

Method                        | Use
---                           | ---
`add(value)`                  | Adds `value` to the set, provided it doesn't already exist in the set, and returns a status code (`0` or `1`) based on whether it was added.<br>If `value` isn't already in the set, and the set is full, i.e. its size is equal to the specified capacity, this will instead throw an error.
`clear()`                     | Removes every element from the set.
`create([items[, capacity]])` | Initializes a `Set` object, with its contents being `items` with any duplicate elements removed, and its capacity being `capacity`.<br>If `items` is unspecified it will default to an empty array.<br>If `capacity` is unspecified it will default to `-1`, giving the set unbounded capacity.
`difference(other)`           | Returns the difference of the current set and `other`,<br>i.e. a new set containing all items that the current set contains but `other` does not.
`has(value)`                  | Returns `1` if `value` is contained in the set, otherwise returns `0`.
`intersection(other)`         | Returns the intersection of the current set and `other`,<br>i.e. a new set containing all items that the two sets share.
`is_empty()`                  | Returns `1` if the number of items in the set is equal to 0, otherwise returns `0`.
`is_full()`                   | Returns `1` if the number of items in the set is equal to the specified capacity, otherwise returns `0`.[^1]
`is_subset(other)`            | Returns `1` if the current set is a subset of `other`,<br>i.e. every element of the current set is contained in `other`.
`remove(value)`               | Removes `value` from the set, provided it exists in the set.
`special()`                   | Returns the number of items in the set.
`to_bit()`                    | Returns `1` if the deque is not empty, otherwise returns `0`.[^2]
`to_string()`                 | Returns some information about the set as a string; its capacity, number of items, and the values of its items.
`union(other)`                | Returns the union of the current set and `other`,<br>i.e. the two sets' items added together with duplicates again removed.
`values()`                    | Returns the contents of the set as an array.

## StaticArray

A static array is like a normal array, but with a fixed size. They may also enforce all elements to be of a certain type.

Method                   | Use
---                      | ---
`create(value[, type])`  | Initializes a `StaticArray` object. If `type` is specified, it defines the enforced type of the static array.<br>If `value` is an integer, it defines the size of the static array.<br>If `value` is an array, its size defines the size of the static array, and its elements are copied into the static array.<br>If `type` is not specified, the static array will not enforce elements to be of any particular type.
`get_item(index)`        | Returns the `index`th item in the static array.<br>If `index` is outside the bounds of the static array, an error is thrown.
`set_item(index, value)` | Sets the `index`th item in the static array to `value`.<br>If `index` is outside the bounds of the static array, or `value` is not of the correct type for the array,<br>provided it enforces a particular type, an error is thrown.
`special()`              | Returns an array containing all items in the static array, with any unassigned indices ignored.
`to_bit()`               | Returns `1` if the static array is not empty, otherwise returns `0`.
`to_string()`            | Returns some information about the static array as a string;<br>its size, its type ("null" if it doesn't enforce one), and a table mapping each item's index to its value.

## ArithmeticArray

An arithmetic array is an array which can be used with different binary operators.

```sm
<-collections.ArithmeticArray;

aa: ArithmeticArray([/\, //, /\/]);

aa!;  == [2, 3, 5]
aa + /\!;  == [4, 5, 7]
aa ++ ///!;  == [14, 21, 35]

is_odd: aa --- /\;
is_odd!;  == [0, 1, 1]

aa: ArithmeticArray(["oh", "hey", "hello"]);
aa + "!"!;  == ["oh!", "hey!", "hello!"]
```

Binary operators supported by ArithmeticArray:
- arithmetic: `+`, `++`, `+++`, `-`, `--`, `---`
- bitwise: `&`, `|`, `^`
- comparison: `::`, `>:`, `>`, `<:`, `<`, `:::`

ArithmeticArray allows item assignment and inherits behavior for `$`, `to_sit`, and `to_string` from the `Array` class.

You can also use your own custom operators in the form of functions by using the `apply(op, other)` method:

```sm
<-collections.ArithmeticArray;
<-math.shl;

aa: ArithmeticArray([///, /\//, //\/]);
aa!;
aa.apply(shl, /\)!;


remove_null nullable default * {
    * default ? nullable :: _ ,, nullable;
}

aa: ArithmeticArray([_, /\, //, _, /\/, _, ///]);
aa!;  == [null, 2, 3, null, 5, null, 7]
aa.apply(remove_null, \)!;  == [0, 2, 3, 0, 5, 0, 7]
```


[^1]: Note that this will always return `0` if the specified capacity is negative, or if the user does not provide a capacity.

[^2]: `to_bit()` is functionally the opposite of `is_empty()`.
