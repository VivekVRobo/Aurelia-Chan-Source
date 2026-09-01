import requests
import json
from integrated_backend import app

client = app.test_client()

# Test 1: Weak/lazy resume (must NOT give fake praise or high score)
res1 = client.post('/api/resume-audit', json={'resume': 'I worked at a company. I did coding and managed some people. I am a hard worker.'})
data1 = res1.get_json()
print('=== WEAK RESUME TEST ===')
print(f"Score: {data1['score']} (Expression: {data1['expression']})")
print(f"Recommendation: {data1['recommendation']}")
assert data1['score'] <= 60, f"Expected score <= 60, got {data1['score']}"
assert data1['expression'] in ['warning', 'disappointed', 'analyzing']

# Test 2: Strong Executive resume (must score high)
res2 = client.post('/api/resume-audit', json={'resume': 'VP of Engineering. Spearheaded global cloud migration across 4 regions ($25M budget), scaling engineering organization from 45 to 180 members. Delivered 42% latency reduction and accelerated ARR growth by $38M over 24 months.'})
data2 = res2.get_json()
print('\n=== STRONG RESUME TEST ===')
print(f"Score: {data2['score']} (Expression: {data2['expression']})")
print(f"Recommendation: {data2['recommendation']}")
assert data2['score'] >= 85, f"Expected score >= 85, got {data2['score']}"
assert data2['expression'] == 'approval'

# Test 3: Entitled/weak interview answer (must NOT give fake praise)
res3 = client.post('/api/interview-evaluate', json={'response': 'I deserve more money because living costs are high and my boss is unfair.', 'scenario': 'Salary'})
data3 = res3.get_json()
print('\n=== ENTITLED INTERVIEW TEST ===')
print(f"Score: {data3['score']} (Expression: {data3['expression']})")
print(f"Feedback: {data3['feedback']}")
assert data3['score'] <= 55, f"Expected score <= 55, got {data3['score']}"
assert data3['expression'] in ['warning', 'skeptical']

# Test 4: Strong STAR interview answer
res4 = client.post('/api/interview-evaluate', json={'response': 'I acknowledge the fiscal constraints directly, but present 75th-percentile market data demonstrating that my target package aligns with expected gross margin expansion. I propose a structured 6-month performance review tied to quantifiable revenue milestones.', 'scenario': 'Salary'})
data4 = res4.get_json()
print('\n=== STRONG INTERVIEW TEST ===')
print(f"Score: {data4['score']} (Expression: {data4['expression']})")
print(f"Feedback: {data4['feedback']}")
assert data4['score'] >= 85, f"Expected score >= 85, got {data4['score']}"
assert data4['expression'] == 'confident'

# Test 5: Chat Endpoint - Promotion inquiry
res5 = client.post('/api/chat', json={'message': 'How do I get a promotion?'})
data5 = res5.get_json()
print('\n=== CHAT PROMOTION TEST ===')
print(f"Response snippet: {data5['response'][:140]}...")
print(f"Expression: {data5['expression']}")
assert 'promotion' in data5['response'].lower() and 'de-risked' in data5['response'].lower()

print('\n>>> ALL HIGH-RIGOR EXECUTIVE INTELLIGENCE TESTS PASSED PERFECTLY! <<<')
