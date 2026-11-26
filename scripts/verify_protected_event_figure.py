"""The user explicitly froze the historical event-types PDF and PNG."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'figures/generated/event_signatures.pdf':'a85d23376f5f94c6956502553f424b5800ad66d262a0f042b579b1af6052c80d',
          'figures/generated/event_signatures.png':'8e8d78d043f68a154a64e588a28b638c7d6d3b3e1c7e03f1d3a866c33e3928da'}
def verify():
    for name,expected in EXPECTED.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Protected event-types image was modified: '+name)
    print('PROTECTED_EVENT_TYPES_FIGURE_UNCHANGED')
if __name__=='__main__':verify()
