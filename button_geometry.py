#!/usr/bin/env python3.5
from os import system
if __name__ == '__main__':
	name = input("Name: ").strip()
	scale = input("Alpha-scale (default 1): ").strip()
	if scale == "":
		scale = 1
	else:
		scale = float(scale)
	system("cd /home/vanfed/Documents/Python/empire_game/lib/menu && egg-texture-cards -o {0}_maps.egg -p 240,240 -c 1,1,1,{1} {0}_ready.png {0}_click.png {0}_rollover.png {0}_disabled.png".format(name, scale))