"""
Generación de Embeddings NLP — TT-E3-03.
Usa BERT clínico en español (BioBERT-es / BETO) para generar embeddings
de 768 dimensiones a partir del texto libre del motivo de consulta.

Referencia: Documento de Arquitectura §10.3, RF-NLP.
"""
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración de modelos NLP
# ---------------------------------------------------------------------------
# Modelos candidatos (en orden de preferencia para español clínico):
MODELOS_NLP = {
    "beto_clinico": "dccuchile/bert-base-spanish-wwm-uncased",  # BETO (español general)
    "biomedical_es": "PlanTL-GOB-ES/bsc-bio-ehr-es",           # Biomedical Spanish EHR
    "multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # Multilingüe ligero
}

# Dimensión de embeddings por modelo
EMBEDDING_DIMS = {
    "beto_clinico": 768,
    "biomedical_es": 768,
    "multilingual": 384,
}

# Tamaño máximo de tokens (textos clínicos típicamente cortos)
MAX_LENGTH = 128


class NLPEmbedder:
    """
    Genera embeddings de texto libre usando modelos BERT preentrenados.
    Soporta ejecución CPU (sin GPU) para entornos de desarrollo.
    """

    def __init__(
        self,
        model_name: str = "beto_clinico",
        use_gpu: bool = False,
        batch_size: int = 32,
    ):
        """
        Args:
            model_name: Clave del modelo en MODELOS_NLP.
            use_gpu: Si es True, intenta usar CUDA/MPS.
            batch_size: Tamaño de batch para inferencia.
        """
        self.model_key = model_name
        self.model_path = MODELOS_NLP.get(model_name, model_name)
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        self.embedding_dim = EMBEDDING_DIMS.get(model_name, 768)

        self.model = None
        self.tokenizer = None
        self._device = "cpu"

    # ------------------------------------------------------------------
    # Carga del modelo (lazy)
    # ------------------------------------------------------------------
    def _ensure_loaded(self):
        """Carga el modelo y tokenizador si aún no están en memoria."""
        if self.model is not None:
            return

        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            logger.info(f"Cargando modelo NLP: {self.model_path} ...")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            if self.use_gpu and torch.cuda.is_available():
                self._device = "cuda"
            elif self.use_gpu and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = "mps"

            self.model = AutoModel.from_pretrained(self.model_path)
            self.model.to(self._device)
            self.model.eval()

            logger.info(f"  Modelo cargado en {self._device}. Embedding dim: {self.embedding_dim}")

        except ImportError:
            logger.warning(
                "Transformers no instalado. Usando fallback TF-IDF ligero. "
                "Instala: pip install transformers torch"
            )
            self._load_fallback()

    def _load_fallback(self):
        """Fallback: usa TF-IDF como representación vectorial ligera."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._fallback_mode = True
        self._tfidf = TfidfVectorizer(max_features=256, ngram_range=(1, 2))
        self.embedding_dim = 256
        self._is_fitted = False
        logger.info("  Modo fallback TF-IDF activado (256 dims)")

    # ------------------------------------------------------------------
    # Generación de embeddings
    # ------------------------------------------------------------------
    def generate_embeddings(
        self,
        texts: List[str],
        fit_tfidf: bool = False,
    ) -> np.ndarray:
        """
        Genera embeddings para una lista de textos.

        Args:
            texts: Lista de textos clínicos.
            fit_tfidf: Si True y en modo fallback, ajusta el TF-IDF (train).
                       Si False, solo transforma (test).

        Returns:
            np.ndarray de shape (n_textos, embedding_dim).
        """
        self._ensure_loaded()

        texts = [str(t) if pd.notna(t) and str(t).strip() else "" for t in texts]

        if getattr(self, "_fallback_mode", False):
            return self._generate_tfidf(texts, fit_tfidf)
        else:
            return self._generate_bert(texts)

    def _generate_bert(self, texts: List[str]) -> np.ndarray:
        """Genera embeddings usando BERT (mean pooling)."""
        import torch

        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]

            # Tokenizar
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            # Inferir
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling sobre la última capa hidden
                attention_mask = inputs["attention_mask"]
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
                    input_mask_expanded.sum(1), min=1e-9
                )
                all_embeddings.append(embeddings.cpu().numpy())

        result = np.vstack(all_embeddings)
        logger.info(f"  Embeddings generados: {result.shape}")
        return result

    def _generate_tfidf(self, texts: List[str], fit: bool = False) -> np.ndarray:
        """Fallback TF-IDF."""
        if fit or not self._is_fitted:
            embeddings = self._tfidf.fit_transform(texts).toarray()
            self._is_fitted = True
        else:
            embeddings = self._tfidf.transform(texts).toarray()
        logger.info(f"  Embeddings TF-IDF generados: {embeddings.shape}")
        return embeddings

    # ------------------------------------------------------------------
    # Información
    # ------------------------------------------------------------------
    def get_config(self) -> dict:
        """Retorna la configuración actual del embedder."""
        return {
            "model_key": self.model_key,
            "model_path": self.model_path,
            "embedding_dim": self.embedding_dim,
            "device": self._device,
            "fallback_mode": getattr(self, "_fallback_mode", False),
            "batch_size": self.batch_size,
            "max_length": MAX_LENGTH,
        }


def generate_clinical_embeddings(
    texts: List[str],
    model_name: str = "beto_clinico",
    use_gpu: bool = False,
) -> np.ndarray:
    """
    Función de conveniencia: genera embeddings para textos clínicos.
    """
    embedder = NLPEmbedder(model_name=model_name, use_gpu=use_gpu)
    return embedder.generate_embeddings(texts, fit_tfidf=True)
