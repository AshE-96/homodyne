# Copied unchanged (apart from this header) from HMD-S06: parts/03-standalone/hmd-s06-damavand-summit-weather/artifact/grib2_point.py
# (28 Nov 2026). Credit: the HMD-S06 pure-Python GRIB2 point decoder. Kept as a copy so the two episodes stay independent.
"""grib2_point.py · HMD-S06 · read a few grid points out of one GRIB2 message, standard library only.

ECMWF open data (IFS and AIFS, 0.25°) packs every field with CCSDS/AEC compression (GRIB2 data
template 5.42). We do not install ecCodes; instead this file implements the small part we need:

  * sections 3 (regular lat-lon grid, template 3.0) and 5 (template 5.0 simple or 5.42 CCSDS);
  * the CCSDS 121.0-B adaptive entropy decoder (zero-block, second-extension, split-sample,
    uncompressed options) with the unit-delay preprocessor, as in libaec;
  * decoding stops as soon as the highest grid index we asked for has been reached, so a point at
    36° N costs about 40% of a full field.

    from grib2_point import read_points
    vals = read_points(grib_bytes, [(35.9517, 52.1092)])   # -> {'values': [[v00, v01, v10, v11]], ...}

It is a teaching-sized decoder, not a replacement for ecCodes: no bitmaps, no other grids, no
complex packing. Anything unexpected raises ValueError rather than returning a wrong number.
"""
import math
import struct

ROS = 5  # "remainder of segment" marker in the zero-block option


def _sections(msg):
    if msg[:4] != b'GRIB' or msg[7] != 2:
        raise ValueError('not a GRIB2 message')
    p, out = 16, {}
    while p < len(msg) - 4:
        if msg[p:p + 4] == b'7777':
            break
        ln = struct.unpack('>I', msg[p:p + 4])[0]
        out[msg[p + 4]] = msg[p:p + ln]
        p += ln
    return out


def _smag32(b):
    v = struct.unpack('>I', b)[0]
    return -(v & 0x7FFFFFFF) if v & 0x80000000 else v


def _smag16(b):
    v = struct.unpack('>H', b)[0]
    return -(v & 0x7FFF) if v & 0x8000 else v


def grid(sec3):
    """Regular lat-lon (template 3.0): Ni, Nj, first point, increments, scanning mode."""
    if struct.unpack('>H', sec3[12:14])[0] != 0:
        raise ValueError('only grid template 3.0 is supported')
    ni, nj = struct.unpack('>II', sec3[30:38])
    la1, lo1 = _smag32(sec3[46:50]) / 1e6, _smag32(sec3[50:54]) / 1e6
    la2, lo2 = _smag32(sec3[55:59]) / 1e6, _smag32(sec3[59:63]) / 1e6
    di, dj = struct.unpack('>II', sec3[63:71])
    scan = sec3[71]
    if scan not in (0, 64):
        raise ValueError(f'scanning mode {scan} not supported')
    return dict(ni=ni, nj=nj, la1=la1, lo1=lo1, la2=la2, lo2=lo2, di=di / 1e6, dj=dj / 1e6, south_to_north=bool(scan & 64))


def neighbours(g, lat, lon):
    """The four grid points around (lat, lon): flat indices and bilinear weights."""
    fj = (lat - g['la1']) / g['dj'] if g['south_to_north'] else (g['la1'] - lat) / g['dj']
    fi = ((lon - g['lo1']) % 360.0) / g['di']
    j0, i0 = int(math.floor(fj)), int(math.floor(fi))
    tj, ti = fj - j0, fi - i0
    pts = []
    for dj, wj in ((0, 1 - tj), (1, tj)):
        for di, wi in ((0, 1 - ti), (1, ti)):
            j, i = j0 + dj, (i0 + di) % g['ni']
            pts.append((j * g['ni'] + i, wj * wi, g['la1'] + (-1 if not g['south_to_north'] else 1) * j * g['dj'],
                        (g['lo1'] + i * g['di'] + 180) % 360 - 180))
    return pts


class _Bits:
    """MSB-first bit reader over a '0101…' string (str.find makes the unary codes fast)."""

    def __init__(self, data):
        self.s = ''.join(f'{x:08b}' for x in data)
        self.p = 0

    def get(self, n):
        if n == 0:
            return 0
        v = int(self.s[self.p:self.p + n], 2)
        if self.p + n > len(self.s):
            raise ValueError('CCSDS stream ended early')
        self.p += n
        return v

    def fs(self):
        q = self.s.find('1', self.p)
        if q < 0:
            raise ValueError('CCSDS stream ended early (fundamental sequence)')
        v = q - self.p
        self.p = q + 1
        return v


def aec_decode(data, bits_per_sample, block_size, rsi, flags, n_wanted):
    """Decode the first n_wanted samples of a CCSDS 121.0-B stream (libaec semantics)."""
    if flags & 1:
        raise ValueError('signed samples not supported')
    pp = bool(flags & 8)
    if flags & 16 and bits_per_sample <= 4:
        raise ValueError('restricted coding option not supported')
    if flags & 32:
        raise ValueError('RSI padding not supported')
    id_len = 5 if bits_per_sample > 16 else 4 if bits_per_sample > 8 else 3
    id_max = (1 << id_len) - 1
    xmax = (1 << bits_per_sample) - 1
    br = _Bits(data)
    out = []
    rsi_samples = rsi * block_size
    # second-extension table: m -> (beta, ms)
    se = []
    for beta in range(0, 14):
        ms = beta * (beta + 1) // 2
        for _ in range(beta + 1):
            se.append((beta, ms))
    while len(out) < n_wanted:
        rsi_start = len(out)
        block = []          # mapped residuals of this RSI (reference sample stored raw)
        used = 0
        ref_val = None
        while used < rsi_samples and rsi_start + used < n_wanted:
            ref = 1 if (pp and used == 0) else 0
            ident = br.get(id_len)
            if ident == 0:
                sel = br.get(1)
                if ref:
                    ref_val = br.get(bits_per_sample)
                    used += 1
                if sel == 1:                      # second extension
                    i = ref
                    while i < block_size:
                        m = br.fs()
                        if m >= len(se):
                            raise ValueError('bad second-extension code')
                        beta, ms = se[m]
                        d1 = m - ms
                        if i & 1 == 0:
                            block.append(beta - d1)
                            i += 1
                        block.append(d1)
                        i += 1
                    used += block_size - ref
                else:                             # zero block(s)
                    zb = br.fs() + 1
                    if zb == ROS:
                        b = used // block_size
                        zb = min(rsi - b, 64 - (b % 64))
                    elif zb > ROS:
                        zb -= 1
                    n0 = zb * block_size - ref
                    block.extend([0] * n0)
                    used += n0
            elif ident == id_max:                 # uncompressed
                vals = [br.get(bits_per_sample) for _ in range(block_size)]
                if ref:
                    ref_val, vals = vals[0], vals[1:]
                    used += 1
                block.extend(vals)
                used += len(vals)
            else:                                 # split sample, k = id - 1
                k = ident - 1
                if ref:
                    ref_val = br.get(bits_per_sample)
                    used += 1
                n = block_size - ref
                hi = [br.fs() for _ in range(n)]
                if k:
                    hi = [(h << k) | br.get(k) for h in hi]
                block.extend(hi)
                used += n
        # undo the preprocessor (unit-delay predictor + mapping)
        if pp:
            x = ref_val
            seq = [x]
            for d in block:
                theta = min(x, xmax - x)
                if d <= 2 * theta:
                    x = x + (d >> 1) if d & 1 == 0 else x - ((d + 1) >> 1)
                elif theta == x:
                    x = d
                else:
                    x = xmax - d
                seq.append(x)
            out.extend(seq)
        else:
            out.extend(block)
        if used < rsi_samples:
            break
    return out[:n_wanted]


def read_points(msg, latlons):
    """Bilinear values at each (lat, lon) and the four raw corner values."""
    s = _sections(msg)
    g = grid(s[3])
    s5, s6, s7 = s[5], s[6], s[7]
    if s6[5] != 255:
        raise ValueError('bitmaps not supported')
    tmpl = struct.unpack('>H', s5[9:11])[0]
    R = struct.unpack('>f', s5[11:15])[0]
    E, D = _smag16(s5[15:17]), _smag16(s5[17:19])
    nbits = s5[19]
    plan = [neighbours(g, la, lo) for la, lo in latlons]
    need = max(idx for pts in plan for idx, *_ in pts) + 1
    if nbits == 0:
        raw = [0] * need
    elif tmpl == 0:
        br = _Bits(s7[5:5 + (need * nbits + 7) // 8 + 1])
        raw = [br.get(nbits) for _ in range(need)]
    elif tmpl == 42:
        flags, bsize, rsi = s5[21], s5[22], struct.unpack('>H', s5[23:25])[0]
        raw = aec_decode(s7[5:], nbits, bsize, rsi, flags, need)
    else:
        raise ValueError(f'data template 5.{tmpl} not supported')
    scale, dec = 2.0 ** E, 10.0 ** D
    res = []
    for pts in plan:
        corners = [(R + raw[idx] * scale) / dec for idx, *_ in pts]
        res.append(dict(value=sum(c * w for c, (_, w, *_r) in zip(corners, pts)), corners=corners,
                        corner_latlon=[(la, lo) for _, _, la, lo in pts]))
    return dict(grid=g, template=tmpl, nbits=nbits, points=res)


def messages(blob):
    """Split a file of concatenated GRIB2 messages."""
    p, out = 0, []
    while p + 16 <= len(blob):
        if blob[p:p + 4] != b'GRIB':
            q = blob.find(b'GRIB', p + 1)
            if q < 0:
                break
            p = q
            continue
        ln = struct.unpack('>Q', blob[p + 8:p + 16])[0]
        out.append(blob[p:p + ln])
        p += ln
    return out


def product(msg):
    """(discipline, category, number, level type, level value) from sections 0 and 4 (templates 4.0/4.8)."""
    s = _sections(msg)
    s4 = s[4]
    cat, num = s4[9], s4[10]
    ltype, lscale = s4[22], s4[23]
    lval = struct.unpack('>I', s4[24:28])[0]
    if lval != 0xFFFFFFFF and lscale != 0xFF:
        lval = lval / 10 ** (lscale if lscale < 128 else -(lscale & 0x7F))
    return msg[6], cat, num, ltype, lval
