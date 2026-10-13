"""Opt-in domain routing for the completed, exposed-development experiments.

Routing never receives case IDs, references, scores or saved answers. The caller
builds its existing domain prompt from the returned context before applying the
message transform. Nothing here changes the production default.
"""
from newdomain.catalogue_counts import evidence
from newdomain.answer_focus import focus_messages
from newdomain.typed_boundaries import messages as boundary_messages


def select(corpus, question, baseline_context, aggregates):
    if corpus == 'niuhuang':
        return {'route': 'nh-focused-typed-v2', 'context': dict(baseline_context),
                'calculation_trace': {}}
    if corpus != 'guangming':
        raise ValueError('unsupported corpus')
    computed, trace = evidence(question, aggregates)
    if not computed:
        return {'route': 'gm-c1', 'context': dict(baseline_context),
                'calculation_trace': {}}
    # The measured route has one catalogue. Do not silently expand to an
    # untested multi-catalogue policy or crowd out all ordinary source evidence.
    if len(computed) != 1:
        raise ValueError('count route requires exactly one catalogue')
    if set(computed) & set(baseline_context):
        raise ValueError('derived/source identifier collision')
    return {'route': 'gm-c1-catalogue-counts',
            'context': {**computed, **dict(list(baseline_context.items())[:7])},
            'calculation_trace': trace}


def transform_messages(route, messages, templates=None):
    if route == 'nh-focused-typed-v2':
        if templates is None:
            raise ValueError('approved boundary templates required')
        return boundary_messages(focus_messages(messages), templates, 'citations')
    if route in ('gm-c1', 'gm-c1-catalogue-counts'):
        return messages
    raise ValueError('unsupported route')
