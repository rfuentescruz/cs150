# Javascript (yava-script)

## Requirements

Javascript requires `python2.7` and the `ply` library to run. Install `ply` using:

```
pip install ply
```

## Usage

To start a REPL session, run:

```
python lang.py
```

This will enter a REPL session where statements may be entered line by line and they
will be executed immediately:

```
jt  > a = 1
jt  > b = 2
jt  > print a + b
3
```

Statements entered in a REPL session do not need to end in a semicolon (;).

Multi-line statements (`if`, `while`, functions) can be used within a REPL session but
the session do not support nested multi-line statements:

```
jt  > a = 10
jt  > while (a > 0) {
... >   a = a - 1
... >   print a
... > }
9
8
7
6
5
4
3
2
1
0
jt  >
```

Aside from a REPL session, `.jt` files may be executed by passing in the filename as a
command line argument:

```
python lang.py ./sample_programs/heapsort.jt
[9, 10, 2, 1, 5, 4, 3, 6, 8, 7, 13]
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13]
```

