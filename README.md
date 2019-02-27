# g-code_conversion

## How to use it

Launch the script with

```
python C2Gonversion.py
```

## init files

The script uses two init files, one for the script itself and another one required by the G-code file. The first contains information on the input/output files and the spacing used in the function interpolation. The second contains all the variables that will be printed in the script output. The standard names are 'init' and 'gcode_init'. They can be manually set with optional arguments:

```
-i         Selects the script init file
-g         Selects the G-code init file
```

## Input
Can be manually set in the 'init' file.

## Output
By default the output is set to 'out.txt' file, but can be manually set in the 'init' file.

## Graphics
A graphical output is available, via matplotlib. To activate it, launch the script with the arguments

```
-graphic
```
