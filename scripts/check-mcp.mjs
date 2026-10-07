// Read-only integration check: never call draft submission or administrator tools.
import assert from 'node:assert/strict';
const endpoint = 'https://h-rules.stoom.win/api/mcp';
let id = 0, session, protocol = '2025-03-26';
async function rpc(method, params) {
  const headers = {'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':protocol};
  if (session) headers['Mcp-Session-Id'] = session;
  const response = await fetch(endpoint, {method:'POST', headers, body:JSON.stringify({jsonrpc:'2.0',id:++id,method,params}), signal:AbortSignal.timeout(20000)});
  assert.equal(response.status, 200, `${method}: HTTP ${response.status}`);
  session = response.headers.get('Mcp-Session-Id') || session;
  const raw = await response.text();
  const data = response.headers.get('content-type')?.includes('text/event-stream')
    ? JSON.parse(raw.split('\n').find(line=>line.startsWith('data:')).slice(5).trim()) : JSON.parse(raw);
  assert(!data.error, `${method}: RPC error`);
  assert(!data.result?.isError, `${method}: tool error`);
  return data.result;
}
function toolData(result) {
  return result.structuredContent || JSON.parse(result.content.find(item=>item.type === 'text').text);
}
const init = await rpc('initialize', {protocolVersion:protocol,capabilities:{},clientInfo:{name:'stoom-distribution-check',version:'1.0.0'}});
protocol = init.protocolVersion;
const listing = await rpc('tools/list', {});
assert.equal(listing.tools.length, 11);
assert(!listing.tools.some(tool=>tool.name.includes('admin') || tool.name.includes('conflict')));
const draft = listing.tools.find(tool=>tool.name === 'submit_hwiki_draft');
assert(draft.inputSchema.required.includes('consentToShare'));
assert(draft.inputSchema.required.includes('personalDataRemoved'));
await rpc('tools/call', {name:'get_sync_status',arguments:{}});
await rpc('tools/call', {name:'search_regulations',arguments:{query:'졸업',scope:'current',limit:3}});
const articles = toolData(await rpc('tools/call', {name:'list_articles',arguments:{ruleId:'2-1-2',limit:5}}));
const key = articles.articles?.[0]?.key;
assert(key, 'No actual article key returned');
const article = toolData(await rpc('tools/call', {name:'get_article',arguments:{ruleId:'2-1-2',articleKey:key}}));
assert(article.text?.length || article.article?.text?.length, 'No article text returned');
console.log(JSON.stringify({endpoint,protocol,toolCount:listing.tools.length,readOnlyProbe:true,ruleId:'2-1-2',articleKey:key,articleTextVerified:true}));
