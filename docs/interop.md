# Python Interoperability

Samarium 0.4.0 introduced partial Python Interoperability, allowing you to use
Python functions inside Samarium.

The Python file you want to use has to be in the same directory as your Samarium
file (so standard importing rules apply).

Making a Python function usable in Samarium is as easy as decorating it with
`@export`—it's gonna do all conversions between supported Samarium and Python
types automatically.

Python files are imported the same way as Samarium files.

Samarium files take priority over Python files, meaning that if you have both
`file.py` and `file.sm` in the same folder, Samarium will import `file.sm`.

## Examples

### Example 1
```py
# foo.py
from samarium import run, Registry
from samarium.python import export


@export
def exec(code: str) -> None:
    run(code, Registry({}), __file__)
```
```sm
<-foo.exec("/////??!;");  == 14
```

### Example 2
```py
# bar.py
import json

from samarium.python import export


@export
def read_json(source: str) -> None:
    return json.loads(source)
```
```sm
source <~ "sample.json";
<-bar.read_json(source)!;
== {{"hello" -> "world", "pi" -> 3.14}}
```

## Supported Conversions

### Samarium → Python
Samarium Type | Python Type
---           | ---
Array         | list
Enum          | Enum
File          | IOBase
Number        | float
Iterator      | Iterator
Null          | NoneType
Slice         | SliceRange[^1]
String        | str
Table         | dict
Zip           | zip

[^1]: 

### Python → Samarium
Python Type    | Samarium Type
---            | ---
int            | Number
bool           | Number
float          | Number
str            | String
NoneType       | Null
list           | Array
tuple          | Array
set            | Array
dict           | Table
range          | Slice
slice          | Slice
SliceRange[^1] | Slice
IOBase         | File
zip            | Zip
type[Enum]     | Enum
Iterator       | Iterator

Additionally, Enum members only get their values converted.

[^1]: Samarium Slices can act as both Python `range`s and `slice`s, therefore a
`SliceRange` object is being returned. It only has 2 properties, `range` and
`slice`, which return exactly those objects.