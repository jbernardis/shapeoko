import math

def validateKeys(usedKeys, validKeys):
    badKeys = []

    for k in usedKeys:
        if k not in validKeys:
            badKeys.append(k)

    if len(badKeys) == 0:
        return None

    result = ["Invalid key(s) specified: %s" % ", ".join(badKeys),
              "Allowable keys are: %s" % ", ".join(validKeys.keys())]

    missingKeys = []
    for k in validKeys:
        if k not in usedKeys:
            missingKeys.append(k)

    if len(missingKeys) > 0:
        result.append("Missing keys: %s" % ", ".join(missingKeys))
        for k in missingKeys:
            result.append("%s: %s" % (k, validKeys[k]))

    return result

def triangulate(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    d = math.sqrt(dx*dx + dy*dy)
    return d
