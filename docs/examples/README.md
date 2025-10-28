# Examples

Collection of sample programs and expected outputs for quick testing.

## Arithmetic with mixed types

Source:
```
y := x*2.0 + z*3.0*r;
write y;
```

Notes:
- `2.0` and `3.0` are floats; expressions with `x`, `z`, `r` may promote to float.

## Conditionals and loops

Source:
```
read x;
if x < 10 then
  write x;
else
  repeat
    x := x - 1;
  until x = 10;
  write x;
end;
```
