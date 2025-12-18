"""
Credit Card Statement Parser Package
Provides parsers for multiple credit card issuers
"""

from .detect_issuer import detect_issuer
from .hdfc import parse_hdfc
from .icici import parse_icici
from .axis import parse_axis
from .chase import parse_chase
from .idfc import parse_idfc

__all__ = [
    'detect_issuer',
    'parse_hdfc',
    'parse_icici',
    'parse_axis',
    'parse_chase',
    'parse_idfc',
]
