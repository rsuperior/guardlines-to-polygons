# Guardlines to polygons JSON converter tool.

Requires Python 3.

Try

```
python guardlines-def-to-json.py -h
```

for usage information.

This tool could be used by technically inclined players to make their own
zone files for their own use on the ClassicUO World Map, but it is really
intended for the maintainers of shard-specific launcher bundles, who might
make a file or two for guard zones on their shard and then be done with it.

## Input file format

The input format comes from a file used by Razor Community Edition to draw
guard lines in the UOPS map.  It's named `guardlines.def`.

This file is essentially a list of rectangles, with comments and grouping.

The comments are simply lines that start with `#`.  Any grouping semantics
probably weren't originally intended, but I interpret comments as labels for
the sequence of rectangles that follows.

The rectangles are lines with 6 integers separated by spaces.  In order,
these represent {X, Y, Width, Height, MinZ, MaxZ}.  I discard the last two
integers when I process this file.

Rectangles within a group are often adjacent to one another, but not always.
More on that when I discuss output later on.

Empty lines are ignored but are nice for separating groups if you're manually
writing a new input file.

Example of input format (example filename guardlines.def):

```
# Name of city or guarded area
1000 1200 100 50 0 127
1100 1100 50 200 0 127
1150 1200 100 40 0 127
950 100 30 36 0 127

# Name of another city
1500 2100 120 98 -20 60
1620 2100 120 150 -20 60
```

## Output file format

The tool converts the input format into a JSON-based output format.

But first, for all rectangles within a group in the input file, the tool
finds mutually adjacent rectangles and merges them into a single polygon.
The reason for this is to allow ClassicUO to draw fewer lines to represent
complex guard zones, and particularly to avoid drawing lines that traverse
the middle of guarded areas. Such lines are inconsequential to players and
clutter the map display..

Example of output format (example filename: GuardZones.zones.json):
```
{
  "mapIndex": 0,
  "zones": [
    {
      "color": "yellow",
      "label": "Name of city or guarded area",
      "polygon": [
        [ 950, 100 ],
        [ 980, 100 ],
        [ 980, 136 ],
        [ 950, 136 ]
      ]
    },
    {
      "color": "yellow",
      "label": "Name of city or guarded area",
      "polygon": [
        [ 1150, 1300 ],
        [ 1150, 1240 ],
        [ 1250, 1240 ],
        [ 1250, 1200 ],
        [ 1150, 1200 ],
        [ 1150, 1100 ],
        [ 1100, 1100 ],
        [ 1100, 1200 ],
        [ 1000, 1200 ],
        [ 1000, 1250 ],
        [ 1100, 1250 ],
        [ 1100, 1300 ]
      ]
    },
    {
      "color": "yellow",
      "label": "Name of another city",
      "polygon": [
        [ 1740, 2250 ],
        [ 1740, 2100 ],
        [ 1500, 2100 ],
        [ 1500, 2198 ],
        [ 1620, 2198 ],
        [ 1620, 2250 ]
      ]
    }
  ]
}
```

Note that the whitespace actually produced by the tool may look different
than the example above, which I have adjusted for readability.

You can see also how shapes are represented differently here than in the
input.  Each shape is a polygon defined by a sequence of {X, Y} points.
ClassicUO will connect each of these in sequence by drawing lines, finally
drawing a line from the last point back to the first.

The output files are meant to be stored in the Client\Data subdirectory
(the same place where CSV files for World Map markers go).
