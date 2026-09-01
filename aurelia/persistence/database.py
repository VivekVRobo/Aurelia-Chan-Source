"""
Aurelia Cognitive OS V4 - SQLite Transactional Database & State Persistence
===========================================================================
Ensures ACID transactions around cognitive commits. If any cognitive or
verification step fails, the entire transaction is rolled back.
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


class CognitiveDatabase:
    """
    ACID transactional storage for Aurelia Cognitive OS V4.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        """Initializes tables for receipts, memories, and artifacts."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_receipts (
                    decision_id TEXT PRIMARY KEY,
                    snapshot_id TEXT NOT NULL,
                    request_text TEXT NOT NULL,
                    intent_type TEXT NOT NULL,
                    conclusion_summary TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS executive_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    artifact_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    decision_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_cognitive_cycle_transaction(
        self,
        decision_id: str,
        snapshot_id: str,
        request_text: str,
        intent_type: str,
        conclusion: str,
        confidence: float,
        artifacts: List[Dict[str, Any]]
    ) -> bool:
        """
        Saves receipt and artifacts inside a single SQLite transaction.
        Rolls back completely if an exception occurs.
        """
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO decision_receipts (
                        decision_id, snapshot_id, request_text, intent_type, conclusion_summary, confidence_score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (decision_id, snapshot_id, request_text, intent_type, conclusion, confidence))

                for art in artifacts:
                    self.conn.execute("""
                        INSERT INTO executive_artifacts (
                            artifact_id, artifact_type, title, version, decision_id, payload_json
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        art["id"],
                        art["type"],
                        art["title"],
                        art["version"],
                        decision_id,
                        json.dumps(art["payload"])
                    ))
            return True
        except Exception as e:
            print(f"Transaction rollback: {e}")
            return False

    def get_decision_receipt(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Lookup a receipt by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT decision_id, snapshot_id, request_text, conclusion_summary, confidence_score FROM decision_receipts WHERE decision_id = ?", (decision_id,))
        row = cursor.fetchone()
        if row:
            return {
                "decision_id": row[0],
                "snapshot_id": row[1],
                "request_text": row[2],
                "conclusion_summary": row[3],
                "confidence_score": row[4]
            }
        return None
