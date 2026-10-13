"""Opt-in generic condition-consistency prompt, independently written.

This is prompting, not verified symbolic execution or a learned verifier.
No per-question thresholds, reference answers or source-specific rules enter it.
"""
INSTRUCTION = (
 '在写结论前先核对问题前提与条件的逻辑关系，再输出原有JSON。'
 '先确定所问对象和条款，优先采用该条款括号明确的含本数或不含本数；否则采用同一政策中适用的定义，不挪用其他政策或对象的定义。'
 '对上限或下限，把文字关系转成大小比较再代入：下限含本数用大于或等于，不含本数用严格大于；上限含本数用小于或等于，不含本数用严格小于。'
 '明确已发生与要求未发生相冲突；明确未发生与要求未发生一致；没有说明不是已发生，也不是未发生。'
 '并列条件须逐项判断，问题仅问局部条件则只给局部结论；不得把原文条件误当成问题对象已具备的事实。'
 '最终逐句检查：首句结论必须与引用的定义、题设事实及后续解释一致，不能先判不符合又解释其实符合。证据不足时不要猜测。'
 '仍只输出原有最多3句、每句160字、证据句柄JSON，不输出内部核对过程。'
)


def add_predicate_instruction(messages):
    if not messages or messages[0]['role']!='system':raise ValueError('system message required')
    out=[dict(m) for m in messages];out[0]['content']+=INSTRUCTION;return out
