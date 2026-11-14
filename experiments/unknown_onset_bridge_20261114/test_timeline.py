import pandas as pd
from audit_p07_timeline import audit

def test_timeline():
    df=pd.DataFrame([
        dict(record_id='A',episode_id=1,off_true=5,off_emitted=5.4,compress_time=6,next_on_true=9,number_histories_at_next_on=1,number_distinct_old_causes_at_next_on=1,trace_discarded_amplitude=.1,trace_discarded_between=.5),
        dict(record_id='B',episode_id=1,off_true=5,off_emitted=5.4,compress_time=12,next_on_true=9,number_histories_at_next_on=3,number_distinct_old_causes_at_next_on=2,trace_discarded_amplitude=.2,trace_discarded_between=.6)
    ])
    a=audit(df)
    assert a['fraction_compressed_before_next_on']==.5
    assert a['n_with_multiple_old_causes_at_next_on']==1
    print('PASS timeline validator and post-hoc quantities')
if __name__=='__main__':test_timeline()
