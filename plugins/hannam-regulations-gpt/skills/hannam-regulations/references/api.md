# 도구와 데이터

MCP 도구: `get_sync_status`, `search_regulations`, `list_regulation_versions`, `list_articles`, `get_regulation`, `get_article`, `compare_articles`, `get_knowledge_manifest`.

검색에는 `query`, `scope` (`current`, `title`, `all`), `limit`을 사용한다. 검색 결과의 `ruleId`, `versionId`, `articles[].key`로 근거를 조회한다. 예: 학칙 규정 ID는 `2-1-2`. 버전 ID는 조회 결과에서 복사하고 날짜에서 생성하지 않는다.

조문 조회 인자: `ruleId`, `articleKey`, 선택적인 `versionId`.

개정 비교 인자: `beforeRuleId`, `beforeVersionId`, `afterVersionId`, 선택적인 `afterRuleId`, `articleKey`, `query`, `includeUnchanged`, `offset`, `limit`.

원문 스키마는 `hannam-regulations/2`이다. 규정 ID, 공식 원문 URL, 공식 표시일, 원문 SHA-256 지문, 추출 방식과 수집 시각을 보관한다. `articles`는 원문 문자열의 UTF-16 시작·끝 오프셋이다. 조문 조회 API에서는 이 오프셋에 해당하는 `text`를 함께 반환한다. `main:제1조`는 본문 제1조이며 부칙의 제1조와 별개다. `ambiguous: true`는 조문 구분·번호 확인이 필요한 자료다.

현재·과거 모두 공식 한글 첨부 원문을 우선 사용한다. `provenance.textSourceUrl`은 본문을 읽은 첨부파일 링크, `provenance.attachmentSha256`은 파일 바이트의 SHA-256이다. 기존 `sourceHash`는 추출 본문·버전 메타데이터의 식별 지문이다. 첨부파일은 저장·프록시하지 않는다.

`usableForComparison: false`, `provenance.status: unverified-history`, `supersededBy`가 있는 보존본은 과거 적용 근거로 사용하지 않는다. 공식 구규정 페이지의 HTML이나 첨부파일에 현재 내용이 섞일 수 있다. `supersededBy`가 있으면 그 버전을 다시 조회하고, 없으면 당시 원문이 확인되지 않았다고 설명한다. 본문 미확보는 규정이나 조문의 부재를 뜻하지 않는다.

`document`의 `schemaVersion: hnu-document/1`에는 블록 순서와 표의 `rows`, `cols`, `cells`가 있다. 각 셀은 0부터 시작하는 `row`, `col`, `rowSpan`, `colSpan`, `text`, `childTableIds`를 가진다. 셀 안 블록·중첩 표를 함께 보존한다. 조문 조회 응답의 `tables`는 그 조문에 해당하는 표만 담는다. `document.warnings`와 그림·원문 확인 표시를 읽고 복원이 불완전한 도형·수식·조판을 확정된 내용으로 추론하지 않는다.

`compare_articles`의 `tableComparison`은 같은 조문·별표에서 표 순서와 셀 위치를 기준으로 비교한다. 표 이동·행열 삽입의 의미적 대응을 보장하지 않는다. `amendmentSummary.method`가 `official-note`이면 대학의 개정 안내를 짧게 정리한 것이고, `article-diff`이면 확인된 원문의 변경 조문으로 만든 요약이다.

`/data/catalog.json`은 검색·버전 색인이다. 상세 본문·표는 버전별로 분리되며 `get_regulation`, `get_article`, JSON·Markdown API가 필요한 상세 자료를 함께 반환한다. 색인의 빈 `text`만 보고 과거 본문이 없다고 판단하지 말고 `hasText`·`documentRef`를 확인한다.

`get_knowledge_manifest`가 실제 API·Markdown 경로를 반환한다. 비공개 사이트에서는 브라우저 로그인, MCP OAuth 또는 플랫폼이 발급한 서버용 서비스 접근이 필요하다. 스킬 파일·일반 링크·MCP 주소는 접근 권한을 부여하지 않는다.

사람의 검토 상태: `pending` (검토 대기), `confirmed` (상충 확인), `different-scope` (적용 범위 다름), `resolved` (해소됨). 자동 스캐너는 `missing-reference`, `numeric-difference` 후보만 생성한다. 의미 분석 전체를 대체하지 않는다.

## 공개 연결·GPTs 경로

공개 규정 조회·H-Weki 초안 접수 MCP: https://h-rules.stoom.win/api/mcp. 기존 플랫폼 OAuth MCP는 https://hannam-regulations-wiki.esceeee.chatgpt.site/mcp 이다. h-rules.stoom.win/mcp 주소는 사용하지 않는다.

공개 MCP의 규정 조회 도구와 GET /api/qa/{toolName}은 공개 자료를 읽는다. submit_hwiki_draft만 사용자 동의 후 초안을 접수하며 관리자 게시·자료 수정 도구는 제공하지 않는다. get_regulation은 메타데이터와 첫 50개 조문 키, get_knowledge_manifest는 경로 요약을 반환한다. list_regulation_versions(ruleId, offset, limit, usableOnly)와 list_articles(ruleId, versionId, offset, limit)의 nextOffset을 따른다.

get_article의 textPagination.nextOffset으로 textOffset을 이어 보내고 textLimit은 최대 20000이다. tables의 tableIndex를 고른 뒤 selectedTable.cellPagination.nextOffset으로 cellOffset을 이어 조회한다. cellLimit 최대 50, cellTextLimit 최대 4000이다. textTruncated가 참인 셀은 전체 본문 페이지 또는 공식 원문에서 확인한다. 공개 compare_articles의 긴 텍스트는 textTruncated로, 표는 summary-only로 표시되므로 원문 조문 조회로 검증한다.

GPTs의 Actions에는 https://h-rules.stoom.win/openapi.json 을 가져오고, instructions에는 사이트의 /gpts-instructions.md를 사용한다. SKILL ZIP 업로드가 Actions 연결을 대신하지 않는다. 자세한 사람용 설정 안내는 /?view=knowledge 및 /connection-guide.md에 있다.

## H-Weki 조회·접수

게시 글은 `search_hwiki`·`get_hwiki_page`로 조회한다. 사용자 승인 초안은 `submit_hwiki_draft` 또는 `POST https://h-rules.stoom.win/api/hwiki/drafts`로 접수한다. 현재 도구 스키마를 확인하며 자세한 필드·목적지·결과 처리는 [H-Weki 전송 지침](weki-submission.md)을 따른다.
