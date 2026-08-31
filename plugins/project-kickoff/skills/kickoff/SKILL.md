---
name: kickoff
description: 프로젝트에 기본 문서 세트(CLAUDE.md, 커밋 컨벤션, 코드 리뷰 가이드, PR 템플릿, 사이클 회고 체계, PR 봇 리뷰 규칙)를 스택에 맞게 생성하고 .gitignore까지 설정한다. "프로젝트 세팅", "레포 세팅", "기본 문서 만들어줘", "CLAUDE.md 만들어줘", "새 프로젝트 시작할게", "킥오프" 요청이면 사용자가 명시적으로 스킬을 부르지 않아도 반드시 사용한다. 기존 레포에 문서 체계를 나중에 얹는 경우도 포함한다.
---

# 프로젝트 킥오프 문서 세팅

템플릿 문서를 프로젝트 스펙에 맞게 채워서 배치한다. 커밋 대상과 이그노어 대상을 나누고 `.gitignore`까지 손본다.

**템플릿 경로: `${CLAUDE_PLUGIN_ROOT}/skills/kickoff/templates/`**
플러그인은 설치 시 캐시로 복사되므로 상대 경로가 아니라 이 환경변수 경로로 읽는다.

**절대 규칙 두 개**

1. `{{PLACEHOLDER}}`가 한 개라도 파일에 남으면 실패다. 전부 실제 값으로 치환하거나 규칙대로 삭제한다.
   예외: `code-review.md` 안의 `${{ github.event.* }}`는 GitHub Actions 문법 그대로다. 치환 대상이 아니다.
2. 감지하지 못한 값을 추측으로 채우지 않는다. 모르면 STEP 2에서 묻거나 "미정"으로 명시한다.

---

## STEP 1. 현황 파악

기존 파일과 스펙을 한 번에 읽는다. 이 단계에서는 아무것도 쓰지 않는다.

### 1-1. 기존 파일 존재 여부

```
CLAUDE.md  README.md  .gitignore  docs/  .github/pull_request_template.md  .claude/  .env.example
```

하나라도 있으면 STEP 2에서 파일 단위로 처리 방법을 묻는다. 임의로 덮어쓰지 않는다.

### 1-2. 스펙 감지

| 읽을 것 | 뽑을 값 |
| --- | --- |
| `package.json` | 실제 서비스명 후보, 의존성과 **버전 range**, `scripts` 전체, `packageManager` |
| lock 파일 (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` / `bun.lock*`) | 패키지 매니저 확정 |
| `tsconfig.json` | strict 여부, path alias |
| `app.json` / `app.config.*` / `eas.json` | Expo 여부, 플러그인, 빌드 방식 |
| `package.json`의 `expo` 의존성 | **Expo SDK 버전.** `app.json`에는 SDK 정보가 없다 |
| `next.config.*` / `vite.config.*` | 웹 프레임워크, 라우터 방식 |
| `tailwind.config.*` 또는 CSS의 `@theme` | 스타일링 방식, 이미 정의된 토큰 실측값 |
| 루트·`src/` 폴더 목록 | 실제 폴더 구조 |
| `git branch -a`, `git symbolic-ref --short HEAD` | **실제 브랜치명.** `main`이라고 가정하지 않는다 |
| `git remote -v` | 리모트 유무 |
| `git ls-files .claude` | `.claude/` 하위가 이미 추적 중인지 |
| `.env.example` | 환경 변수 항목 |

### 1-3. 감지 원칙

- **버전은 `package.json`의 range를 그대로 옮긴다.** `~56.0.8`을 `56.0.8`로 바꾸지 않는다. lockfile을 파서 확정 버전을 캐지 않는다. package.json이 프로젝트가 선언한 값이고, 문서와 대조하기 쉽다.
- **파일이 있어도 비어 있으면 "존재하지만 비어 있음"으로 적는다.** 파일명만 보고 역할을 지어내지 않는다.
- **브랜치명은 실측값을 그대로 쓴다.** 레포가 `master`면 문서에도 `master`라고 적는다. 없는 브랜치명을 적으면 그 문서는 거짓이 된다. `main`으로 리네임할지는 STEP 2에서 물어본다.
- **`package.json`이 있으면 install 여부와 무관하게 버전 range를 적는다.** lock 파일이 비었거나 `node_modules`가 없으면 "설치 전 상태"라고 한 줄 덧붙인다. `package.json` 자체가 없을 때만 버전·명령어를 비우고 "설치 후 갱신" 주석을 남긴다.

---

## STEP 2. 확인 + 질문 (한 번에)

STEP 1 결과를 표로 보여주고, 아래를 **한 메시지에 묶어서** 물어본다. 여러 턴에 나눠 던지지 않는다.

**A. 감지 결과 확인**

1. 프로젝트명 — `package.json`의 `name`이 아니라 사용자가 실제로 부르는 이름. 후보를 제시하고 확인받는다 (예: package.json은 `uridoo-app`, app.json은 `우리두`)
2. 감지한 스택·버전·명령어·폴더 구조 — 틀린 게 있으면 고쳐달라고
3. 기존 파일이 있으면 파일 단위로 새로 만들지 / 병합할지 / 건너뛸지
4. 기본 브랜치명이 `master`면 그대로 쓸지 `main`으로 바꿀지. `dev`가 없으면 앞으로 팔 계획인지도 함께 (계획이 있으면 3단 전략으로 쓴다)

**B. 감지로 알 수 없는 것**

5. 프로젝트가 무엇을 하는지 2~3줄. **무엇이 아닌지도 한 줄** 받으면 범위가 잘 잡힌다
6. 배포 대상 (웹 / 앱스토어 / 사내 / 미정)
7. 작업 구성 — 혼자인지, 팀이면 사용자 역할과 나머지 담당 범위. 호칭 규칙과 리뷰 대상 PR 범위가 여기서 갈린다
8. 디자인 토큰 — 이미 있으면 원본 위치(Figma Variables, Tokens Studio, config). 없으면 "미정"
9. 한글·영문 표기(워드마크) 규칙이 있는지. 없으면 넘어간다

이 묶음 외에 별도 확인이 필요한 지점은 STEP 3의 `git rm --cached`와 STEP 6의 커밋 두 개뿐이다.

---

## STEP 3. .gitignore 먼저

파일을 만들기 전에 `.gitignore`부터 손댄다. 순서가 반대면 그 사이에 `git add -A`가 끼어 이그노어 대상이 커밋된다.

아래 블록을 추가한다.

```gitignore
# Claude Code
.claude/settings.local.json
.claude/local/
```

- `.gitignore`가 없으면 프레임워크 표준 ignore와 함께 새로 만든다.
- **있지만 부실하면 보완을 제안한다.** 스택 표준 항목(Next.js면 `.env*.local`, `out/`, `.vercel`, `next-env.d.ts` / Expo면 `.expo/`, `ios/`, `android/`, `*.jks`)이 빠졌으면 무엇이 빠졌는지 알리고 추가할지 묻는다. 환경 변수 누락은 특히 짚는다.
- 기존에 `.claude/` **전체를 무시하는 줄**이 있으면 이 블록으로 바꾸지 않는다. 범위가 좁아져서 그동안 안 올라가던 파일이 갑자기 추적 대상이 된다. 현재 상태를 알리고 어떻게 할지 묻는다.
- `git ls-files .claude`에 결과가 있으면 `git rm --cached -r .claude/local` 이 필요하다고 알린다. **실행은 확인받고 한다.**

작성 후 `git check-ignore -v .claude/local/PR_REVIEW_RULES.md` 로 규칙이 실제로 먹는지 확인한다.

---

## STEP 4. 파일 생성

`${CLAUDE_PLUGIN_ROOT}/skills/kickoff/templates/` 의 각 파일을 읽어 플레이스홀더를 치환한 뒤 배치한다.

**커밋 대상**

| 템플릿 | 배치 경로 |
| --- | --- |
| `CLAUDE.md` | `CLAUDE.md` |
| `commit-convention.md` | `docs/commit-convention.md` |
| `code-review.md` | `docs/code-review.md` |
| `pull_request_template.md` | `.github/pull_request_template.md` |
| `cycle-TEMPLATE.md` | `docs/log/TEMPLATE.md` |
| `decision-backlog.md` | `docs/log/decision-backlog.md` |
| `README.md` | `README.md` |

**이그노어 대상**

| 템플릿 | 배치 경로 |
| --- | --- |
| `PR_REVIEW_RULES.md` | `.claude/local/PR_REVIEW_RULES.md` |
| `cycle-note-TEMPLATE.md` | `.claude/local/notes/cycle-note-TEMPLATE.md` |

`.claude/local/reviews/`는 만들지 않는다. 첫 리뷰 때 생긴다. 문서 세 곳(`CLAUDE.md` 표, `docs/code-review.md` §4·프로젝트별 조정 표)이 이 경로를 참조하므로, STEP 6에서 "아직 없는 폴더이고 첫 리뷰 때 생긴다"고 한 줄 알린다.

### 기존 파일 병합 규칙

STEP 2에서 "병합"을 택한 경우에만 적용한다.

- 기존 내용을 살리되, **새 섹션과 내용이 겹치면 새 섹션으로 흡수하고 원문 쪽은 지운다.** 같은 규칙이 한 문서에 두 번 있으면 나중에 한쪽만 고쳐져서 어긋난다.
- 흡수한 항목은 STEP 6 보고에 "기존 X를 Y 섹션으로 옮겼다"고 적는다.
- 기존에만 있고 템플릿에 없는 규칙은 원문 그대로 살린다. 위치는 성격이 맞는 섹션 안으로.
- `README.md`가 이미 있으면 템플릿에서 "## 문서" 표만 떼어내 끝에 덧붙인다. 나머지 플레이스홀더(`{{STACK_SHORT_LIST}}` 등)는 쓰이지 않으므로 치환 대상이 아니다. 다만 `.env.example`이 있는데 기존 README에 환경 변수 안내가 없으면 그 사실을 STEP 6에 보고한다.

### 플레이스홀더 접미사 규칙

- `_OR_OMIT` — 값이 없으면 **그 줄이나 블록을 통째로 지운다.** 지운 뒤 앞뒤 빈 줄도 정리해서 연속 빈 줄이 2개 이상 남지 않게 한다. 값이 있으면 여러 줄이어도 된다.
- `_OR_NA` / `_OR_TBD` / `_OR_NONE` — 값이 없으면 접미사가 가리키는 기본 문구(`해당 없음` / `미정` / `없음`)를 넣는다. 지우지 않는다.
- 접미사 없음 — 반드시 값을 채운다.

### 치환표

| 플레이스홀더 | 채우는 값 |
| --- | --- |
| `{{PROJECT_NAME}}` | STEP 2에서 확인받은 실제 서비스명 |
| `{{PROJECT_ONE_LINER}}` | 한 줄 목적 |
| `{{PROJECT_SUMMARY_2_3_LINES}}` | 2~3줄 설명 + "무엇이 아닌지" 한 줄 |
| `{{WORDMARK_OR_NA}}` | 한글·영문 표기 규칙 |
| `{{USER_ROLE}}` | 예: `PO 겸 프론트엔드 개발자 (단독 프론트). 백엔드는 별도 팀원 담당` |
| `{{DATA_MODEL_ONE_LINE_OR_TBD}}` | 핵심 엔티티 관계 한 줄 |
| `{{STACK_LIST}}` | 감지한 스택을 `- 항목: 값 (버전 range)` 불릿으로. 순서는 프레임워크 / 언어·타입 설정 / 라우팅 / 스타일링 / 상태관리 / 네이티브·플랫폼 모듈 / 린트·테스트 / 패키지 매니저 / 빌드·배포 / 백엔드 |
| `{{STACK_SHORT_LIST}}` | README용. 위에서 프레임워크·언어·스타일링·백엔드 4~5줄만 추린 것. CLAUDE.md 전문을 그대로 복사하지 않는다 |
| `{{BACKEND_SPEC_NOTE_OR_OMIT}}` | 백엔드 명세 문서가 실제로 있을 때만. 인용 기호 `>` 를 포함해서 쓴다 |
| `{{COMMANDS_BLOCK}}` | **호출 명령 형태로** 쓴다. `next dev`가 아니라 `pnpm dev`. 감지한 패키지 매니저를 반영한다. 각 줄에 `# 설명 (원본 스크립트)` 주석. `package.json`에 없는 스크립트를 지어내지 않는다. 스크립트가 아닌 명령(`pnpm install`, `npx tsc --noEmit`)은 필요하면 넣되 `# 스크립트 아님` 주석을 단다 |
| `{{ENV_NOTE_OR_OMIT}}` | `.env.example`이 있을 때만. 환경 변수 파일 위치와 주요 변수의 용도를 2~3줄로. **값은 절대 적지 않는다.** 서버 전용 값과 클라이언트 노출 값의 구분이 있으면 그것도 명시 |
| `{{FOLDER_STRUCTURE_BLOCK}}` | **STEP 4가 끝난 뒤 상태 기준.** 이 스킬이 만드는 `docs/log/`, `.github/`, `.claude/local/`도 포함한다. 각 줄에 `# 역할` 주석. 빈 폴더나 빈 파일만 든 폴더는 그렇게 표시하고 역할을 지어내지 않는다 |
| `{{DESIGN_TOKEN_SECTION}}` | 색 / radius / 타이포 / 그림자 **네 항목을 각각** 처리한다. 실측값이 있는 항목은 값을 옮겨 적고, 없는 항목은 `미정. 확정 후 여기 기록` 이라고 쓴다. 하나라도 실측값이 있으면 첫 줄에 토큰 정의 위치와 사용 방식(className / style prop)을 명시한다. 네 항목이 전부 없으면 첫 줄 없이 섹션 전체를 `아직 미정. 토큰 확정 시 색·radius·타이포·그림자를 여기 기록한다. 그 전까지 하드코딩 색상 금지는 동일하게 적용한다.` 한 줄로만 채운다. 원본(Tokens Studio 등)에 있지만 코드로 안 옮긴 값이 있으면 "옮기지 않은 값은 사용 금지" 한 줄 추가 |
| `{{BRANCH_STRATEGY_LIST}}` | **감지한 실제 브랜치명**으로. `dev`가 있으면 3단(기본/dev/feature), 없으면 2단(기본/feature) |
| `{{INTEGRATION_BRANCH}}` | 실제 통합 브랜치명. `dev`가 있으면 `dev`, 없으면 감지한 기본 브랜치명 |
| `{{REVIEW_TARGET_PRS}}` | 모든 홉을 적는다. 3단이면 `` `feature/xxx` → `dev`, `dev` → `{기본 브랜치}` ``. `{기본 브랜치}`에는 감지한 실제 이름을 넣는다 |
| `{{VERIFY_COMMANDS_INLINE}}` | 타입체크와 린트 **둘 다**. 각각 `package.json`에 스크립트가 있으면 **감지한 패키지 매니저의 run 형태**(`npm run <이름>` / `pnpm <이름>` / `yarn <이름>`)를 쓰고, 없으면 직접 명령(`npx tsc --noEmit`)을 쓴다. `{{COMMANDS_BLOCK}}`과 표기가 어긋나면 안 된다. 테스트 스크립트가 있으면 그것도 포함 |
| `{{VERIFY_CHECK_LINES}}` | 위 명령들을 `- 이름 (\`명령\`) — PASS / FAIL` 줄로 |
| `{{VERIFY_CHECKBOX_LINES}}` | 위 명령들을 `- [ ] 이름 (\`명령\`)` 줄로 |
| `{{COMMIT_EXAMPLES_BLOCK}}` | 그 프로젝트에서 실제로 나올 법한 커밋 7개. 태그별 1개씩. 도메인 용어를 쓴다 |
| `{{BRANCH_PR_RULES_LIST}}` | 브랜치 전략을 불릿으로. 끝에 `- 브랜치 전략 원본은 \`CLAUDE.md\`` 한 줄 추가 |
| `{{CYCLE_EXAMPLES}}` | 그 프로젝트에서 나올 법한 사이클 이름 2개. 예: 앱이면 `"온보딩 구현", "그룹 초대 구현"` |
| `{{TEAM_REFERENCE_RULE}}` | 팀이면 `백엔드 담당은 "팀원"으로만 지칭한다` / 혼자면 `협업자가 생기면 "팀원"으로 지칭한다` |
| `{{CLICKABLE_ELEMENT_RULE}}` | 웹이면 `` 클릭 핸들러 달린 `div` (`button` 사용) `` / React Native면 `` `onPress` 달린 `View` (`Pressable` 사용) `` |
| `{{DESIGN_TOKEN_CHECKBOX_OR_OMIT}}` | 토큰이 정의돼 있을 때만 `- [ ] 디자인 토큰 사용 (하드코딩 색상 없음)`. 미정이면 줄 삭제 |
| `{{PR_VISUAL_SECTION_OR_OMIT}}` | UI가 있는 프로젝트면 `## 화면` 섹션. 모바일이면 iOS·Android 캡처 자리, 웹이면 before/after 캡처 자리. CLI·라이브러리처럼 화면이 없으면 섹션 삭제 |
| `{{EXTRA_CONVENTIONS_OR_OMIT}}` | 스택 특수 규칙. 예: Next.js면 Server/Client Component 경계와 `NEXT_PUBLIC_` 노출 금지, Expo면 Expo Router 파일 기반 라우팅 주의점 |
| `{{AUTOGEN_FILES_INLINE}}` | 그 스택에서 사람이 손대지 않는 자동 생성 파일. 예: `lockfile, expo-router 자동 라우트` / `lockfile, next-env.d.ts, 생성 타입` |
| `{{CONFIG_FILES_INLINE}}` | 실행 환경·신뢰 경계를 정의하는 설정 파일 경로를 백틱 목록으로. `.github/workflows/*.yml`은 항상 포함. 스택별로 `eas.json`, `app.config.*`, `next.config.*`, `vercel.json`, `Dockerfile`, `package.json` 중 실제로 있는 것 |
| `{{EXTRA_REVIEW_AREAS_OR_OMIT}}` | 플랫폼 특수 점검 영역을 불릿으로. **모바일이면 반드시 포함**: 네이티브 권한 처리, 플랫폼 분기(iOS/Android), safe area·키보드 회피, 리스트 렌더 성능. 웹이면 접근성(시맨틱 태그·키보드 포커스·색 대비), SSR/CSR 경계 |
| `{{EXTRA_REVIEW_AREAS_INLINE_OR_NONE}}` | 위 항목을 쉼표로 이은 한 줄 요약 |
| `{{INSTALL_AND_RUN_BLOCK}}` | 감지한 패키지 매니저로 설치 + 실행 명령 |
| `{{ENV_SECTION_OR_OMIT}}` | `.env.example`이 있으면 `## 환경 변수` 섹션과 변수 목록. 값은 적지 않는다 |
| `{{README_EXTRA_SECTIONS_OR_OMIT}}` | 배포 대상이 앱스토어면 `## 지원 환경`(iOS/Android 최소 버전), `## 스크린샷` 자리. 웹이면 배포 URL 자리 |

---

## STEP 5. 템플릿 손질

치환만으로 안 되는 부분이다. 배치 후 확인한다.

- `.claude/local/PR_REVIEW_RULES.md`의 "다른 프로젝트 사례" 표는 웹(Next.js + Tailwind v4) 프로젝트 기록이다. 이 프로젝트 스택이 다르면 섹션 제목 밑에 `현재 프로젝트는 <실제 스택>이라 사실 관계가 다르다.` 한 줄을 추가한다. 중괄호 없이 실제 값으로 쓴다.
- 리모트가 없는 로컬 전용 레포면 PR 템플릿과 PR 기반 리뷰 절차가 당장은 동작하지 않는다. 생성은 하되 STEP 6에서 "리모트 연결 후 동작한다"고 알린다.

---

## STEP 6. 보고

- 만든 파일을 커밋 대상 / 이그노어 대상으로 나눠 목록으로
- 기존 파일에서 흡수·이동한 내용
- "미정"으로 남긴 항목과, `_OR_OMIT`으로 삭제한 항목
- 디자인 토큰을 "미정"으로 남겼으면, 같은 플러그인의 `tokens` 스킬로 이어서 정리할 수 있다고 한 줄 알린다 (`/project-kickoff:tokens`). 이 스킬에서 토큰 작업을 직접 하지 않는다
- `.gitignore` 보완 제안 중 사용자가 아직 결정 안 한 것
- 커밋 제안. **두 커밋으로 나눈다.** 방금 만든 커밋 컨벤션이 "여러 변경 섞기 금지"라 한 커밋으로 묶으면 첫 커밋부터 자기 규칙을 어긴다

```
chore: gitignore에 Claude Code 로컬 경로 추가     # 기존 파일에 블록만 추가한 경우
chore: gitignore 추가                              # 새로 만든 경우
docs: 프로젝트 기본 문서 세트 추가
```

`.gitignore` 보완까지 했으면 그것도 chore 커밋에 포함된다.

실행 여부는 사용자에게 묻는다.

---

## 왜 이 배치인가

사용자가 위치를 물으면 이 근거로 답한다.

- **커밋하는 것은 계약이다.** `CLAUDE.md`, 커밋 컨벤션, 코드 리뷰 가이드는 그 레포에서 일하는 모두(사람이든 AI든)가 따라야 하는 규칙이라 레포에 있어야 한다. Claude Code 커뮤니티 관행도 프로젝트 내 `CLAUDE.md`와 `.claude/settings.json`은 커밋, `local`이 붙은 것만 이그노어다.
- **`.github/pull_request_template.md`는 선택지가 없다.** GitHub이 이 경로에서 읽어야 템플릿이 동작한다.
- **회고 로그(`docs/log/cycle-NN.md`)는 커밋한다.** 이그노어 폴더는 git 백업이 안 된다. 몇 달 뒤 꺼내 쓸 자산을 로컬에만 두면 PC가 날아갈 때 같이 날아간다. 결정 기록을 코드 옆에 커밋하는 건 ADR 관행과도 맞는다.
- **개인 메모는 분리한다.** 커밋되는 회고에는 솔직한 실패 기록을 못 쓴다. 그 부분만 `.claude/local/notes/`로 빼서 검열 압박을 없앤다.
- **리뷰 리포트는 PR 코멘트가 정본이다.** 브랜치마다 파일이 쌓이면 레포가 지저분해지고, 머지 후엔 다시 안 본다. PR에 붙이면 영구 트레일은 남고 레포는 깨끗하다.
- **`.claude/local/`로 한 곳에 모은다.** `.gitignore` 한 줄로 끝나고, `local` 네이밍이 Claude Code의 `settings.local.json` 규칙과 맞아서 나중에 봐도 의도가 읽힌다. `docs/` 밑에 숨기면 문서 트리에 커밋 대상과 비대상이 섞여 매번 헷갈린다.

---

## 하지 말 것

- 플레이스홀더를 남긴 채 파일 저장
- `package.json`을 안 읽고 버전·명령어를 추정해서 기입
- 없는 브랜치명(`main`)을 문서에 적기
- 없는 npm 스크립트를 명령어 섹션에 적기
- 기존 파일 덮어쓰기 (STEP 2 확인 없이)
- `.gitignore`보다 파일 생성을 먼저
- `git rm --cached` 를 확인 없이 실행
- 자동 커밋. 커밋은 제안만 하고 지시를 받는다
- 문서 만들면서 코드나 컴포넌트 스캐폴딩까지 진행. 이 스킬은 문서까지만 한다. `docs/log/`, `.claude/local/notes/` 같은 문서용 폴더 생성은 예외
