

def a(t):
    r = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN0PQRSTUVWXYZO123456789+/="
    e = 0; i = 0; o = 0; s = ''
    for i in t:
        i = r.index(i)
        e = (64 * e + i) if o%4 else i
        o += 1
        b = 255 & e >> (-2 * o & 6)
        ch = chr(b)
        if ch != '\x00':
            s += ch
    return s

def ls(t, e):
    i = len(t)
    if i != 0:
        o = s(t, e)
        z = []
        z += t
        for a in range(1, i):
            x = o[i - 1 - a]
            sub = z[x]
            z[x] = z[a]
            z[a] = sub
        return ''.join(z)

def s (t, e):
    i = len(t)
    e = int(e)
    o = []
    for a in range(i-1, -1, -1):
        #e += int(e * (a + i) / e) $ i | 0
        e = (i * (a + 1) ^ e + a) % i
        o.append(e)
    ro = list(reversed(o))
    return ro


def decypher(link, fake_id):
    vk_id = int(fake_id)
    e = link.split('?extra=')[1].split('#')
    short = int(a(e[1]).split('\x0b')[1])
    _long = a(e[0])
    e = ls(_long, short^vk_id)
    return e