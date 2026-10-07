# H-Weki 전송 목적지와 접수 절차

이 문서는 사용자가 승인한 규정 해설을 한남대학교 규정 DB와 같은 서비스의 H-Weki 저장층으로 보내기 위한 지침이다. DB에 직접 접속하지 않고 서버가 제공하는 접수 API를 사용한다.

## 목적지

| 용도 | 주소·방법 |
| --- | --- |
| 기존 ChatGPT·Codex 플랫폼 연결 | `https://hannam-regulations-wiki.esceeee.chatgpt.site/mcp`의 `submit_hwiki_draft` |
| Claude 등 외부 MCP 연결 | `https://h-rules.stoom.win/api/mcp`의 `submit_hwiki_draft` |
| GPTs Actions 명세 | `https://h-rules.stoom.win/openapi.json`의 `submit_hwiki_draft` operation |
| MCP 없이 HTTP 제출 | `POST https://h-rules.stoom.win/api/hwiki/drafts`, `Content-Type: application/json` |
| 기존 아티클 검색·조회 | `search_hwiki`, `get_hwiki_page` |
| 실제 연결 정보·현재 명세 | `GET https://h-rules.stoom.win/api/mcp-info`, `GET https://h-rules.stoom.win/openapi.json` |
| 사람이 보는 H-Weki | `https://h-rules.stoom.win/?view=hwiki` |

공개 접수 API는 인증 없이 승인된 초안을 받는다. 플랫폼 연결은 기존 OAuth를 유지한다. 접수는 비공개 검토 대기이며 공개 게시·원문 변경·관리자 심사를 대신하지 않는다. `/mcp`는 REST 접수 주소가 아니다. `GET /api/qa/{toolName}`은 읽기용이며 쓰기에 사용하지 않는다.

이미 연결된 도구를 우선 사용하고 같은 초안을 MCP와 HTTP로 이중 전송하지 않는다. 일반 웹 검색·페이지 열람 도구만 있는 환경에서는 POST할 수 있다고 가정하지 않는다. 연결이나 쓰기 도구가 없으면 공개용 초안을 제공하고 아직 접수되지 않았다고 설명한다.

## 제출 데이터

매번 현재 MCP `inputSchema` 또는 OpenAPI `POST /api/hwiki/drafts`의 requestBody를 확인한다. 로컬 구현·설치본·운영 서버의 기능이 다를 수 있다. 최신 스키마가 허용하는 항목과 길이 제한을 따른다.

기본 필수 항목은 다음과 같다.

| 항목 | 전달 값 |
| --- | --- |
| `requestId` | 이번 공개 초안용 UUID. 응답 불명·재시도에도 같은 값과 같은 내용을 사용 |
| `title` | 공개할 제목, 최대 140자 |
| `summary` | 공개 요약, 최대 800자 |
| `body` | 공개할 해설 Markdown, 최대 16000자. 전체 채팅·개인정보·미공개 사례 제외 |
| `references` | 직접 조회한 `{ruleId, versionId, articleKey}` 1~12개. ID나 버전을 추측하지 않음 |
| `consentToShare` | 사용자가 공개할 내용을 승인한 경우에만 `true` |
| `personalDataRemoved` | 공개 초안의 개인정보·미공개 사례 제거를 확인한 경우에만 `true` |

기본 선택 항목은 `topic`(최대 60자)과 `basis`(`current` 또는 `historical`)이다. 서버가 근거의 실제 존재를 검증하고 출처·지문을 기록하므로 references 객체에 임의의 URL·설명·개인 정보를 추가하지 않는다.

현재 스키마가 지원할 때 사용하는 확장 항목:

- `relatedPageId`, `relatedPageRevision`: `get_hwiki_page`에서 실제 읽은 기존 글 ID·revision. 수정 충돌을 방지하기 위해 함께 전달한다.
- `contributionType`: 새 글은 `article`, 기존 글 수정 제안은 `correction`, 다른 해석은 `opinion`. correction·opinion에는 기존 글 연결이 필요하다. 기존 글을 직접 덮어쓰지 않는다.
- `classificationPath`: 선택적 탐색 분류. 대·중·소로 고정하지 않고 현재 스키마의 배열 제한을 따른다. 글의 고유 ID와 관계를 분류와 혼동하지 않는다.

이 확장 항목이 명세에 없으면 전송하지 않는다. 기본 `topic`·본문으로 새 글을 접수할 수 있지만, 기존 글 수정·의견 연결이 필요한 요청은 그 관계를 잃은 새 글로 바꾸어 제출하지 않는다. 공개할 보완안을 준비해 두고 해당 기능이 아직 연결에서 제공되지 않는다고 안내한다. 사용자 동의 없이 수정·의견을 새 글로 바꾸지 않는다.

게시된 실제 글을 연결할 경우 본문에 `[[문서ID|표시이름]]` 또는 `[표시이름](https://h-rules.stoom.win/?view=hwiki&wiki=문서ID)`를 사용할 수 있다. 지원되는 Markdown 렌더러·관계 조회 기능은 현재 서버의 응답으로 확인하며 존재하지 않는 글 ID를 생성하지 않는다.

## 처리 흐름과 결과

관련 글과 근거 규정을 읽고 → 공개할 초안을 사용자에게 보여주고 → 공개 동의·정보 제거를 확인한 뒤 → 허용된 항목으로 한 번 제출한다. 초안 준비 요청과 공개 제출 승인을 구분한다. 이미 보여준 초안에 대한 명시적인 등록 승인은 다시 요구하지 않는다.

응답에서 `draftId`와 `status`를 확인해 “초안 접수 / 관리자 검토 대기”로 안내한다. `published`·상태를 보지 않고 공개되었다고 말하지 않는다. 오류·응답 불명에서는 접수 성공을 추측하지 않는다. 응답이 불명확해 같은 요청을 재시도할 때 ID와 내용을 유지한다.

400 입력·근거 오류는 내용을 확인한다. 403 동의·권한 오류는 승인이나 권한을 임의로 채워 재시도하지 않는다. 409는 같은 요청 ID의 내용 불일치 또는 현재 스키마가 지원하는 기존 글 revision 충돌일 수 있으므로 오류 본문을 읽는다. revision이 바뀌었으면 글을 다시 읽어 보완안이 여전히 타당한지 확인하고 공개 내용이 달라졌을 때 사용자 승인을 갱신한다.

## 생성 모델 기록

H-Weki 초안을 제출할 때 현재 도구 스키마가 `generation`을 지원하면 확인 가능한 생성 정보를 함께 보낸다. `model`에는 실행환경·API가 제공한 실제 모델 식별자를 사용하고, `provider`, `client`, `modelVersion`은 확인한 값만 기록한다. 세부 버전·스냅샷을 알 수 없으면 해당 항목을 생략한다. 서비스 이름이나 모델 자신의 추측으로 버전을 만들어 넣지 않는다.

`source`는 실행환경 메타데이터가 있으면 `runtime-metadata`, 사용자가 생성 당시 표시를 확인해 알려준 경우 `user-reported`이다. 기록할 모델 정보가 없으면 generation 전체를 생략한다. 서버는 이를 제공받은 정보로 보관하며 실행 모델을 직접 인증하지 않는다. `verification`은 서버가 `reported-only`로 설정한다. API 키·계정 ID·대화 ID·프롬프트·실행 로그는 전송하지 않는다.

공개할 초안을 보여줄 때 생성 정보를 함께 표시한다. 관리자는 같은 정보를 검토하고, 게시 글과 수정본별 생성 기록에도 보존한다. 기존 글의 생성 정보를 새 수정본에 그대로 복사하지 않는다. 사람이 사이트에서 수정 제안을 작성했다면 AI 생성 모델을 임의로 붙이지 않는다. 모델 정보는 근거 규정·버전·조문과 검토 상태를 함께 살펴보는 작성 출처이다.


## 내용에 따른 글타래 성장과 모델 기록

등록 전 `search_hwiki`의 `organizationStructure`와 관련 `get_hwiki_page` 본문을 읽고, 새 글의 중심 쟁점·보완·다른 관점·독립 주제를 의미에 따라 판단한다. 근거 규정명이나 소관 부서를 곧바로 분류로 사용하지 않는다. 현재 스키마가 제공하는 `organization`에 실제 구조 revision·읽은 기존 글 ID/revision·주제 범위·통합/세분화·글 관계와 이유를 전달한다. 글 게시와 구조 반영은 관리자 검토 뒤 같은 트랜잭션으로 처리되며 원래 글의 내용·ID·모델 이력은 보존한다. 서버가 단어만으로 의미를 추정하거나 별도 LLM을 자동 호출한다고 표현하지 않는다.

`generation`에는 실제 확인 가능한 생성 모델을 함께 보낸다. 기존 글의 생성 모델과 이번 글타래 판단 모델을 혼동하거나 미기록 모델을 추정해서 채우지 않는다. 서버는 전달받은 모델 정보를 미검증으로 표시한다. 오래된 도구 명세에 `generation`·`organization` 인자가 없으면 지원되는 H-Weki-Metadata 본문 끝 JSON 형식으로 전달할 수 있다. 형식·현재 스키마·예시는 [글타래와 모델 기록](https://h-rules.stoom.win/weki-organization.md)을 확인한다. 본문 자체는 16,000자 이내이며 메타정보는 서버가 본문과 분리해 검증·저장한다. 누락 경고가 있으면 정보가 저장됐다고 주장하지 않는다.
