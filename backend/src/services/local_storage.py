"""
In-memory local storage for testing without Supabase.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List


class LocalStorage:
    def __init__(self):
        self.original_cvs: Dict[str, Any] = {}
        self.job_postings: Dict[str, Any] = {}
        self.generated_cvs: Dict[str, Any] = {}
        self.profiles: Dict[str, Any] = {}

    def _now(self) -> str:
        return datetime.now().isoformat()

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        item = {**data, "id": data.get("id") or str(uuid.uuid4()), "created_at": self._now()}
        collection = getattr(self, table, None)
        if collection is None:
            raise ValueError(f"Unknown table: {table}")
        collection[item["id"]] = item
        return item

    def get(self, table: str, item_id: str) -> Dict[str, Any] | None:
        collection = getattr(self, table, None)
        return collection.get(item_id) if collection else None

    def list_by_user(self, table: str, user_id: str) -> List[Dict[str, Any]]:
        collection = getattr(self, table, None)
        if not collection:
            return []
        return [item for item in collection.values() if item.get("user_id") == user_id]

    def update(self, table: str, item_id: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
        collection = getattr(self, table, None)
        if not collection or item_id not in collection:
            return None
        item = collection[item_id]
        item.update(data)
        item["updated_at"] = self._now()
        return item

    def delete(self, table: str, item_id: str) -> bool:
        collection = getattr(self, table, None)
        if collection and item_id in collection:
            del collection[item_id]
            return True
        return False


storage = LocalStorage()
