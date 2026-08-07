# project-kickoff

프로젝트 시작 시 필요한 문서 세트를 **프로젝트 스펙에 맞게 가공해서** 배치하는 Claude Code 플러그인.

템플릿을 그대로 복사하지 않는다. `package.json`, `tsconfig`, `app.json`, `tailwind.config`, 실제 브랜치명, git remote를 읽어서 스택·버전·명령어·폴더 구조·디자인 토큰을 감지하고, 감지로 알 수 없는 것만 물어본 뒤 채운다.

깃허브에 올리면 안 되는 문서는 `.claude/local/`로 분리하고 `.gitignore`까지 설정한다.

---

## 설치

```
/plugin marketplace add Leeseoleem/claude-project-kickoff
/plugin install project-kickoff@leeseoleem-plugins
```

터미널에서 하려면 `claude plugin marketplace add ...` 형태로 쓴다.

## 사용

아무 프로젝트에서 아래처럼 말하면 스킬이 걸린다.

```
프로젝트 세팅해줘
레포 세팅하자
CLAUDE.md 만들어줘
```

직접 부르려면 `/project-kickoff:kickoff`.

---

## 만드는 것

### 커밋 대상

| 경로 | 내용 |
| --- | --- |
| `CLAUDE.md` | 프로젝트 규칙. 스택·명령어·폴더 구조·디자인 토큰·브랜치 전략·응답 규칙 |
| `docs/commit-convention.md` | 커밋 컨벤션 (7종 태그, AI 트레일러 금지 포함) |
| `docs/code-review.md` | 코드 리뷰 절차. Critical/Major/Minor/Note/Positive 5단 분류와 리포트 양식 |
| `docs/log/TEMPLATE.md` | 사이클 회고 양식 |
| `docs/log/decision-backlog.md` | 보류 항목 누적 문서 |
| `.github/pull_request_template.md` | PR 템플릿 |
| `README.md` | 소개, 실행 방법, 문서 인덱스 |

### 이그노어 대상 (`.claude/local/`)

| 경로 | 내용 |
| --- | --- |
| `PR_REVIEW_RULES.md` | PR 봇 리뷰를 어떻게 판단·브리핑할지에 대한 개인 규칙 |
| `notes/cycle-note-TEMPLATE.md` | 사이클 개인 메모 양식. 포폴 후보, 솔직한 회고 |
| `reviews/` | 코드 리뷰 리포트 사본 (첫 리뷰 때 생성) |

`.gitignore`에 `.claude/local/` 한 줄이 추가된다.

---

## 왜 이렇게 나눴나

**커밋하는 것은 계약이다.** `CLAUDE.md`, 커밋 컨벤션, 코드 리뷰 가이드는 그 레포에서 일하는 모두(사람이든 AI든)가 따라야 하는 규칙이라 레포에 있어야 한다.

**`.github/pull_request_template.md`는 선택지가 없다.** GitHub이 이 경로에서 읽어야 템플릿이 동작한다.

**회고 로그는 커밋한다.** 이그노어 폴더는 git 백업이 안 된다. 몇 달 뒤 포트폴리오 쓸 때 꺼낼 자산을 로컬에만 두면 PC가 날아갈 때 같이 날아간다. 결정 기록을 코드 옆에 커밋하는 건 ADR 관행과도 맞는다.

**개인 메모는 분리한다.** 커밋되는 회고에는 솔직한 실패 기록을 못 쓴다. 그 부분만 `.claude/local/notes/`로 빼서 검열 압박을 없앤다.

**리뷰 리포트는 PR 코멘트가 정본이다.** 브랜치마다 파일이 쌓이면 레포가 지저분해지고 머지 후엔 다시 안 본다. PR에 붙이면 영구 트레일은 남고 레포는 깨끗하다.

**`.claude/local/`로 한 곳에 모은다.** `.gitignore` 한 줄로 끝나고, `local` 네이밍이 Claude Code의 `settings.local.json` 규칙과 맞아서 나중에 봐도 의도가 읽힌다.

---

## 동작 순서

1. **현황 파악** — 기존 파일 존재 여부 + 스펙 감지. 이 단계에서는 아무것도 쓰지 않는다
2. **확인 + 질문** — 감지 결과를 표로 보여주고, 알 수 없는 것만 한 메시지에 묶어 물어본다
3. **`.gitignore` 먼저** — 파일보다 먼저 손댄다. 순서가 반대면 그 사이 `git add -A`에 이그노어 대상이 딸려 들어간다
4. **파일 생성** — 플레이스홀더 32개를 전부 치환. 하나라도 남으면 실패
5. **템플릿 손질** — 스택이 다른 참고 자료에 단서 추가
6. **보고** — 미정 항목, 삭제한 섹션, 커밋 제안 2개. 커밋은 실행하지 않는다

기존 파일은 절대 덮어쓰지 않는다. 파일 단위로 새로 만들지 / 병합할지 / 건너뛸지 물어본다.

---

## 커스터마이즈

템플릿을 고치려면 `plugins/project-kickoff/skills/kickoff/templates/` 를 수정하고 푸시한 뒤, Claude Code에서 `/plugin` → 업데이트.

`plugin.json`의 `version`을 올려야 업데이트가 인식된다. `version`을 지우면 commit SHA 기준으로 자동 갱신된다.

플레이스홀더를 추가하면 `SKILL.md`의 치환표에도 반드시 같이 넣어야 한다. 표에 없는 플레이스홀더는 치환되지 않고 그대로 남는다.

---

## 레포 구조

```
.claude-plugin/
  marketplace.json                    # 마켓플레이스 정의
plugins/
  project-kickoff/
    .claude-plugin/
      plugin.json                     # 플러그인 정의
    skills/
      kickoff/
        SKILL.md                      # 절차, 감지 규칙, 치환표
        templates/                    # 문서 템플릿 9개
```

## 라이선스

MIT
