
def transform90axis( upAxis, vals ):
    # x - on side
    # y - upright
    # z - flat
    #[ -x, -y, z]
    if upAxis == 'x':
        return [-vals[1],-vals[2],vals[0]]
    elif upAxis == 'y':
        return [vals[0],-vals[2],vals[1]]
    elif upAxis == 'z': 
        return [vals[0],vals[1],vals[2]]