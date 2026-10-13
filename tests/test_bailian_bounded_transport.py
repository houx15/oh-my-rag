import json,unittest
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
from newdomain.bailian_bounded_transport import BailianStreamTransport,ENDPOINT_TEMPLATE,MODEL
from newdomain.transport import LiveAuthorizationError
from eval.optimization.transports import TransportError

class BailianAdapterTest(unittest.TestCase):
    def ctx(self):return SimpleNamespace(_check_prior=lambda:None,manifest=SimpleNamespace(_raw={'provider_route':{'endpoint_template':ENDPOINT_TEMPLATE,'model':MODEL,'credential_environment_name':'DASHSCOPE_SEARCH_API_KEY'}}))
    def test_denies_missing_or_wrong_authority_before_credentials(self):
        a=BailianStreamTransport(model=MODEL)
        with patch.object(a,'_load_credentials')as c:
            with self.assertRaises(LiveAuthorizationError):a.call('chat',{})
            a.authorize(SimpleNamespace(_check_prior=lambda:None,manifest=SimpleNamespace(_raw={})))
            with self.assertRaises(LiveAuthorizationError):a.call('chat',{})
            c.assert_not_called()
    def test_request_and_observed_provenance(self):
        a=BailianStreamTransport(model=MODEL);a.authorize(self.ctx());response=MagicMock();response.status_code=200
        event={'model':MODEL,'id':'fake-response','choices':[{'delta':{'content':'{"ok":true}'},'finish_reason':'stop'}],'usage':{'prompt_tokens':12,'completion_tokens':5}}
        response.iter_lines.return_value=['data: '+json.dumps(event),'data: [DONE]'];session=MagicMock();session.post.return_value.__enter__.return_value=response
        with patch.object(a,'_load_credentials',return_value={'DASHSCOPE_SEARCH_API_KEY':'dummy','BAILIAN_WORKSPACE_ID':'test-workspace'}),patch('requests.Session',return_value=session):
            r=a.call('chat',{'messages':[{'role':'system','content':'JSON'},{'role':'user','content':'test'}]})
        self.assertEqual(r['actual_model'],MODEL);self.assertEqual(r['provider'],'Alibaba Cloud Bailian');self.assertTrue(r['stream_done'])
        args,kw=session.post.call_args;self.assertEqual(args[0],ENDPOINT_TEMPLATE.format(workspace='test-workspace'));self.assertFalse(kw['allow_redirects']);self.assertFalse(kw['json']['enable_thinking']);self.assertEqual(kw['json']['max_tokens'],800)
    def test_http_failure_not_answer(self):
        a=BailianStreamTransport(model=MODEL);a.authorize(self.ctx());response=MagicMock();response.status_code=401;session=MagicMock();session.post.return_value.__enter__.return_value=response
        with patch.object(a,'_load_credentials',return_value={'DASHSCOPE_SEARCH_API_KEY':'dummy','BAILIAN_WORKSPACE_ID':'test-workspace'}),patch('requests.Session',return_value=session),self.assertRaisesRegex(TransportError,'401'):
            a.call('chat',{'messages':[{'role':'system','content':'JSON'},{'role':'user','content':'test'}]})

    def test_bounded_request_streams_usage_and_retains_user_budget(self):
        a=BailianStreamTransport(model=MODEL);self.assertEqual(a.timeout,120)
        with self.assertRaises(ValueError):BailianStreamTransport(model=MODEL,request_timeout_s=121)
        with self.assertRaises(ValueError):BailianStreamTransport(model=MODEL,max_output_tokens=801)

    def test_soft_deadline_not_hidden_by_late_success(self):
        from newdomain.bailian_bounded_transport import BailianDeadlineTransport
        ctx=SimpleNamespace(manifest_path='m',redaction_names_path='d');transport=BailianDeadlineTransport(ctx);called=[];transport.on_soft_deadline=lambda:called.append(True)
        receive,send,process=MagicMock(),MagicMock(),MagicMock();receive.poll.side_effect=[False,True];receive.recv.return_value={'ok':True,'response':{'content':'{}'}};process.is_alive.return_value=False
        mp=MagicMock();mp.Pipe.return_value=(receive,send);mp.Process.return_value=process
        with patch('newdomain.bailian_bounded_transport.multiprocessing.get_context',return_value=mp),patch('newdomain.bailian_bounded_transport.time.perf_counter',side_effect=[0,20,24]):
            r=transport.call('chat',{'messages':[]})
        self.assertEqual(called,[True]);self.assertTrue(r['latency_budget_exceeded']);self.assertEqual(r['application_transport_ms'],24000);self.assertEqual(receive.poll.call_args_list[1].args,(105,))

    def test_hard_deadline_cleans_up_child(self):
        from newdomain.bailian_bounded_transport import BailianDeadlineTransport
        ctx=SimpleNamespace(manifest_path='m',redaction_names_path='d');transport=BailianDeadlineTransport(ctx)
        receive,send,process=MagicMock(),MagicMock(),MagicMock();receive.poll.side_effect=[False,False];process.is_alive.side_effect=[True,False]
        mp=MagicMock();mp.Pipe.return_value=(receive,send);mp.Process.return_value=process
        with patch('newdomain.bailian_bounded_transport.multiprocessing.get_context',return_value=mp),patch('newdomain.bailian_bounded_transport.time.perf_counter',side_effect=[0,20]),self.assertRaisesRegex(TransportError,'hard125s'):
            transport.call('chat',{'messages':[]})
        process.terminate.assert_called_once();receive.close.assert_called_once()
