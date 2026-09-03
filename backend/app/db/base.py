# Import all the models, so that Base has them before being
# imported by Alembic or Base.metadata.create_all()
from app.db.session import Base  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401
from app.models.return_ import Return  # noqa: F401
from app.models.risk_prediction import RiskPrediction  # noqa: F401
from app.models.policy_decision import PolicyDecision  # noqa: F401
from app.models.customer_risk_cache import CustomerRiskCache  # noqa: F401
from app.models.product_risk_cache import ProductRiskCache  # noqa: F401
from app.models.policy_config import PolicyConfig  # noqa: F401
from app.models.agent_trace import AgentTrace  # noqa: F401

