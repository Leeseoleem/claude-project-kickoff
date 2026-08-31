#!/usr/bin/env python3
"""디자인 토큰 보조 도구. 표준 라이브러리만 사용한다.

  scan <경로...>              하드코딩된 색·radius·spacing 수집
  contrast <fg> <bg> [기준]   대비비 하나. 기준은 text(기본) | ui | large
  check <json파일> [--md]     쌍 일괄 검사. --md면 마크다운 표로 출력
  scale <hex> [이름] [단계]   기준색을 그 단계에 두고 스케일 생성 (기본 500)
  fill <json파일> [이름]      확정된 단계들 사이를 메워 빈 단계만 생성
  audit <json파일> [--same-family]  사실상 중복인 색 찾기

check 입력 형식 (기준을 쌍마다 선언한다):
  {"text on bg": ["#111", "#FFF"],            <- 기준 text = 4.5:1
   "border on bg": ["#CCC", "#FFF", "ui"],    <- 기준 ui   = 3:1
   "제목": ["#777", "#FFF", "large"]}          <- 기준 large = 3:1

fill 입력 형식 (확정값만 넣는다. 나머지는 생성된다):
  {"500": "#FF8A7A", "700": "#E2503C"}

모든 출력은 JSON(--md 제외). 사람이 읽는 정리는 호출한 쪽에서 한다.
"""
import sys, os, re, json, math
from collections import Counter, defaultdict

# ---------- 색 변환 ----------

def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6:
        raise ValueError(f'hex 형식이 아니다: {h}')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#' + ''.join(f'{max(0, min(255, round(c * 255))):02X}' for c in rgb)

def _srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _lin_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

def rgb_to_oklab(rgb):
    r, g, b = (_srgb_to_lin(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (max(0.0, v) ** (1 / 3) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )

def oklab_to_rgb(lab):
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v ** 3 for v in (l_, m_, s_))
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    raw = (r, g, bb)
    clipped = any(c < -0.002 or c > 1.002 for c in raw)
    return tuple(min(1.0, max(0.0, _lin_to_srgb(c))) for c in raw), clipped

def to_hex(lab):
    rgb, clipped = oklab_to_rgb(lab)
    return rgb_to_hex(rgb), clipped

def luminance(rgb):
    r, g, b = (_srgb_to_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(fg, bg):
    a, b = luminance(hex_to_rgb(fg)), luminance(hex_to_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)

def delta_ok(h1, h2):
    """OKLab 유클리드 거리. 0.02 미만이면 눈으로 구분이 거의 안 된다."""
    a, b = rgb_to_oklab(hex_to_rgb(h1)), rgb_to_oklab(hex_to_rgb(h2))
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

# ---------- scan ----------

COLOR_RE = re.compile(
    r'#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b'
    r'|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)'
    r'|hsla?\(\s*[\d.]+(?:deg)?\s*,?\s*[\d.]+%\s*,?\s*[\d.]+%\s*(?:[,/]\s*[\d.]+%?\s*)?\)'
)
RGB_RE = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)')

RADIUS_RE = re.compile(r'(?:border-?[Rr]adius\s*[:=]\s*|rounded-\[)\s*(\d+(?:\.\d+)?)\s*(?:px)?')
SPACING_RE = re.compile(
    r'(?:(?:padding|margin|gap|rowGap|columnGap|top|left|right|bottom)'
    r'(?:Horizontal|Vertical|Top|Bottom|Left|Right|Block|Inline)?\s*[:=]\s*'
    r'|(?:[pmgxy]|p[trblxy]|m[trblxy]|gap)-\[)\s*(\d+(?:\.\d+)?)\s*(?:px)?')

SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '.next', '.expo', 'ios', 'android',
             'coverage', '__pycache__', '.claude', 'vendor', 'Pods', '.turbo'}
CODE_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.css', '.scss', '.sass', '.less',
             '.vue', '.svelte', '.html', '.json', '.mjs', '.cjs'}
DOC_EXTS = {'.md', '.mdx'}

# 정의 파일은 파일명이 정확히 알려진 것만 인정한다.
# 느슨한 경로 매칭(theme|colors 포함)은 ThemeCard.tsx 같은 일반 컴포넌트를 통째로 숨긴다.
DEF_BASENAME = re.compile(
    r'^(tailwind\.config\.[a-z]+'
    r'|(?:design[-_])?tokens?(?:\.[a-z0-9]+)*\.json'
    r'|(?:colors?|colours?|variables?|theme|globals?|global|design[-_]tokens?)\.(?:css|scss|less)'
    r')$', re.I)
# 줄 모양으로 보는 정의. 파일명보다 이쪽이 정확하다.
DEF_LINE = re.compile(
    r'^\s*(?:--[\w-]+|\$[\w-]+|@define-color\s+[\w-]+'
    r'|["\']?[\w.-]+["\']?)\s*:\s*["\']?(?:#[0-9a-fA-F]{3,8}|rgba?\()')

def _normalize(val):
    """같은 색이 hex와 rgb()로 흩어지지 않게 hex로 모은다. hsl은 그대로 둔다."""
    if val.startswith('#'):
        try:
            return rgb_to_hex(hex_to_rgb(val))
        except ValueError:
            return None
    m = RGB_RE.match(val)
    if m:
        r, g, b = (int(x) for x in m.groups())
        if max(r, g, b) > 255:
            return None
        return rgb_to_hex((r / 255, g / 255, b / 255))
    return val

def cmd_scan(paths):
    hits, defs, docs = Counter(), Counter(), Counter()
    where = defaultdict(list)
    doc_where = defaultdict(list)
    radius, spacing = Counter(), Counter()
    rad_where, sp_where = defaultdict(list), defaultdict(list)
    files_scanned = 0
    for root_path in paths:
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            for fn in files:
                ext = os.path.splitext(fn)[1]
                is_doc = ext in DOC_EXTS
                if ext not in CODE_EXTS and not is_doc:
                    continue
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, root_path)
                file_is_def = bool(DEF_BASENAME.match(fn))
                try:
                    with open(fp, encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                except OSError:
                    continue
                files_scanned += 1
                for i, line in enumerate(lines, 1):
                    loc = f'{rel}:{i}'
                    for m in COLOR_RE.finditer(line):
                        val = _normalize(m.group(0))
                        if val is None:
                            continue
                        if is_doc:
                            docs[val] += 1
                            if len(doc_where[val]) < 8:
                                doc_where[val].append(loc)
                        elif file_is_def or DEF_LINE.match(line):
                            defs[val] += 1
                        else:
                            hits[val] += 1
                            if len(where[val]) < 8:
                                where[val].append(loc)
                    if is_doc:
                        continue
                    for m in RADIUS_RE.finditer(line):
                        v = m.group(1)
                        radius[v] += 1
                        if len(rad_where[v]) < 6:
                            rad_where[v].append(loc)
                    for m in SPACING_RE.finditer(line):
                        v = m.group(1)
                        spacing[v] += 1
                        if len(sp_where[v]) < 6:
                            sp_where[v].append(loc)

    def odd(v):
        try:
            f = float(v)
        except ValueError:
            return True
        return f % 4 != 0

    return {
        'files_scanned': files_scanned,
        'hardcoded': [{'value': v, 'count': c, 'sample_locations': where[v]}
                      for v, c in hits.most_common()],
        'in_definition_files': [{'value': v, 'count': c} for v, c in defs.most_common()],
        'in_docs': [{'value': v, 'count': c, 'sample_locations': doc_where[v]}
                    for v, c in docs.most_common()],
        'radius': [{'value': v, 'count': c, 'sample_locations': rad_where[v]}
                   for v, c in radius.most_common()],
        'spacing': [{'value': v, 'count': c, 'off_scale': odd(v),
                     'sample_locations': sp_where[v]}
                    for v, c in spacing.most_common()],
        'notes': [
            'hardcoded만 치환 대상 후보다.',
            'in_docs는 문서에 복사된 값이다. 코드와 어긋나기 쉬우니 함께 갱신한다.',
            'spacing의 off_scale=true는 4의 배수가 아니다. 의도인지 확인한다.',
        ],
    }

# ---------- contrast / check ----------

THRESHOLD = {'text': 4.5, 'ui': 3.0, 'large': 3.0}

def _row(name, fg, bg, kind='text'):
    kind = kind if kind in THRESHOLD else 'text'
    r = contrast_ratio(fg, bg)
    need = THRESHOLD[kind]
    return {'name': name, 'fg': fg, 'bg': bg, 'kind': kind,
            'ratio': round(r, 2), 'required': need, 'pass': r >= need,
            'AAA_text': r >= 7.0}

def cmd_contrast(fg, bg, kind='text'):
    return _row(f'{fg} on {bg}', fg, bg, kind)

def cmd_check(path, markdown=False):
    raw = json.load(open(path, encoding='utf-8'))
    rows = []
    for name, spec in raw.items():
        fg, bg = spec[0], spec[1]
        kind = spec[2] if len(spec) > 2 else 'text'
        rows.append(_row(name, fg, bg, kind))
    failing = [r['name'] for r in rows if not r['pass']]
    if markdown:
        out = ['| 쌍 | fg | bg | 기준 | 비율 | 판정 |', '|---|---|---|---|---|---|']
        for r in rows:
            out.append(f"| {r['name']} | `{r['fg']}` | `{r['bg']}` | {r['required']}:1 "
                       f"| {r['ratio']} | {'통과' if r['pass'] else '미달'} |")
        out.append('')
        out.append(f"{len(rows)}쌍 중 {len(failing)}쌍 미달"
                   + (f": {', '.join(failing)}" if failing else ''))
        return '\n'.join(out)
    return {'results': rows, 'failing': failing,
            'summary': f'{len(rows)}쌍 중 {len(failing)}쌍이 각자의 기준에 미달'}

# ---------- scale / fill ----------

STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
TARGET_L = {50: 0.97, 100: 0.94, 200: 0.88, 300: 0.79, 400: 0.70, 500: 0.62,
            600: 0.54, 700: 0.45, 800: 0.35, 900: 0.24, 950: 0.17}
L_MAX, L_MIN = 0.975, 0.15

def _chroma_k(direction, u):
    """밝은 쪽으로 갈수록 채도를 크게 낮춘다. 유지하면 형광 파스텔이 된다."""
    return max(0.06, 1 - 0.90 * (u ** 0.75)) if direction == 'up' else max(0.06, 1 - 0.30 * u)

def cmd_scale(base_hex, name='color', anchor=500):
    anchor = int(anchor)
    if anchor not in STEPS:
        raise ValueError(f'anchor는 {STEPS} 중 하나여야 한다')
    L0, a0, b0 = rgb_to_oklab(hex_to_rgb(base_hex))
    TA = TARGET_L[anchor]
    span_up = TARGET_L[STEPS[0]] - TA
    span_dn = TA - TARGET_L[STEPS[-1]]
    out, clipped_steps = {}, []
    for s in STEPS:
        if s == anchor:
            out[f'{name}-{s}'] = rgb_to_hex(hex_to_rgb(base_hex))
            continue
        if TARGET_L[s] > TA:
            u = (TARGET_L[s] - TA) / span_up if span_up > 1e-6 else 1.0
            L, k = L0 + u * max(0.0, L_MAX - L0), _chroma_k('up', u)
        else:
            u = (TA - TARGET_L[s]) / span_dn if span_dn > 1e-6 else 1.0
            L, k = L0 - u * max(0.0, L0 - L_MIN), _chroma_k('down', u)
        h, clipped = to_hex((L, a0 * k, b0 * k))
        out[f'{name}-{s}'] = h
        if clipped:
            clipped_steps.append(s)
    res = {'base': base_hex, 'anchored_at': anchor, 'scale': out,
           'warning': '생성값은 출발점이다. 브랜드 색은 디자이너 확인 후 손보정이 필요할 수 있다.'}
    if clipped_steps:
        res['gamut_clipped'] = clipped_steps
        res['gamut_note'] = ('이 단계들은 sRGB 범위를 벗어나 잘렸다. 채도가 무너져 '
                             '브랜드와 무관한 색이 됐을 수 있으니 눈으로 확인한다.')
    return res

def cmd_fill(path, name='color'):
    """확정된 단계는 그대로 두고 빈 단계만 채운다.

    브랜드 팔레트가 500과 700처럼 두 점 이상을 고정해 두는 경우를 위한 것이다.
    scale은 앵커 하나만 받아서 확정값과 어긋난다.
    """
    known_raw = json.load(open(path, encoding='utf-8'))
    known = {}
    for k, v in known_raw.items():
        s = int(re.sub(r'\D', '', str(k)))
        if s not in STEPS:
            raise ValueError(f'{k}: 단계는 {STEPS} 중 하나여야 한다')
        known[s] = rgb_to_hex(hex_to_rgb(v))
    if not known:
        raise ValueError('확정값이 최소 하나는 필요하다')
    anchors = sorted(known)
    labs = {s: rgb_to_oklab(hex_to_rgb(known[s])) for s in anchors}
    out, generated, clipped_steps = {}, [], []
    for s in STEPS:
        if s in known:
            out[f'{name}-{s}'] = known[s]
            continue
        lo = max([a for a in anchors if a < s], default=None)
        hi = min([a for a in anchors if a > s], default=None)
        if lo is not None and hi is not None:
            t = (TARGET_L[s] - TARGET_L[lo]) / (TARGET_L[hi] - TARGET_L[lo])
            lab = tuple(labs[lo][i] + t * (labs[hi][i] - labs[lo][i]) for i in range(3))
        else:
            a = lo if lo is not None else hi
            L0, a0, b0 = labs[a]
            if s < a:  # 더 밝은 쪽
                u = (TARGET_L[s] - TARGET_L[a]) / max(1e-6, TARGET_L[STEPS[0]] - TARGET_L[a])
                u = min(1.0, max(0.0, u))
                lab = (L0 + u * max(0.0, L_MAX - L0), a0 * _chroma_k('up', u), b0 * _chroma_k('up', u))
            else:      # 더 어두운 쪽
                u = (TARGET_L[a] - TARGET_L[s]) / max(1e-6, TARGET_L[a] - TARGET_L[STEPS[-1]])
                u = min(1.0, max(0.0, u))
                k = _chroma_k('down', u)
                lab = (L0 - u * max(0.0, L0 - L_MIN), a0 * k, b0 * k)
        h, clipped = to_hex(lab)
        out[f'{name}-{s}'] = h
        generated.append(s)
        if clipped:
            clipped_steps.append(s)
    # 밝기가 단조 감소하는지 확인한다. 확정값끼리 어긋나 있으면 여기서 걸린다
    Ls = [rgb_to_oklab(hex_to_rgb(out[f'{name}-{s}']))[0] for s in STEPS]
    non_mono = [STEPS[i] for i in range(len(Ls) - 1) if Ls[i] <= Ls[i + 1]]
    res = {'anchors': anchors, 'generated': generated, 'scale': out}
    if non_mono:
        res['not_monotonic_after'] = non_mono
        res['monotonic_note'] = '이 단계 다음이 더 밝거나 같다. 확정값끼리 간격이 어긋났을 수 있다.'
    if clipped_steps:
        res['gamut_clipped'] = clipped_steps
    return res

# ---------- audit ----------

def cmd_audit(path, same_family_only=False):
    tokens = json.load(open(path, encoding='utf-8'))
    def family(n):
        return re.split(r'[-_.]', n)[0]
    names = list(tokens)
    dupes = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if same_family_only and family(names[i]) != family(names[j]):
                continue
            try:
                d = delta_ok(tokens[names[i]], tokens[names[j]])
            except ValueError:
                continue
            if d < 0.02:
                dupes.append({'a': names[i], 'b': names[j],
                              'value_a': tokens[names[i]], 'value_b': tokens[names[j]],
                              'same_family': family(names[i]) == family(names[j]),
                              'delta': round(d, 4)})
    dupes.sort(key=lambda x: (not x['same_family'], x['delta']))
    return {'token_count': len(tokens), 'near_duplicates': dupes,
            'note': ('delta 0.02 미만은 눈으로 구분이 거의 안 된다. '
                     'same_family=true가 실제 문제일 가능성이 높다. '
                     '다른 색군의 가장 밝은 단계끼리 겹치는 것은 흔하고 대개 무해하다.')}

# ---------- main ----------

def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    c, rest = argv[1], argv[2:]
    md = '--md' in rest or '--markdown' in rest
    same = '--same-family' in rest
    pos = [a for a in rest if not a.startswith('--')]
    try:
        if c == 'scan':
            r = cmd_scan(pos or ['.'])
        elif c == 'contrast':
            r = cmd_contrast(pos[0], pos[1], pos[2] if len(pos) > 2 else 'text')
        elif c == 'check':
            r = cmd_check(pos[0], md)
        elif c == 'scale':
            r = cmd_scale(pos[0], pos[1] if len(pos) > 1 else 'color',
                          pos[2] if len(pos) > 2 else 500)
        elif c == 'fill':
            r = cmd_fill(pos[0], pos[1] if len(pos) > 1 else 'color')
        elif c == 'audit':
            r = cmd_audit(pos[0], same)
        else:
            print(__doc__)
            return 1
    except (IndexError, ValueError, OSError, KeyError) as e:
        print(json.dumps({'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False))
        return 1
    print(r if isinstance(r, str) else json.dumps(r, ensure_ascii=False, indent=1))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
