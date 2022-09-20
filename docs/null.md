# Null

The null value in Samarium is not represented by any symbol—in fact, it's represented by the lack of it:
```sm
x: /;
y:;
z: [-/, , /];
```
The above code sets `x` to `1`, `y` to `null`, and `z` to `[-1, null, 1]`.

The following code prints `1` if `y` is equal to `null` and `null` is present in `z`, and `0` otherwise.
```sm
y :: && ->? z!;
```
One could alias null for clarity:
```sm
null:;
y :: null && null ->? z!;
```

The null value is not inserted implicitly for method calls, therefore:
```sm
V: .to_bit();
```
has to be written as
```sm
null:;
V: null.to_bit();
```
or – without introducing any variables – as
```sm
V: [,]<<\>>.to_bit();
```
