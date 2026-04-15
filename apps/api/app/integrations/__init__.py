"""Third-party integration adapters."""

from app.integrations.apollo import ApolloAdapter
from app.integrations.attio import AttioAdapter
from app.integrations.base import IntegrationResult, NotConfiguredError
from app.integrations.bukku import BukkuAdapter
from app.integrations.calcom import CalcomAdapter
from app.integrations.meta import MetaAdapter
from app.integrations.metricool import MetricoolAdapter

__all__ = [
    "ApolloAdapter",
    "AttioAdapter",
    "BukkuAdapter",
    "CalcomAdapter",
    "IntegrationResult",
    "MetaAdapter",
    "MetricoolAdapter",
    "NotConfiguredError",
]
