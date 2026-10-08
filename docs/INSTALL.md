# 환경별 설치

배포판 1.0.1 · 확인일 2026-10-08. 제품 메뉴와 설치 지원 범위는 계정·앱 버전·조직 정책에 따라 달라질 수 있습니다.

## GPT·Codex 통합 설치

1. 설치 기능을 지원하는 ChatGPT 데스크톱·Codex에 저장소 주소와 README의 설치 요청 문구를 전달합니다.
2. 명령을 직접 쓰는 경우 `codex plugin marketplace add wansucong-stoom/stoom-hrulesmcp --ref main`으로 출처를 등록합니다.
3. ChatGPT 데스크톱의 Plugins Directory에서 **한남대FLOW** 출처와 `hannam-regulations-gpt`를 찾아 설치합니다. 새 대화에서 플러그인과 스킬을 확인합니다.
4. 표시되는 연결 승인을 완료하고 아래 첫 질문으로 실제 도구 호출을 확인합니다.

ZIP을 사용하는 경우 `dist/stoom-hrules-gpt.zip`을 풀면 `hannam-regulations-gpt/plugin.json`, `mcp.json`, `skills/`가 나옵니다. 로컬 마켓플레이스의 `source.path`를 이 플러그인 폴더에 연결합니다. 다른 마켓플레이스 설정을 덮어쓰지 말고 기존 설정에 항목을 추가합니다.

플러그인 설치가 없는 환경에서 MCP를 지원하면 서버 이름 `hannam-regulations`, Streamable HTTP URL `https://h-rules.stoom.win/api/mcp`, 인증 없음으로 추가합니다. 스킬만 설치하려면 `dist/hannam-regulations-skill.zip`의 폴더 전체를 클라이언트의 사용자 스킬 경로에 넣습니다. 스킬 ZIP은 MCP 연결을 자동 생성하지 않습니다.

일반 ChatGPT 웹에는 GitHub 주소만으로 로컬 플러그인이 자동 설치된다고 안내하지 않습니다. 사용자 정의 MCP 기능이 있을 때 공개 서버를 추가하거나, 아래 GPTs Actions 경로를 사용합니다.

## 사용자 정의 GPTs

1. GPT 만들기 → Configure → Actions → Import from URL에 `https://h-rules.stoom.win/openapi.json`을 넣습니다. 인증은 None입니다.
2. GPT 통합 ZIP의 `gpts/instructions.md` 내용을 Instructions에 붙입니다. ZIP의 `gpts/openapi.json`은 배포 시점 사본이며, 최신 URL 가져오기를 우선합니다.
3. Actions의 `get_sync_status`, `search_regulations`를 시험하고 조문 조회를 확인합니다.

GPTs Actions 설정은 MCP·플러그인 설치와 다른 경로입니다. 스킬 ZIP을 Actions 스키마로 넣지 않습니다. 공개 GPT 배포 시 실제 개인정보 처리방침과 조직의 허용 도메인 설정을 확인합니다.

## Claude Code 통합 설치

터미널에서 다음을 실행합니다.

```sh
claude plugin marketplace add wansucong-stoom/stoom-hrulesmcp
claude plugin install hannam-regulations-claude@stoom-hrulesmcp
claude plugin list
```

설치 후 새 Claude Code 세션에서 `/mcp`로 연결을 확인합니다. 스킬은 `/hannam-regulations-claude:hannam-regulations`로 사용할 수 있습니다. 새 플러그인 반영을 요청하는 메시지가 나오면 그 안내를 따릅니다. 플러그인에 MCP와 스킬이 포함되므로 별도의 같은 서버·스킬을 중복 추가하지 않습니다.

ZIP은 풀어서 `claude --plugin-dir ./hannam-regulations-claude`로 해당 세션에서 사용할 수 있습니다. 영구 설치는 위 마켓플레이스 경로를 사용합니다. 플러그인을 쓸 수 없을 때의 개별 MCP 등록 명령은 다음과 같습니다.

```sh
claude mcp add --transport http --scope user hannam-regulations https://h-rules.stoom.win/api/mcp
```

## Claude 웹·Desktop·Cowork

1. Customize → Connectors → Add custom connector에서 이름 **한남대FLOW**와 URL `https://h-rules.stoom.win/api/mcp`를 추가합니다. 인증은 No sign in입니다. 조직 계정은 관리자가 먼저 커넥터를 허용해야 할 수 있습니다.
2. `dist/hannam-regulations-claude-skill.zip`을 받아 Customize → Skills → Create skill → Upload a skill에서 올리고 켭니다. 필요한 Code execution and file creation 기능도 허용합니다.
3. 새 대화에서 커넥터를 켜고 규정 질문을 보냅니다.

웹의 스킬 업로드에 `stoom-hrules-claude.zip` 통합 플러그인을 올리지 않습니다. 스킬과 커넥터는 각각 설정합니다. Claude Code 설치가 Claude 웹의 커넥터·스킬 설치까지 완료한다고 가정하지 않습니다.

## 첫 질문과 확인

> 연결한 한남대FLOW에서 학칙의 졸업 관련 조문을 찾아줘. 마지막 자료 확인 시각, 규정명, 조문 번호, 버전의 공식 표시일과 공식 원문 링크를 함께 알려줘.

실제 `get_sync_status` → `search_regulations` → `list_articles` → `get_article` 호출과 출처를 확인합니다. 설치됐다는 답변만으로 연결 성공을 판단하지 않습니다. 규정 DB 인증은 없지만 AI 서비스 자체의 계정과 사용 권한은 필요합니다.

## 업데이트·오류

Claude Code는 `claude plugin marketplace update stoom-hrulesmcp` 후 `claude plugin update hannam-regulations-claude@stoom-hrulesmcp`를 실행합니다. Codex 마켓플레이스는 `codex plugin marketplace upgrade stoom-hrulesmcp`로 새로고침하고 설치된 플러그인을 갱신합니다. ZIP 설치는 새 파일로 기존 설치를 갱신합니다. GPTs는 최신 Actions 스키마와 지침을 다시 가져옵니다.

규정 데이터는 질문 시 서버에서 조회합니다. 플러그인·스킬·GPT 지침 파일은 새 릴리스를 설치해야 바뀝니다. 오래된 Weki 해설은 현재 규정 조문·부칙과 비교합니다.

- 404: 서버 URL의 `/api/mcp`를 확인합니다.
- 401·OAuth 오류: 공개 서버와 기존 플랫폼 OAuth 주소를 혼용했는지 확인합니다.
- 메뉴 없음: 해당 제품의 기능과 조직 허용을 확인하고 지원되는 수동 경로를 사용합니다.
- 스킬만 보임: MCP가 실제로 연결됐는지 확인합니다.
- 접수 응답 `pending`: 검토 대기이며 게시 완료가 아닙니다.

## 공식 설정 자료

- [OpenAI 플러그인·마켓플레이스](https://developers.openai.com/plugins/build/plugins)
- [OpenAI MCP 연결](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Claude 마켓플레이스](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude MCP](https://code.claude.com/docs/en/mcp)
- [Claude 원격 커넥터](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Claude 스킬 업로드](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
