"""Shared sail shaping in the authored 114-vertex-per-blade layout."""
import math
from mathutils import Vector

INNER_WIDTH = .60
INNER_RADIUS = 5.5
OUTER_RADIUS = 47.8

def taper_sails(positions, width_factor=1.35):
    """Keep outer cloth width; converge straight rails gently toward the hub.

    Only rail spacing changes; cross sections retain their thickness. Rungs
    keep rectangular sections, cloth follows the frame, and the hub is untouched.
    """
    assert len(positions) == 518
    right=Vector((math.sqrt(3)/2,-.5,0)); up=Vector((0,0,1))
    hub=Vector((26.99117,-41.48987,90.94731))
    def factor(radius):return INNER_WIDTH+(1-INNER_WIDTH)*(radius-INNER_RADIUS)/(OUTER_RADIUS-INNER_RADIUS)
    for blade in range(4):
        angle=math.radians(22.5+blade*90)
        across=right*math.cos(angle)-up*math.sin(angle)
        along=right*math.sin(angle)+up*math.cos(angle)
        for local in range(114):
            idx=blade*114+local; p=Vector(positions[idx]); radial=(p-hub).dot(along)
            if local<16:
                side=-1 if local<8 else 1
                delta=side*4.5*width_factor*(factor(radial)-1)
            elif local<64:
                radial=[8,15.8,23.6,31.4,39.2,47][(local-16)//8]
                delta=(p-hub).dot(across)*(factor(radial)-1)
            elif local<82:
                delta=(p-hub).dot(across)*(factor(radial)-1)
            else:
                side=-1 if ((local-82)//8)%2==0 else 1
                radial=30.3 if local<98 else 47.2
                delta=side*4.5*width_factor*(factor(radial)-1)
            positions[idx]=p+across*delta
    return positions
