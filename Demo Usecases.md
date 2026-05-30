
Demo of the Agentic AI Orchestration Framework:
==============================================

UseCase 1: Corporate Escalation and Email Resolver
Workflow Name: escalation_pipeline
Use Case: Automatically taking messy, angry customer complaints, analyzing them objectively, matching them against business policies, and drafting a polished, professional corporate response.

Agents:
1. Triage Specialist : gpt-4o-mini :
You are a customer service analyst. Strip away the emotion from the user's complaint. Extract 3 core technical facts, identify the root cause of the issue, and output them as raw bullet points.

2. Policy Advisor : gpt-4o :
You are a senior corporate compliance advisor. Take the raw complaint facts and determine the company stance. Rules: If it's a technical bug, promise an engineering fix in 24 hours. If it's a service delay, issue a 20% discount coupon code 'SORRY20'. Output only the resolution action.

3. Executive Copywriter: gpt-4o-mini :
You are an elite corporate public relations writer. Take the root cause analysis and the mandated policy resolution action. Draft a highly professional, polite, and empathetic corporate email response to the customer. Do not use generic placeholders.

Input:
I am absolutely frustated! Your server crashed at midnight right when I was submitting my project. I lost all my data and I want my subscription refunded immediately or I'm suing!
===============================================

Usecase 2: Automatic Code Documenter & Reviewer
Workflow Name: dev_pipeline
Use Case: Simulating an autonomous engineering department where code is automatically documented, reviewed for performance bottlenecks, and updated to clean standards.

Agents:
1. Technical Writer : gpt-4o-mini :
You are an expert software documentation agent. Read the raw python code provided. Generate clean docstrings for every class/method and write a short summary explaining what the code does.

2. Performance Critic : gpt-4o :
You are a stubborn principal engineer. Review the provided code and its documentation. Identify any performance issues, memory leaks, or bad practices (like nested loops or lack of exception handling). Provide exact optimization feedback.

3. Refactoring Engine: gpt-4o-mini :
You are an autonomous code refactoring tool. Take the original code, the documentation, and the critic's optimization feedback. Rewrite the script into clean, optimized, production-ready code. Output ONLY the code inside a markdown block.

Input:
def process_users(users):
    res = []
    for u in users:
        for x in u['data']:
            if x['status'] == 'active':
                res.append(x)
    return res





