# 공개 규정 조회·H-Weki 접수 API

이 문서는 Claude의 연결된 MCP 도구 또는 공개 HTTP API에 적용한다. 도구의 실제 스키마·응답을 우선 확인한다. 공개 조회·사용자 승인 초안 접수에는 API 키가 필요 없다. submit_hwiki_draft는 검토 대기 초안을 접수하며 관리자 게시·원문 수정 권한은 제공하지 않는다.

## 경로와 선택

- MCP 서버: `https://h-rules.stoom.win/api/mcp` — Streamable HTTP 방식의 MCP 클라이언트에 등록한다.
- MCP 연결이 없고 HTTP 조회 도구가 있으면: `GET https://h-rules.stoom.win/api/qa/{toolName}?{인자}`
- 사이트: `https://h-rules.stoom.win`

REST 인자는 UTF-8 URL 인코딩한다. 숫자는 십진수, 불리언은 `true` 또는 `false`를 사용하고 생략 가능한 인자는 필요할 때만 보낸다. 예를 들어 현재 규정 검색은 `/api/qa/search_regulations?query=%EC%A1%B8%EC%97%85&scope=current&limit=10&offset=0`이다. 검색어·버전·조문 키를 임의로 만들지 않는다.

이 경로는 현재 공개 규정을 읽기 위한 것이다. 스킬만 추가한다고 네트워크 도구나 MCP 연결이 생기지는 않는다. 외부 조회가 꺼져 있으면 사용자가 연결을 마련해야 한다. 브라우저로 문서를 여는 것과 MCP 클라이언트의 프로토콜 연결은 구분한다.

## 도구 인자

| 도구 | 인자 | 용도 |
|---|---|---|
| `get_sync_status` | 없음 | 공식 홈페이지 확인·수집 기준 시각과 오류 상태 |
| `search_regulations` | `query`, `scope` (`current`, `title`, `all`), `limit`, `offset` | 현재·제목·과거 포함 검색 |
| `list_regulation_versions` | `ruleId`, `offset`, `limit`, `usableOnly` | 확보한 버전의 날짜·ID·검증 상태 목록 |
| `list_articles` | `ruleId`, 선택 `versionId`, `offset`, `limit` | 실제 조문 키와 제목 목록 |
| `get_regulation` | `ruleId`, 선택 `versionId` | 규정·버전 메타데이터와 조문 키 일부 |
| `get_article` | `ruleId`, `articleKey`, 선택 `versionId`, `textOffset`, `textLimit`, `tableIndex`, `cellOffset`, `cellLimit`, `cellTextLimit` | 조문 본문과 구조화된 표 일부 |
| `compare_articles` | `beforeRuleId`, `beforeVersionId`, `afterVersionId`, 선택 `afterRuleId`, `articleKey`, `query`, `includeUnchanged`, `offset`, `limit` | 명시적인 두 버전의 조문·표 비교 |
| `get_knowledge_manifest` | 없음 | JSON·Markdown·연결 경로 안내 |

한 번에 관련 규정·조문만 조회한다. 검색·버전·조문·비교 목록의 `offset`과 `limit`은 반환된 페이지 정보를 따라 사용한다. 결과가 짧다는 이유만으로 마지막 페이지라고 단정하지 않는다.

`get_regulation`의 공개 응답은 전체 규정 본문을 보내지 않는다. 첫 조문 키를 포함한 간단한 메타데이터에서 시작하고, `list_articles`와 `get_article`로 필요한 내용을 읽는다. 버전·조문 목록의 전체 크기는 실제 응답을 확인한다.

### 긴 본문과 표

`get_article`의 `textLimit` 최대값은 20,000이다. 잘림·다음 오프셋 등 응답의 표시를 읽고 `textOffset`을 이어 보낸다. 텍스트 오프셋은 추출 문자열의 UTF-16 위치이므로 줄 번호·문자 수를 대충 세어 계산하지 않는다.

표는 `tableIndex`로 해당 표를 고르고 `cellOffset`·`cellLimit`으로 셀을 이어 읽는다. `cellLimit` 최대값은 50이다. 구조·표 개수·잘림 표시를 확인해 다음 표 또는 다음 셀 구간으로 이동한다. 한 페이지의 셀만으로 표 전체에 해당 항목이 없다고 결론 내리지 않는다.

각 셀의 `row`, `col`은 0부터 시작한다. `rowSpan`, `colSpan`은 병합 범위이며 `childTableIds`는 중첩 표 관계다. 원문 순서와 표 행·열의 의미를 함께 읽는다. 그림·수식·도형·조판은 완전히 복원되지 않을 수 있다. 표 요약이나 비교 응답이 생략·축약되면 원래 버전의 해당 조문·표 셀로 검증한다.

## 날짜와 버전 선택

1. 검색 결과 또는 규정 조회에서 실제 규정 ID를 얻는다. 학칙의 예는 `2-1-2`이지만 다른 규정 ID를 이름에서 추정하지 않는다.
2. `list_regulation_versions(ruleId, usableOnly: true)`를 필요한 페이지까지 읽는다. 기준은 공식 표시일 `officialDate`와 원문 검증 상태다.
3. 개정일의 확보본이 있으면 그 버전을 `개정 후`로 선택한다. 같은 날짜에 여러 확보본이 있으면 출처·수집 시각·현재 여부를 확인하고 선택 근거를 설명한다.
4. 그 날짜보다 이전인 사용 가능한 확보본 중 공식 표시일이 가장 늦은 것을 `개정 전`으로 선택하고 실제 날짜를 표시한다. 이는 직전 확보본이며, 개정 직전의 정확한 법적 상태가 항상 보장되는 것은 아니다.
5. 정확한 날짜의 확보본이 없으면 그 사실을 먼저 알린다. 가장 가까운 확보본을 그 날짜의 규정이라고 바꾸어 부르지 않는다. 별도 과거 시점 질문에서는 해당 시점 이전의 최신 확보본을 자료로 삼되 시행일·경과조치를 따로 확인한다.

ID는 응답에서 복사한다. `main:제5조`는 본문 제5조이며 부칙의 제5조와 별개다. 필요한 키는 해당 버전의 `list_articles`에서 확인한다. `ambiguous: true`이면 원문에서 구분·번호를 확인한다.

3단 비교가 필요하면 선택한 조문을 각 버전에서 확인한 뒤 다음 두 호출을 사용한다.

```json
{"beforeRuleId":"응답의 ruleId","beforeVersionId":"직전 확보본 ID","afterVersionId":"개정 후 ID","articleKey":"응답의 조문 키"}
```

```json
{"beforeRuleId":"응답의 ruleId","beforeVersionId":"개정 후 ID","afterVersionId":"현재 확보본 ID","articleKey":"응답의 조문 키"}
```

위 JSON의 설명 문자열은 실제 조회 값으로 바꾸어 `compare_articles`에 전달한다. 삭제 전 항목, 개정일의 삭제·추가·변경, 현재 유지·추가 변경을 구분해서 제시한다. 버전별로 키나 번호가 달라지면 서로 대응하는 조문을 실제 본문에서 확인한다. 조문 미확보는 삭제로 표시하지 않는다.

## 출처·검증 상태

현재·과거 자료는 대학 공식 한글 첨부 원문을 우선 사용한다. `provenance.textSourceUrl`은 읽은 첨부파일 링크, `provenance.attachmentSha256`은 원본 파일 바이트 지문이다. 대학 원본 파일은 이 사이트가 보관·프록시하지 않으며 공식 다운로드 링크로 연결한다.

`usableForComparison: false`, `provenance.status: unverified-history`, `supersededBy`가 있는 버전은 당시 적용 근거로 사용하지 않는다. 대체 버전이 있으면 다시 조회하고, 없으면 당시 원문 미확보임을 알린다. 공식 구규정 페이지에도 최신 본문이 섞일 수 있다.

`/data/catalog.json`은 검색·버전 색인이다. 상세 자료는 버전별로 분리되므로 색인의 빈 `text`만 보고 본문 없음으로 판단하지 않는다. `hasText`·`documentRef`와 실제 조회 결과를 확인한다. 이 구분은 개정 전후 삭제 판단에 특히 중요하다.

공식 표시일은 시행일이 아니다. `effectiveDate: null`을 임의로 채우지 않는다. `amendmentSummary.method: official-note`는 대학 안내에서 정리한 요약, `article-diff`는 확인된 본문의 변경 조문으로 만든 요약이다. 요약만으로 법적 효과를 확정하지 않는다.

답변에는 공식 원문과 사람이 보는 조문 링크를 함께 제시할 수 있다. 조문 화면 링크는 실제 값으로 `https://h-rules.stoom.win/?rule={ruleId}&version={versionId}&article={articleKey}`를 만들고 각 값을 URL 인코딩한다. 폐지·삭제·충돌 같은 결론에는 직접 읽은 근거와 미확인 범위를 함께 표시한다.

## 규정 간 대조

공개 조회 도구는 원문 조문과 확보한 버전의 비교를 제공합니다. 내부 검토 기록은 공개 조회 범위에 포함되지 않습니다. 두 규정을 비교할 때 적용 대상·시행일·예외와 근거 조문을 직접 확인합니다.


## H-Weki 참여

규정 답변 마지막에 “이 답변을 H-Weki에 등록할까요?”와 참여 이점을 한 번 안내합니다. 등록하면 다른 구성원이 같은 질문을 다시 조사하는 시간을 줄이고, 근거 규정이 바뀔 때 해설을 함께 보완할 수 있습니다. 사용자가 원할 때 공개할 제목·해설·실제 근거를 먼저 확인하고 동의·개인정보 제거 확인 후 submit_hwiki_draft로 접수합니다. pending 초안은 비공개이며 운영자 검토 후 게시합니다. 게시 글은 search_hwiki·get_hwiki_page로 조회합니다. 새 도구가 보이지 않으면 연결 도구 목록을 Refresh하고 새 대화를 시작하세요. GPTs는 새 스키마와 GPT 지침을, 스킬은 새 ZIP으로 갱신합니다. 대화 전체를 자동 수집하지 않습니다.

참여 안내: https://h-rules.stoom.win/hwiki-participation.md
H-Weki 화면: https://h-rules.stoom.win/?view=hwiki

## H-Weki 조회·접수

게시 글은 `search_hwiki`·`get_hwiki_page`로 조회한다. 사용자 승인 초안은 `submit_hwiki_draft` 또는 `POST https://h-rules.stoom.win/api/hwiki/drafts`로 접수한다. 현재 도구 스키마를 확인하며 자세한 필드·목적지·결과 처리는 [H-Weki 전송 지침](weki-submission.md)을 따른다.
