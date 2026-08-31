# 토큰 네이밍 체계와 다크모드 규칙

이 문서는 두 가지를 정의한다. 어떤 이름 체계를 쓸지, 그리고 라이트 값에서 다크 값을 어떻게 도출할지.

---

## 1. 두 층

**원시 토큰(primitive)** 은 색 그 자체다. 역할을 모른다.

```
coral-50 … coral-900   gray-0 … gray-900   sky-500   lime-500
```

원시 토큰에 역할 이름을 붙이지 않는다. `primary-500`은 원시가 아니다. 원시는 브랜드 팔레트고, 역할은 그 위 층이다.

**기능 토큰(semantic)** 은 역할이다. 값을 직접 갖지 않고 원시를 참조한다.

```
--surface-bg: var(--coral-50)   (O)
--surface-bg: #FFF4F0            (X — 원시를 우회하면 두 층으로 나눈 의미가 없다)
```

컴포넌트 코드는 **기능 토큰만** 쓴다. 원시를 직접 참조하는 순간 다크모드 전환과 리브랜딩이 다시 전수 수정이 된다.

---

## 2. 어떤 체계를 쓰는가 (감지 규칙)

| 감지 조건 | 체계 |
| --- | --- |
| `react-native` 또는 `nativewind` 의존성 있음 | **A. 역할 단계형** |
| 웹이고 `components/ui/`, `class-variance-authority`, `tailwindcss-animate` 중 하나라도 있음 | **B. foreground 쌍형** |
| 웹이고 위 흔적 없음 | **A**를 정본으로 하고, B 별칭 추가를 선택지로 제시 |

기존 프로젝트에 이미 한쪽 체계가 있으면 그것을 따른다. 감지 규칙보다 우선한다.

---

## 3. 체계 A — 역할 단계형

React Native·NativeWind 기본. shadcn/ui를 쓸 수 없는 환경이라 생태계 호환 이점이 없고, 단계가 명시적이라 읽기 쉽다.

| 그룹 | 토큰 | 역할 |
| --- | --- | --- |
| surface | `surface-bg` | 화면 기본 배경 |
| | `surface-bg-muted` | 한 단계 눌린 면 (카드 뒤, 섹션 구분) |
| | `surface-bg-subtle` | 가장 눌린 면 (입력 필드 배경, 비활성 영역) |
| text | `text` | 본문 |
| | `text-muted` | 부제·보조 설명 |
| | `text-subtle` | 플레이스홀더·비활성 |
| border | `border` | 장식용 구분선 (divider). 의미를 전달하지 않는다 |
| | `border-strong` | 의미 있는 경계 (입력 필드 테두리, 포커스 링, 선택 상태) |
| primary | `primary` | 주 액션 면 |
| | `primary-soft` | 옅은 강조 배경 (뱃지, 선택 상태) |
| | `primary-deep` | 눌림·호버 |
| | `on-primary` | primary·primary-deep 위 글자 |
| 상태 | `danger` / `danger-soft` / `on-danger` | 파괴적 액션·에러 |
| | `success` / `warning` (필요할 때만) | |

채색 면 위 글자는 **`on-<면이름>` 하나로만** 표현한다. `text-on` 같은 범용 토큰을 따로 두지 않는다. 두면 어느 쪽이 우선인지 모호해지고, 실제로는 대개 같은 값이라 죽은 토큰이 된다.

프로젝트에 도메인 색군이 있으면 같은 3단 구조로 확장한다. 예: `domain-course-soft / -base / -deep`. 이때 그 위 글자도 `on-domain` 처럼 짝을 만든다.

### 필수 대비 쌍

`tokens.py check`의 쌍별 기준을 함께 적는다. 세 번째 항목이 기준이다.

```json
{
  "text on surface-bg":              ["…", "…"],
  "text-muted on surface-bg":        ["…", "…"],
  "text-subtle on surface-bg":       ["…", "…"],
  "text on surface-bg-muted":        ["…", "…"],
  "text on surface-bg-subtle":       ["…", "…"],
  "text-muted on surface-bg-subtle": ["…", "…"],
  "text-subtle on surface-bg-subtle":["…", "…"],
  "on-primary on primary":           ["…", "…"],
  "on-primary on primary-deep":      ["…", "…"],
  "text on primary-soft":            ["…", "…"],
  "on-danger on danger":             ["…", "…"],
  "text on danger-soft":             ["…", "…"],
  "border-strong on surface-bg":     ["…", "…", "ui"]
}
```

`text-subtle` × `surface-bg-subtle`을 빼먹기 쉬운데, 플레이스홀더가 입력 필드 위에 올라가는 조합이라 설계상 반드시 만난다. 여기가 실무에서 가장 자주 깨진다.

**`border`는 대비 기준을 두지 않는다.** 흰 배경 위에서 3:1을 넘는 회색은 이미 구분선이 아니라 실선 프레임이다. `border`는 장식이므로 면제하고, 의미를 전달하는 경계는 전부 `border-strong`으로 보내 거기에만 3:1(`ui`)을 건다. 이 분리를 안 하면 매번 "구분선을 진하게 만들지 접근성을 포기할지" 사이에서 막힌다.

`primary-deep`은 같은 버튼의 눌림 상태라 `on-primary`를 그대로 쓴다. 그래서 `on-primary on primary-deep`도 필수다.

### Tailwind 키 매핑

CSS 변수 이름은 위 표 그대로 두되, Tailwind 색 키는 아래처럼 바꿔 등록한다. 그대로 등록하면 클래스가 `text-text-muted`, `border-border-strong`이 되어 쓰기 나쁘다.

| CSS 변수 | Tailwind 키 | 결과 클래스 |
| --- | --- | --- |
| `--surface-bg` 계열 | `surface` | `bg-surface`, `bg-surface-muted`, `bg-surface-subtle` |
| `--text` 계열 | `fg` | `text-fg`, `text-fg-muted`, `text-fg-subtle` |
| `--border` 계열 | `line` | `border-line`, `border-line-strong` |
| `--primary` 계열 | `primary` | `bg-primary`, `bg-primary-soft`, `text-on-primary` |

매핑표를 `docs/DESIGN_TOKENS.md`에 반드시 적는다. 변수명과 클래스명이 다르다는 사실을 문서 없이 알 방법이 없다.

## 4. 체계 B — foreground 쌍형

shadcn/ui 생태계 표준. 배경 토큰마다 그 위에 올릴 글자색이 짝으로 정의된다.

```
--background / --foreground
--card / --card-foreground
--popover / --popover-foreground
--muted / --muted-foreground
--accent / --accent-foreground
--primary / --primary-foreground
--secondary / --secondary-foreground
--destructive / --destructive-foreground
--border  --input  --ring
```

규칙은 하나다. **`bg-X`를 쓰면 글자는 `text-X-foreground`다.** 다른 조합은 대비 검사를 통과하지 못한다고 보고 의심한다.

체계 A보다 단계가 적다. 회색 3단계가 필요하면 `--muted` 하나로는 부족하니 `--muted-2` 같은 확장이 생기는데, 그때는 확장분도 반드시 `-foreground` 짝을 함께 만든다.

**필수 대비 쌍**: 정의된 모든 `X` / `X-foreground` 조합 전부. 추가로 `border` on `background`.

---

## 5. 다크모드 도출 규칙

라이트 값을 그대로 반전(255 - v)하지 않는다. 색이 탁해지고 브랜드 색이 무너진다. 아래 규칙을 항목별로 적용한다.

### 5-1. 면(surface)은 순서를 뒤집는다

라이트에서 `bg`가 가장 밝고 `subtle`이 가장 어둡다. 다크에서는 **`bg`가 가장 어둡고 subtle이 가장 밝다.** 눌린 면일수록 밝아진다.

```
라이트: bg #FFFFFF > bg-muted #FAFAFA > bg-subtle #EDEFEA
다크:   bg #141710 < bg-muted #1E2119 < bg-subtle #2A2E24
```

다크 배경은 순검정(`#000000`)을 쓰지 않는다. OLED 번짐과 그림자 표현 불가 때문이다. gray-900 근처에서 시작한다.

### 5-2. 글자(text)는 순서를 유지한다

`text`가 가장 진하고 `subtle`이 가장 흐린 관계는 다크에서도 같다. 다만 **밝기 방향이 반대**다.

```
라이트: text(어두움) → muted → subtle(밝음, 배경에 가까워짐)
다크:   text(밝음)   → muted → subtle(어두움, 배경에 가까워짐)
```

핵심은 "배경에 가까워질수록 흐리다"이지 "밝다/어둡다"가 아니다. 여기를 헷갈리면 다크에서 subtle이 본문보다 눈에 띄게 된다.

다크 본문은 순백(`#FFFFFF`)을 쓰지 않는다. 어두운 배경 위 순백은 눈부심(halation)을 일으킨다. gray-50~100 범위를 쓴다.

### 5-3. 브랜드 색은 채도를 낮추고 밝기를 올린다

어두운 배경 위에서 같은 채도는 과하게 튄다. 라이트의 `primary`를 다크에서 그대로 쓰면 대비도 대개 미달이다.

```
다크 primary      = 라이트보다 한두 단계 밝은 원시 (예: coral-500 → coral-300)
다크 primary-soft = 라이트의 옅은 배경 대신, 어두운 채색면 (예: coral-900)
다크 primary-deep = 다크 primary 기준으로 한 단계 어두운 값 (예: coral-300 → coral-400)
```

`primary-deep`을 정할 때 **같은 `on-primary`가 그 위에서도 대비를 넘는지 반드시 확인한다.** 눌림 상태는 같은 버튼이라 글자색을 바꿀 수 없다. 못 넘기면 `primary`를 한 단계 더 밝게 올려 두 값 모두 여유를 만든다.

`primary-soft` 같은 강조 채색면은 §5-1의 "순검정 금지"가 말하는 base surface가 아니다. 900단계가 검정에 가까워도 그대로 쓴다. 대신 `text on primary-soft`를 대비 검사에 반드시 넣는다.

### 5-4. on- 토큰은 다시 계산한다

`on-primary`가 라이트에서 흰색이었다고 다크에서도 흰색인 보장이 없다. 다크 `primary`가 밝아졌으면 그 위 글자는 **어두워야** 한다. §5-5 검사에서 반드시 걸린다.

### 5-5. 검사

라이트·다크 양쪽 모두 §3 또는 §4의 필수 대비 쌍을 `tokens.py check`로 돌린다. AA(4.5:1) 미달 항목은 값을 조정한다. 조정해도 브랜드 제약으로 못 넘기면 그 사실과 사용 제한(큰 글씨 전용 등)을 문서에 남긴다. 조용히 넘어가지 않는다.

---

## 6. 출력 형식

스택에 맞는 조합 하나만 만든다. "하나"는 **체계 하나**를 뜻하지 파일 하나가 아니다. NativeWind는 구조상 세 파일이 나온다.

### 웹 — Tailwind v4

```css
@import "tailwindcss";

/* 1층. 원시 */
@theme {
  --color-coral-500: #FF8A7A;
  --color-gray-0: #FFFFFF;
}

/* 2층. 기능 — 라이트 */
:root { --surface-bg: var(--color-gray-0); }

/* 2층. 기능 — 다크. 수동 설정이 시스템 설정을 이긴다 */
.dark, :root:has(.dark) { --surface-bg: var(--color-gray-900); }
@media (prefers-color-scheme: dark) {
  :root:not(.light) { --surface-bg: var(--color-gray-900); }
}

/* 기능 토큰을 유틸리티로 노출한다. inline이 없으면 v4가 빌드 시점 값으로
   고정해 다크 전환이 죽는다. 이 블록이 있어야 bg-surface 클래스가 생긴다 */
@theme inline {
  --color-surface: var(--surface-bg);
  --color-fg: var(--text);
}
```

`@theme inline` 블록을 빼면 컴포넌트가 매번 `bg-[var(--surface-bg)]`를 써야 한다. 반드시 넣는다.

### 모바일 — Tailwind v3 / NativeWind v4

세 파일이 나온다. 층이 다르므로 중복이 아니다.

| 파일 | 담는 것 |
| --- | --- |
| `tailwind.config.js` | 원시 토큰(hex) + 기능 토큰의 **키 등록**. 기능 값은 `rgb(var(--x) / <alpha-value>)` 참조 |
| `global.css` | 기능 토큰의 실제 값. NativeWind가 읽으므로 hex가 아니라 `"R G B"` 채널 형식 |
| `theme/*.ts` | CSS 변수가 닿지 않는 곳을 위한 **해석된 기능값 사본** |

**`global.css`를 앱 진입점에서 import해야 동작한다.** `app/_layout.tsx` 최상단에 `import "@/global.css"`가 없으면 기능 클래스가 값 없이 렌더된다. 조용히 실패하므로 배선을 반드시 확인한다.

**`:root:not(.light)`를 쓰지 않는다.** React Native에는 `:root`도 루트 클래스도 `:not()` 지원도 없다. 대신 선언 순서로 같은 우선순위를 만든다.

```
:root { … }                              라이트 기본
@media (prefers-color-scheme: dark) { :root { … } }   시스템 다크
.dark:root { … }                         수동 다크
.light:root { … }                        수동 라이트 (마지막이라 시스템 다크를 이긴다)
```

런타임 전환은 셀렉터가 아니라 NativeWind의 `colorScheme.set()`이 담당한다.

**`theme/*.ts`가 담는 것은 원시가 아니라 기능값이다.** 원시만 담으면 컴포넌트가 다크 분기를 직접 해야 해서 2층 구조의 의미가 사라진다. RN에는 캐스케이드가 없으므로 라이트·다크 두 객체를 두고 `useColorScheme()`으로 고른다.

```ts
export const colors = { light: { surfaceBg: '#FFFFFF', … }, dark: { … } };
export const colorsFor = (s: 'light' | 'dark') => colors[s];
```

이 사본은 `global.css`와 값이 물리적으로 중복된다. 피할 방법이 없으므로 **정본이 어느 쪽인지 파일 주석에 박는다.** "정본은 `tailwind.config.js`(원시)와 `global.css`(기능). `theme/*`는 사본이고 어긋나면 사본이 틀린 것."

CSS 변수가 닿지 않는 곳은 그림자만이 아니다. StatusBar·NavigationBar 색, expo-router 헤더 옵션, react-navigation 테마, SVG·차트 색이 전부 여기에 해당한다.

**그림자는 기능 토큰 체계 밖에 둔다.** 그림자 색은 면 위의 색이 아니라 빛의 부재라 역할 레이어에 넣을 자리가 없다. `theme/shadow.ts`에 iOS `shadow*`와 Android `elevation`을 함께 담는다. 다크에서 그림자 색은 `#000000`을 써도 된다. §5-1의 순검정 금지는 surface에 대한 규칙이고, 어두운 면 위에서 회색 그림자는 보이지 않는다.
