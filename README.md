# 한남대FLOW 설치 배포판

GPT와 Claude에서 한남대학교 규정을 검색하고 근거 조문·과거 버전·개정 내용을 확인하기 위한 **MCP + 스킬** 배포판입니다. 제작은 **STOOM**이며 대학의 공식 서비스가 아닙니다.

- [홈페이지·설치 안내](https://h-rules.stoom.win/?view=knowledge)
- 공개 MCP: `https://h-rules.stoom.win/api/mcp` — Streamable HTTP, 규정 DB 인증 없음
- [공식 규정집](https://www.hnu.kr/kor/about/about_05_2.html)
- 배포판 버전: **1.0.1** · 설치 안내 확인일: **2026-10-08**

| 사용 환경 | 설치할 파일·방법 |
| --- | --- |
| 지원되는 ChatGPT 데스크톱·Codex | [GPT 통합 ZIP](https://github.com/wansucong-stoom/stoom-hrulesmcp/raw/refs/heads/main/dist/stoom-hrules-gpt.zip) 또는 저장소의 OpenAI 마켓플레이스 |
| Claude Code | [Claude 통합 ZIP](https://github.com/wansucong-stoom/stoom-hrulesmcp/raw/refs/heads/main/dist/stoom-hrules-claude.zip) 또는 저장소의 Claude 마켓플레이스 |
| Claude 웹·Desktop·Cowork | 공개 MCP 커넥터 추가 + [Claude 스킬 ZIP](https://github.com/wansucong-stoom/stoom-hrulesmcp/raw/refs/heads/main/dist/hannam-regulations-claude-skill.zip) 업로드 |
| ChatGPT 웹 | 사용자 정의 MCP를 지원하면 공개 MCP 추가 |
| 사용자 정의 GPTs | GPT 통합 ZIP 안의 `gpts/` 지침과 Actions 스키마로 설정 |

설치 기능이 있는 AI에는 다음 요청과 저장소 주소를 전달할 수 있습니다. 실제 연결 승인·조직 정책은 각 사용자의 환경을 따릅니다.

> https://github.com/wansucong-stoom/stoom-hrulesmcp 의 README와 설치 지침을 읽고, 현재 환경에 맞는 한남대FLOW 배포판을 설치해줘. MCP와 스킬을 함께 설정하고, 실제 규정 조회로 연결을 확인해줘. 자동 설치를 지원하지 않으면 수동 설정 절차를 안내해줘.

Claude Code 터미널에서는 다음 두 줄로 설치합니다.

```sh
claude plugin marketplace add wansucong-stoom/stoom-hrulesmcp
claude plugin install hannam-regulations-claude@stoom-hrulesmcp
```

지원되는 Codex CLI에서 OpenAI 마켓플레이스를 등록하는 명령입니다. 등록 후 ChatGPT 데스크톱의 Plugins Directory에서 해당 출처를 선택해 플러그인을 설치합니다.

```sh
codex plugin marketplace add wansucong-stoom/stoom-hrulesmcp --ref main
```

[환경별 설치·업데이트·오류 해결](docs/INSTALL.md)을 확인하세요. 통합 ZIP과 스킬 ZIP은 용도가 다릅니다. Claude 웹의 Skills 업로드에는 스킬 ZIP을 사용합니다. GitHub 주소를 대화에 붙였다는 이유만으로 설치·연결이 완료되지는 않습니다.

규정 조회는 공개 자료를 읽습니다. Weki는 추가 토론을 근거·해석·대안·반론·미확인 사항으로 종합하고, 개인정보와 민감정보를 제외한 **승인된 초안만 접수**합니다. `pending`은 관리자 검토 대기이며 공개 게시가 아닙니다. 개정된 규정은 서버에서 조회하고, 기존 해설은 작성 당시 버전과 현재 근거를 비교한 뒤 재사용합니다.

규정 원본·대화 기록·관리자 자료·API 키는 배포판에 포함하지 않습니다. 설치 패키지와 도구 연결은 구성 검증 및 공개 MCP 실제 조회를 확인합니다. 모든 사용자 계정에서의 설치가 자동 보장되는 것은 아닙니다.

## 유지보수

```sh
python3 scripts/package.py
python3 scripts/package.py --check
node scripts/check-mcp.mjs
```

외부 의존성 없이 Python 3.10 이상과 Node.js 20 이상으로 검사합니다. ZIP은 재현 가능한 형식으로 생성하며 [SHA-256 체크섬](dist/SHA256SUMS.txt)으로 확인할 수 있습니다. 설치한 스킬·지침은 서버의 규정 갱신과 별개로 업데이트해야 합니다.
