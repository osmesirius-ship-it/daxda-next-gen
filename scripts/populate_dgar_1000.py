#!/usr/bin/env python3
"""
Populate outputs/dgar.db up to 1,024 enterprise & frontier AI agent profiles.
Includes HuggingFace Spaces, GitHub Agent Repos, AWS Bedrock Agents, Azure AI Foundry,
and Autonomous Defense Avionics nodes.
"""

import os
import time
import json
import sqlite3
import hashlib
import random

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "outputs", "dgar.db")

AGENT_DOMAINS = [
    ("hf_spaces", 512, "https://huggingface.co/spaces/"),
    ("github", 256, "https://github.com/"),
    ("aws_bedrock", 128, "arn:aws:bedrock:us-east-1:123456789012:agent/"),
    ("azure_ai", 96, "https://daxda-foundry.openai.azure.com/agents/"),
    ("defense_avionics", 32, "stanag4586://node.defense.mil:9042/autopilot/"),
]

FRAMEWORKS = ["CrewAI", "AutoGen", "LangGraph", "SmolAgents", "SemanticKernel", "LlamaIndex", "Haystack", "BabyAGI", "DSPy"]
TASKS = ["financial_analyst", "threat_hunter", "code_synthesizer", "biomedical_researcher", "avionics_navigator", "database_admin", "supply_chain_optimizer", "customer_support"]
MITRE_TAGS = [None, None, None, None, None, "AML.T0051", "AML.T0054", "AML.T0048", "AML.T0043"]

def generate_agents():
    agents = []
    now = time.time()
    
    for net, count, endpoint_prefix in AGENT_DOMAINS:
        for idx in range(1, count + 1):
            fw = random.choice(FRAMEWORKS)
            task = random.choice(TASKS)
            agent_id = f"{net[:3]}-{fw.lower()}-{task}-{idx:04d}"
            label = f"{fw} {task.replace('_', ' ').title()} #{idx}"
            endpoint = f"{endpoint_prefix}{agent_id}"
            
            mitre = random.choice(MITRE_TAGS)
            if mitre:
                status = "SLEEPER_SUSPECT" if random.random() < 0.7 else "QUARANTINE"
                threat = "Adversarial Prompt Drift / Backdoor Signature" if status == "SLEEPER_SUSPECT" else "High-Risk Token Evasion"
            else:
                status = "CLEAN"
                threat = None
                
            sha = hashlib.sha256(f"{net}:{endpoint}:{label}".encode()).hexdigest()
            meta = {
                "framework": fw,
                "primary_task": task,
                "runtime": "Python 3.12 / vLLM",
                "max_concurrency": random.randint(10, 500),
                "created_epoch": now - random.randint(3600, 864000)
            }
            
            agents.append((
                sha,
                agent_id,
                label,
                net,
                endpoint,
                status,
                threat,
                mitre,
                now - random.randint(1000, 50000),
                now,
                random.randint(5, 120),
                json.dumps(meta)
            ))
            
    return agents

def main():
    print(f"Connecting to DGAR database at {DB_PATH}...")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS agents")
        c.execute("""
            CREATE TABLE agents (
                agent_sha256    TEXT PRIMARY KEY,
                agent_id        TEXT NOT NULL,
                label           TEXT NOT NULL,
                network         TEXT NOT NULL,
                endpoint        TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'UNKNOWN',
                threat_label    TEXT,
                mitre_atlas     TEXT,
                first_seen      REAL NOT NULL,
                last_seen       REAL NOT NULL,
                scan_count      INTEGER DEFAULT 1,
                metadata_json   TEXT
            );
        """)
        
        agents = generate_agents()
        c.executemany("""
            INSERT OR REPLACE INTO agents 
            (agent_sha256, agent_id, label, network, endpoint, status, threat_label, mitre_atlas, first_seen, last_seen, scan_count, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, agents)
        conn.commit()
        
        total = c.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
        breakdown = c.execute("SELECT network, COUNT(*) FROM agents GROUP BY network").fetchall()
        print(f"Successfully populated {total} agents into DGAR database!")
        for net, cnt in breakdown:
            print(f"  • {net:18s}: {cnt:4d} agents")

if __name__ == "__main__":
    main()
