#!/usr/bin/env python3

import sys
from re import compile
from json import dump

from rect import Rect, group_adjacent_rects, \
        adjacent_rects_corners_to_polygons, find_intersections_in_rects

def rects_to_polygons(zonelevel, warn_intersections):
    for k in zonelevel.keys():
        rects = zonelevel[k]

        if warn_intersections:
            intersections = find_intersections_in_rects(rects)

            # I'm not sure intersections are a problem per se, but I think
            # it's a good idea to visually inspect the polygons that
            # come out of this program around any area where there were
            # intersecting rectangles in the input.

            if intersections:
                print("Intersections found in", k, "!", intersections,
                        file=sys.stderr)

        polygons = []

        for g in group_adjacent_rects(rects):
            if len(g) > 1:
                polygons.extend(
                    adjacent_rects_corners_to_polygons([r.corners() for r in g])
                )
            else:
                polygons.append(g[0].polygon())

        zonelevel[k] = polygons


def convert_def_to_json(inf, outf, mapindex, color, warn_intersections):
    rgx_should_parse_ints = compile(r'^\d')
    rgx_parse_ints = compile(r'(-?\d+)')
    rgx_parse_comment = compile(r'^#(.+)$')

    maplevel = {'color': color, 'zones': {} }
    output = { mapindex: maplevel }
    zonename = 'unnamed'
    rects = []

    for line in sys.stdin:
        if m := rgx_parse_comment.match(line):
            if len(rects):
                maplevel['zones'][zonename] = rects
            zonename = m.group(1).strip()
            rects = []
        elif rgx_should_parse_ints.match(line):
            six_ints = tuple(map(int, rgx_parse_ints.findall(line)))

            # The last two ints look like zmin and zmax?
            # Irrelevant for worldmap.
            rects.append(Rect(*six_ints[:4]))

    if len(rects):
        maplevel['zones'][zonename] = rects

    rects_to_polygons(maplevel['zones'], warn_intersections)

    dump(output, outf, sort_keys=True, indent=4)


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(
        usage="""Usage: %prog [-m MAPINDEX] [-c COLOR] [-w] \\
            < guardlines.def [ > output.zones.json ]

This program processes rectangles from guardlines.def (the file that Razor
Community Edition uses) and merges the adjacent ones into polygons, and
finally writes the total output into a JSON format for use by ClassicUO's
new (Jan 2022) 'Zones' feature for the 'World Map'."""
    )

    parser.add_option("-m", "--mapindex", type="int", default=0,
        help="Set 'World.MapIndex' to which these zones belong (default 0)")
    parser.add_option("-c", "--color", type="string", default="green",
        help="Set color these zones should be drawn (default green)")
    parser.add_option("-w", "--warn-intersections", action='store_true',
        help="Warn on stderr about intersecting rects within groups",
        default=False)

    (options, args) = parser.parse_args()

    convert_def_to_json(sys.stdin, sys.stdout,
        options.mapindex, options.color, options.warn_intersections)

