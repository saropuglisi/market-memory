from .base import EpisodeEncoder
from .approach_1_concat import ConcatBaseline
from .approach_2_factorized import FactorizedMultiStage
from .approach_4_graph import GraphEncoder

# Contrastive encoders v1/v2/v3 archived 2026-05-26 after the blind A/B test v2
# revealed that "reactional geometry" — the property they optimize — does not
# correspond to "useful for human analogical reasoning". See
# approaches/archived/README_CONTRASTIVE_ARCHIVE.md.
#
# LLM structured encoders v1/v2/v3 archived 2026-05-25 (fail rate 23% on N=500
# real, generative/discriminative mismatch). See
# approaches/archived/README_LLM_ARCHIVE.md.
#
# To re-enable any archived encoder for historical comparison:
#   from .archived.approach_3_contrastive_v2 import ContrastiveEncoderV2
#   from .archived.approach_5_llm_struct_v3 import LLMStructuredEncoderV3

__all__ = [
    "EpisodeEncoder",
    "ConcatBaseline",
    "FactorizedMultiStage",
    "GraphEncoder",
]
