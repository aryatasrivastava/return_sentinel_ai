from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_POLICY_TYPES = {
    "STANDARD_RETURN",
    "EXCHANGE_FIRST",
    "STORE_CREDIT",
    "RESTOCKING_FEE",
}


class PolicyConfigBase(BaseModel):
    low_risk_allowed: List[str] = Field(
        ...,
        description="Allowed return policies for low risk orders",
    )
    medium_risk_allowed: List[str] = Field(
        ...,
        description="Allowed return policies for medium risk orders",
    )
    high_risk_allowed: List[str] = Field(
        ...,
        description="Allowed return policies for high risk orders",
    )
    low_confidence_fallback: str = Field(
        ...,
        description="Fallback return policy for low confidence cases",
    )

    @field_validator(
        "low_risk_allowed", "medium_risk_allowed", "high_risk_allowed", mode="before"
    )
    @classmethod
    def validate_allowed_policies(cls, value, info):
        field_name = info.field_name
        if not isinstance(value, list):
            raise ValueError(f"Field '{field_name}' must be a list of policy strings.")
        if len(value) == 0:
            raise ValueError(
                f"Field '{field_name}' cannot be empty. At least one policy is required."
            )

        seen = set()
        for policy in value:
            if not isinstance(policy, str):
                raise ValueError(
                    f"Invalid policy value '{policy}' in '{field_name}'. Expected a string."
                )
            if policy not in VALID_POLICY_TYPES:
                raise ValueError(
                    f"Invalid policy '{policy}' in '{field_name}'. Allowed values are: {sorted(list(VALID_POLICY_TYPES))}."
                )
            if policy in seen:
                raise ValueError(
                    f"Duplicate policy '{policy}' found in '{field_name}'. Duplicate values are not allowed."
                )
            seen.add(policy)

        return value

    @field_validator("low_confidence_fallback", mode="before")
    @classmethod
    def validate_fallback_policy(cls, value):
        if not isinstance(value, str):
            raise ValueError(
                "Field 'low_confidence_fallback' must be a single string, not a list or other type."
            )
        if value not in VALID_POLICY_TYPES:
            raise ValueError(
                f"Invalid policy '{value}' for 'low_confidence_fallback'. Allowed values are: {sorted(list(VALID_POLICY_TYPES))}."
            )
        return value


class PolicyConfigUpdate(PolicyConfigBase):
    pass


class PolicyConfigResponse(PolicyConfigBase):
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
