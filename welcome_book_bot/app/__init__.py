from dataclasses import dataclass, field


@dataclass
class Data:
    emb_model_name: str = field(default="ai-forever/sbert_large_nlu_ru")
    emb_dimension: int = field(default=1024)
    max_length: int = field(default=36)
    k_neighbors: int = field(default=4)
