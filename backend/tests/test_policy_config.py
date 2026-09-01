import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.main import app

from app.schemas.policy_config import (
    PolicyConfigBase,
    PolicyConfigUpdate,
    PolicyConfigResponse,
    VALID_POLICY_TYPES,
)
from app.models.policy_config import (
    PolicyConfig,
    DEFAULT_LOW_RISK_ALLOWED,
    DEFAULT_MEDIUM_RISK_ALLOWED,
    DEFAULT_HIGH_RISK_ALLOWED,
    DEFAULT_LOW_CONFIDENCE_FALLBACK,
)
from app.db.session import SessionLocal, engine
from app.db.base import Base


class TestPolicyConfigSchema(unittest.TestCase):
    def test_schema_valid_payload(self):
        """Verify that a valid configuration passes schema validation."""
        data = {
            "low_risk_allowed": ["STANDARD_RETURN"],
            "medium_risk_allowed": ["STANDARD_RETURN", "EXCHANGE_FIRST", "RESTOCKING_FEE"],
            "high_risk_allowed": ["EXCHANGE_FIRST", "STORE_CREDIT", "RESTOCKING_FEE"],
            "low_confidence_fallback": "EXCHANGE_FIRST",
        }
        model = PolicyConfigUpdate(**data)
        self.assertEqual(model.low_risk_allowed, ["STANDARD_RETURN"])
        self.assertEqual(model.low_confidence_fallback, "EXCHANGE_FIRST")

    def test_schema_empty_list_rejected(self):
        """Verify that empty allowed policy lists are rejected with clear error."""
        for field in ["low_risk_allowed", "medium_risk_allowed", "high_risk_allowed"]:
            data = {
                "low_risk_allowed": ["STANDARD_RETURN"],
                "medium_risk_allowed": ["STANDARD_RETURN"],
                "high_risk_allowed": ["STORE_CREDIT"],
                "low_confidence_fallback": "EXCHANGE_FIRST",
            }
            data[field] = []
            with self.assertRaises(ValidationError) as ctx:
                PolicyConfigUpdate(**data)
            self.assertIn(f"Field '{field}' cannot be empty", str(ctx.exception))

    def test_schema_invalid_policy_string_rejected(self):
        """Verify that invalid policy type strings are rejected naming the invalid value."""
        data = {
            "low_risk_allowed": ["NON_EXISTENT_POLICY"],
            "medium_risk_allowed": ["STANDARD_RETURN"],
            "high_risk_allowed": ["STORE_CREDIT"],
            "low_confidence_fallback": "EXCHANGE_FIRST",
        }
        with self.assertRaises(ValidationError) as ctx:
            PolicyConfigUpdate(**data)
        self.assertIn("Invalid policy 'NON_EXISTENT_POLICY'", str(ctx.exception))

    def test_schema_duplicate_policy_rejected(self):
        """Verify that duplicate policies in a single list are rejected."""
        data = {
            "low_risk_allowed": ["STANDARD_RETURN", "STANDARD_RETURN"],
            "medium_risk_allowed": ["STANDARD_RETURN"],
            "high_risk_allowed": ["STORE_CREDIT"],
            "low_confidence_fallback": "EXCHANGE_FIRST",
        }
        with self.assertRaises(ValidationError) as ctx:
            PolicyConfigUpdate(**data)
        self.assertIn("Duplicate policy 'STANDARD_RETURN'", str(ctx.exception))

    def test_schema_invalid_fallback_rejected(self):
        """Verify that low_confidence_fallback must be a valid single string."""
        # Test invalid string
        data1 = {
            "low_risk_allowed": ["STANDARD_RETURN"],
            "medium_risk_allowed": ["STANDARD_RETURN"],
            "high_risk_allowed": ["STORE_CREDIT"],
            "low_confidence_fallback": "INVALID_FALLBACK",
        }
        with self.assertRaises(ValidationError) as ctx1:
            PolicyConfigUpdate(**data1)
        self.assertIn("Invalid policy 'INVALID_FALLBACK' for 'low_confidence_fallback'", str(ctx1.exception))

        # Test list passed instead of string
        data2 = {
            "low_risk_allowed": ["STANDARD_RETURN"],
            "medium_risk_allowed": ["STANDARD_RETURN"],
            "high_risk_allowed": ["STORE_CREDIT"],
            "low_confidence_fallback": ["EXCHANGE_FIRST"],
        }
        with self.assertRaises(ValidationError) as ctx2:
            PolicyConfigUpdate(**data2)
        self.assertIn("Field 'low_confidence_fallback' must be a single string", str(ctx2.exception))


class TestPolicyConfigAPI(unittest.TestCase):
    def test_api_endpoints(self):
        """Test full FastAPI integration with PostgreSQL."""
        with TestClient(app) as client:
            # 1. Test health check
            health_resp = client.get("/health")
            self.assertEqual(health_resp.status_code, 200)
            self.assertEqual(health_resp.json(), {"status": "healthy"})

            # 2. Test root endpoint
            root_resp = client.get("/")
            self.assertEqual(root_resp.status_code, 200)
            self.assertEqual(root_resp.json(), {"message": "ReturnSentinel AI API is running"})

            # 3. Test GET /api/policy-config returns default seeded config
            get_resp = client.get("/api/policy-config")
            self.assertEqual(get_resp.status_code, 200)
            body = get_resp.json()
            self.assertEqual(body["low_risk_allowed"], DEFAULT_LOW_RISK_ALLOWED)
            self.assertEqual(body["medium_risk_allowed"], DEFAULT_MEDIUM_RISK_ALLOWED)
            self.assertEqual(body["high_risk_allowed"], DEFAULT_HIGH_RISK_ALLOWED)
            self.assertEqual(body["low_confidence_fallback"], DEFAULT_LOW_CONFIDENCE_FALLBACK)
            self.assertIn("updated_at", body)

            # 4. Test PUT /api/policy-config rejection: empty list
            put_empty = client.put(
                "/api/policy-config",
                json={
                    "low_risk_allowed": [],
                    "medium_risk_allowed": ["STANDARD_RETURN"],
                    "high_risk_allowed": ["RESTOCKING_FEE"],
                    "low_confidence_fallback": "EXCHANGE_FIRST",
                },
            )
            self.assertEqual(put_empty.status_code, 422)
            self.assertIn("Field 'low_risk_allowed' cannot be empty", put_empty.text)

            # 5. Test PUT /api/policy-config rejection: invalid policy
            put_invalid = client.put(
                "/api/policy-config",
                json={
                    "low_risk_allowed": ["UNKNOWN_POLICY"],
                    "medium_risk_allowed": ["STANDARD_RETURN"],
                    "high_risk_allowed": ["RESTOCKING_FEE"],
                    "low_confidence_fallback": "EXCHANGE_FIRST",
                },
            )
            self.assertEqual(put_invalid.status_code, 422)
            self.assertIn("Invalid policy 'UNKNOWN_POLICY'", put_invalid.text)

            # 6. Test PUT /api/policy-config rejection: duplicate policy
            put_duplicate = client.put(
                "/api/policy-config",
                json={
                    "low_risk_allowed": ["STANDARD_RETURN", "STANDARD_RETURN"],
                    "medium_risk_allowed": ["STANDARD_RETURN"],
                    "high_risk_allowed": ["RESTOCKING_FEE"],
                    "low_confidence_fallback": "EXCHANGE_FIRST",
                },
            )
            self.assertEqual(put_duplicate.status_code, 422)
            self.assertIn("Duplicate policy 'STANDARD_RETURN'", put_duplicate.text)

            # 7. Test PUT /api/policy-config rejection: invalid fallback
            put_invalid_fb = client.put(
                "/api/policy-config",
                json={
                    "low_risk_allowed": ["STANDARD_RETURN"],
                    "medium_risk_allowed": ["STANDARD_RETURN"],
                    "high_risk_allowed": ["RESTOCKING_FEE"],
                    "low_confidence_fallback": ["EXCHANGE_FIRST"],
                },
            )
            self.assertEqual(put_invalid_fb.status_code, 422)

            # 8. Test PUT /api/policy-config valid update
            valid_update = {
                "low_risk_allowed": ["STANDARD_RETURN", "EXCHANGE_FIRST"],
                "medium_risk_allowed": ["EXCHANGE_FIRST", "STORE_CREDIT"],
                "high_risk_allowed": ["RESTOCKING_FEE"],
                "low_confidence_fallback": "STORE_CREDIT",
            }
            put_valid = client.put("/api/policy-config", json=valid_update)
            self.assertEqual(put_valid.status_code, 200)
            updated_body = put_valid.json()
            self.assertEqual(updated_body["low_risk_allowed"], ["STANDARD_RETURN", "EXCHANGE_FIRST"])
            self.assertEqual(updated_body["medium_risk_allowed"], ["EXCHANGE_FIRST", "STORE_CREDIT"])
            self.assertEqual(updated_body["high_risk_allowed"], ["RESTOCKING_FEE"])
            self.assertEqual(updated_body["low_confidence_fallback"], "STORE_CREDIT")
            self.assertIn("updated_at", updated_body)

            # 9. Test subsequent GET /api/policy-config returns persisted changes
            get_persisted = client.get("/api/policy-config")
            self.assertEqual(get_persisted.status_code, 200)
            persisted_body = get_persisted.json()
            self.assertEqual(persisted_body["low_risk_allowed"], ["STANDARD_RETURN", "EXCHANGE_FIRST"])
            self.assertEqual(persisted_body["medium_risk_allowed"], ["EXCHANGE_FIRST", "STORE_CREDIT"])
            self.assertEqual(persisted_body["high_risk_allowed"], ["RESTOCKING_FEE"])
            self.assertEqual(persisted_body["low_confidence_fallback"], "STORE_CREDIT")

            # 10. Reset back to defaults for clean state
            reset_payload = {
                "low_risk_allowed": DEFAULT_LOW_RISK_ALLOWED,
                "medium_risk_allowed": DEFAULT_MEDIUM_RISK_ALLOWED,
                "high_risk_allowed": DEFAULT_HIGH_RISK_ALLOWED,
                "low_confidence_fallback": DEFAULT_LOW_CONFIDENCE_FALLBACK,
            }
            reset_resp = client.put("/api/policy-config", json=reset_payload)
            self.assertEqual(reset_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
