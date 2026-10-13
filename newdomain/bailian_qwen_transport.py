"""Existing pay-as-you-go Bailian route; default-deny and ledger-gated.
No Token Plan traffic, credential writes, redirects, or automatic retries.
"""
import json,time,multiprocessing,re
from pathlib import Path
from typing import Optional,Dict
from newdomain.transport import LiveContext,LiveAuthorizationError,screen
from eval.optimization.transports import TransportError,DispatchGate
from eval.optimization.budget import chat_conservative_estimates
_REPO=Path(__file__).resolve().parent.parent
ENDPOINT_TEMPLATE='https://{workspace}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL='qwen3.8-flash'
LEDGER_MODEL='bailian-qwen3.8-flash'
class BailianStreamTransport:
    """Streaming HTTP adapter. Default-deny: requires a LiveContext to call."""

    def __init__(self, *, model: str, request_timeout_s: float = 45,
                 max_output_tokens: int = 800, thinking: bool = False,
                 temperature: float = 0.2):
        if model != "qwen3.8-flash":
            raise ValueError("Unapproved model")
        if not 1 <= max_output_tokens <= 800:
            raise ValueError("Output bound")
        if not 1 <= request_timeout_s <= 60:
            raise ValueError("Request deadline bound")
        self.model = model
        self.timeout = request_timeout_s
        self.max_output = max_output_tokens
        self.thinking = thinking
        self.temperature = temperature
        self._live_context: Optional[LiveContext] = None

    def authorize(self, ctx: LiveContext) -> None:
        """Explicitly attach live authorization context."""
        self._live_context = ctx

    def _load_credentials(self) -> Dict[str, str]:
        v = {}
        env_file = _REPO / ".env.local"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, x = line.split("=", 1)
                    if k.strip() in ("DASHSCOPE_SEARCH_API_KEY", "BAILIAN_WORKSPACE_ID"):
                        v[k.strip()] = x.strip().strip("\"'")
        return v

    def call(self, kind: str, payload: dict) -> dict:
        if self._live_context is None:
            raise LiveAuthorizationError(
                "BailianStreamTransport.call requires explicit live context "
                "(construct via CLI --live; this is default-deny)")
        self._live_context._check_prior()
        route=self._live_context.manifest._raw.get('provider_route',{})
        if route.get('endpoint_template')!=ENDPOINT_TEMPLATE or route.get('model')!=MODEL or route.get('credential_environment_name')!='DASHSCOPE_SEARCH_API_KEY':
            raise LiveAuthorizationError('Bailian provider route mismatch')
        if kind != "chat":
            raise TransportError("Adapter only supports chat")
        messages = payload.get("messages")
        if not isinstance(messages, list) or len(messages) != 2:
            raise TransportError("Exactly two text messages required")
        for m in messages:
            if set(m) != {"role", "content"} or not isinstance(m["content"], str):
                raise TransportError("Invalid text message")
        if [m["role"] for m in messages] != ["system", "user"]:
            raise TransportError("Message roles invalid")
        request_bytes = len(json.dumps(messages, ensure_ascii=False).encode())
        if request_bytes > 30000:
            raise TransportError("Context byte cap exceeded before API request")

        v = self._load_credentials()
        if not v.get("DASHSCOPE_SEARCH_API_KEY"):
            raise TransportError("Existing credential unavailable")

        workspace=v.get('BAILIAN_WORKSPACE_ID','')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,62}',workspace):raise TransportError('existing workspace unavailable')
        endpoint=ENDPOINT_TEMPLATE.format(workspace=workspace)
        import requests
        body = {"model": self.model, "messages": messages, "max_tokens": self.max_output,
                "temperature": self.temperature,
                "enable_thinking": self.thinking,
                "stream": True, "stream_options": {"include_usage": True},
                "response_format": {"type": "json_object"}}
        start = time.perf_counter()
        first_content = first_reasoning = usage = finish = actual = rid = None
        content = []
        done = False
        session = requests.Session()
        try:
            with session.post(endpoint,
                              headers={"Authorization": "Bearer " + v["DASHSCOPE_SEARCH_API_KEY"]},
                              json=body, stream=True, allow_redirects=False,
                              timeout=(5, self.timeout)) as response:
                if response.status_code != 200:
                    raise TransportError("Bailian HTTP " + str(response.status_code))
                response.encoding = "utf-8"
                for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                    now = time.perf_counter()
                    if now - start > self.timeout:
                        raise TransportError("Generation total deadline exceeded; usage may be unknown")
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        done = True
                        break
                    event = json.loads(data)
                    actual = event.get("model", actual)
                    rid = event.get("id", rid)
                    if event.get("usage") is not None:
                        usage = event["usage"]
                    for choice in event.get("choices", []):
                        delta = choice.get("delta", {})
                        if delta.get("reasoning_content") and first_reasoning is None:
                            first_reasoning = now
                        if delta.get("content"):
                            if first_content is None:
                                first_content = now
                                cb = getattr(self, "on_first_content", None)
                                if cb:
                                    cb()
                            content.append(delta["content"])
                        if choice.get("finish_reason") is not None:
                            finish = choice["finish_reason"]
        except requests.RequestException as e:
            raise TransportError("Bailian transport " + type(e).__name__ + "; usage may be unknown") from None
        except (ValueError, TypeError, KeyError):
            raise TransportError("Malformed stream; usage may be unknown") from None
        finally:
            session.close()
        end = time.perf_counter()
        parsed_usage = None
        if (isinstance(usage, dict) and type(usage.get("prompt_tokens")) is int
                and type(usage.get("completion_tokens")) is int):
            parsed_usage = {"input_tokens": usage["prompt_tokens"],
                            "output_tokens": usage["completion_tokens"]}
        return {"provider":"Alibaba Cloud Bailian", "endpoint_template":ENDPOINT_TEMPLATE, "billing":"pay-as-you-go", "content": "".join(content), "usage": parsed_usage, "provider_usage": usage,
                "requested_model": self.model, "actual_model": actual, "response_id": rid,
                "finish_reason": finish, "stream_done": done,
                "request_input_bytes": request_bytes, "thinking": self.thinking,
                "events_perfcounter": {"first_reasoning_token": first_reasoning,
                                        "first_content_token": first_content,
                                        "full_response": end},
                "timings": {"request_start_monotonic": start,
                            "first_content_monotonic": first_content,
                            "first_reasoning_monotonic": first_reasoning,
                            "response_end_monotonic": end,
                            "ttft_ms": None if first_content is None else (first_content - start) * 1000,
                            "full_ms": (end - start) * 1000},
                "notes": "No reasoning text persisted. TTFT measures first content delta, not a verified complete answer."}



def _worker(pipe,config,messages):
    try:
        ctx=LiveContext(manifest_path=Path(config['manifest']),redaction_names_path=Path(config['denylist']),stage='final')
        route=ctx.manifest._raw.get('provider_route',{})
        if route.get('endpoint_template')!=ENDPOINT_TEMPLATE or route.get('model')!=MODEL or route.get('credential_environment_name')!='DASHSCOPE_SEARCH_API_KEY':raise LiveAuthorizationError('Bailian provider route mismatch')
        adapter=BailianStreamTransport(model=MODEL);adapter.authorize(ctx)
        pipe.send({'ok':True,'response':adapter.call('chat',{'messages':messages})})
    except Exception as e:pipe.send({'ok':False,'error':type(e).__name__+':'+str(e)})
    finally:pipe.close()

class BailianDeadlineTransport:
    def __init__(self,ctx):self.ctx=ctx
    def call(self,kind,payload):
        if kind!='chat':raise TransportError('chat only')
        config={'manifest':str(self.ctx.manifest_path),'denylist':str(self.ctx.redaction_names_path)}
        mp=multiprocessing.get_context('spawn');receive,send=mp.Pipe(duplex=False);p=mp.Process(target=_worker,args=(send,config,payload['messages']));p.start();send.close()
        try:
            if not receive.poll(55):raise TransportError('Bailian hard deadline; usage unknown')
            try:r=receive.recv()
            except EOFError:raise TransportError('Bailian child exited; usage unknown')from None
            if not r['ok']:raise TransportError(r['error'])
            return r['response']
        finally:
            receive.close()
            if p.is_alive():p.terminate()
            p.join(timeout=2)
            if p.is_alive():p.kill();p.join()

class _ContinuationLedger:
    """Count an explicitly resumed failed attempt as a retry, without auto loops."""
    def __init__(self,ledger):self.ledger=ledger
    def reserve(self,*args,**kwargs):
        kwargs['is_retry']=True
        return self.ledger.reserve(*args,**kwargs)
    def __getattr__(self,name):return getattr(self.ledger,name)

def chat(ctx,messages,*,resumed_attempt=False):
    ctx._check_prior()
    policy_path=ctx.manifest._raw.get('public_source_policy_path')
    if policy_path:
        from newdomain.institution_fields import screen_approved_institutions
        screen_approved_institutions(messages,ctx.redaction_names_path,json.loads(Path(policy_path).read_text()))
    else:screen(messages,ctx.redaction_names_path)
    route=ctx.manifest._raw.get('provider_route',{})
    if route.get('endpoint_template')!=ENDPOINT_TEMPLATE or route.get('model')!=MODEL:raise LiveAuthorizationError('Bailian route not authorized')
    i,o=chat_conservative_estimates(ctx.manifest,LEDGER_MODEL)
    return DispatchGate(BailianDeadlineTransport(ctx),_ContinuationLedger(ctx.ledger)if resumed_attempt else ctx.ledger,ctx.manifest,simulated=False).dispatch(kind='chat',payload={'messages':messages},model=LEDGER_MODEL,est_input_tokens=i,est_output_tokens=o)
