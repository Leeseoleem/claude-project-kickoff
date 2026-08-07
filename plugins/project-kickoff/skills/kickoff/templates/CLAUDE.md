# CLAUDE.md

{{PROJECT_NAME}} 작업 시 Claude Code가 따르는 프로젝트 규칙.

---

## 프로젝트 개요

{{PROJECT_SUMMARY_2_3_LINES}}

- 워드마크·표기: {{WORDMARK_OR_NA}}
- 역할: {{USER_ROLE}}
- 데이터 모델: {{DATA_MODEL_ONE_LINE_OR_TBD}}

---

## 기술 스택

{{STACK_LIST}}

> 버전은 package.json 기준. 이 문서와 실제가 다르면 package.json이 맞다.

{{BACKEND_SPEC_NOTE_OR_OMIT}}

---

## 명령어

```bash
{{COMMANDS_BLOCK}}
```

{{ENV_NOTE_OR_OMIT}}

---

## 폴더 구조

```
{{FOLDER_STRUCTURE_BLOCK}}
```

---

## 디자인 토큰

{{DESIGN_TOKEN_SECTION}}

---

## 작업 규칙

### 브랜치 전략
{{BRANCH_STRATEGY_LIST}}

### 커밋
- 형식: `태그: 설명` (50자 이내, 반말 문어체)
- 태그: feat / fix / refactor / style / chore / docs / test (7종, 신설 금지)
- 단계별로 커밋. 여러 변경 섞기 금지
- AI 트레일러·푸터 금지 (`Co-Authored-By`, `Generated with` 등)
- 상세: `docs/commit-convention.md`

### 코드 리뷰
- {{REVIEW_TARGET_PRS}} PR은 머지 전 리뷰 (5줄 이내·문서만 변경 등은 스킵 가능)
- 검증 명령: {{VERIFY_COMMANDS_INLINE}}
- 리포트: PR 코멘트에 남기고, 파일 사본은 `.claude/local/reviews/{브랜치명}.md` (이그노어)
- 상세: `docs/code-review.md`

### 코딩 컨벤션
- TypeScript strict 기준. `any` 지양, 불가피하면 주석으로 사유 명시
- 색상·간격 하드코딩 금지. 토큰·변수만 사용
- 데이터 필드 변경 시 렌더·모달 등 참조 지점도 함께 갱신
- 컴포넌트 PascalCase, 훅 `use` 접두, 유틸 camelCase. named export 기본 (프레임워크가 default export를 요구하는 라우트·페이지 파일은 예외)
{{EXTRA_CONVENTIONS_OR_OMIT}}

---

## 응답 규칙 (Claude Code)

- 한국어로 응답
- 이모지 사용 금지
- 커밋·주석·내부 문서는 반말 문어체. 외부 공유·제출 문서만 존댓말체
- 사람을 지칭할 때 이름·대명사를 쓰지 않는다. 사용자 본인은 "사용자", {{TEAM_REFERENCE_RULE}}
- 한 번에 하나의 화면·결정 단위로 작업. 명시한 범위를 넘어 앞서가지 않는다
- 큰 데이터 모델 변경은 명시적 요청이 있을 때만
- 코드 생략 금지. "...나머지 동일", "// 기존 코드 유지" 형태로 잘라내지 않는다

---

## 하지 말 것

- `any` 사용
- 색상·간격 하드코딩
- {{CLICKABLE_ELEMENT_RULE}}
- 요청 범위 밖 리팩토링
- 상의 없는 새 라이브러리 추가
- 검증 명령 실패 상태로 커밋

---

## 사이클 회고 프로세스

한 사이클(하나의 기능·화면 묶음 작업)이 끝나면 회고 로그를 남긴다.
다음 사이클에서 맥락을 빠르게 복원하고, 포트폴리오 작성 시 재료로 쓰기 위함이다.

### 사이클 단위
{{CYCLE_EXAMPLES}}처럼 의미 있는 작업 묶음 하나 = 한 사이클.
브랜치(feature) 하나가 대략 한 사이클에 대응한다.

### 작성 시점·위치
- 시점: 사이클의 마지막 PR을 `{{INTEGRATION_BRANCH}}`에 머지한 직후
- 회고: `docs/log/cycle-NN.md` (번호 2자리 순차, 커밋)
- 양식: `docs/log/TEMPLATE.md` 복사해서 작성
- 개인 메모: `.claude/local/notes/cycle-NN-note.md` (이그노어, 포폴 후보·솔직한 회고)

### 기록 항목
- 무엇을 했는지 (구현·결정 요약)
- 왜 그렇게 정했는지 (주요 결정과 근거)
- 막혔던 점과 해결 (트러블슈팅)
- 다음 사이클 메모 (보류 항목, 이어서 할 것)

### decision-backlog
사이클 중 보류한 항목은 `docs/log/decision-backlog.md`에 누적한다.
회고의 "다음 사이클 메모"와 함께 후속 작업의 진입점이 된다.

---

## 로컬 전용 문서 (이그노어)

`.claude/local/`은 `.gitignore` 대상이다. 레포에 올리지 않는다.

| 경로 | 내용 |
| --- | --- |
| `.claude/local/PR_REVIEW_RULES.md` | PR 봇 리뷰를 어떻게 판단·브리핑할지에 대한 개인 작업 규칙 |
| `.claude/local/reviews/{브랜치명}.md` | 코드 리뷰 리포트 사본 (정본은 PR 코멘트). 첫 리뷰 때 폴더가 생긴다 |
| `.claude/local/notes/cycle-NN-note.md` | 사이클 개인 메모, 포폴 후보 (양식: 같은 폴더의 `cycle-note-TEMPLATE.md`) |

Claude Code는 이 폴더의 문서도 프로젝트 규칙으로 함께 읽는다.
