export H_TNEW=5.2 H_APRIOR=0.3,0.6 H_ACLIP=0.8
cd "$(dirname "$0")"
python exp1_history.py 3000 3200 1.5 100 1 0.4 test_E1 > results/E1.log 2>&1
python exp1_history.py 3000 3200 0.5 1000 0.5 0.4 test_E2 > results/E2.log 2>&1
