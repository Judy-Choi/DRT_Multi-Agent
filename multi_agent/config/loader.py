"""
설정 로더 및 LLM 생성
"""
import tomllib
import logging
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from openai import RateLimitError
from anthropic import RateLimitError as AnthropicRateLimitError
from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)

def load_settings():
    """settings.toml 파일을 로드합니다."""
    config_path = Path(__file__).parent / "settings.toml"
    
    with open(config_path, "rb") as f:
        return tomllib.load(f)

def _create_llm_instance(model_name, temperature, max_tokens):
    """단일 LLM 인스턴스를 생성합니다."""
    if "claude" in model_name:
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif "gpt" in model_name:
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"지원하지 않는 모델입니다: {model_name}")

def create_llm(settings=None):
    """설정에 따라 LLM을 생성합니다."""
    if settings is None:
        settings = load_settings()
    
    llm_config = settings["llm"]
    primary_model = llm_config["model"]
    fallback_model = llm_config.get("fallback_model")
    temperature = llm_config.get("temperature", 0.0)
    max_tokens = llm_config.get("max_tokens", 1024)

    # Fallback 기능이 있는 LLM 래퍼 반환
    return FallbackLLM(
        primary_model=primary_model,
        fallback_model=fallback_model,
        temperature=temperature,
        max_tokens=max_tokens
    )

class FallbackLLM(Runnable):
    """Fallback 기능이 있는 LLM 래퍼 클래스"""
    
    def __init__(self, primary_model, fallback_model, temperature, max_tokens):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 주 모델 인스턴스 생성
        self.primary_llm = _create_llm_instance(primary_model, temperature, max_tokens)
        
        # 대체 모델 인스턴스 생성 (있는 경우)
        self.fallback_llm = None
        if fallback_model:
            self.fallback_llm = _create_llm_instance(fallback_model, temperature, max_tokens)
    
    def invoke(self, messages, config=None):
        """메시지를 처리하고 fallback 기능을 제공합니다."""
        try:
            # 주 모델로 시도
            return self.primary_llm.invoke(messages, config=config)
        except (RateLimitError, AnthropicRateLimitError) as e:
            if self.fallback_llm:
                logger.warning(f"🔄 {self.primary_model}에서 속도 제한 발생, {self.fallback_model}으로 전환합니다.")
                return self.fallback_llm.invoke(messages, config=config)
            else:
                logger.error("❌ Fallback 모델이 설정되지 않아 오류를 재발생시킵니다.")
                raise
        except Exception as e:
            # 다른 종류의 오류도 fallback으로 처리할 수 있음
            if self.fallback_llm and "rate" in str(e).lower():
                logger.warning(f"🔄 {self.primary_model}에서 오류 발생 ({e}), {self.fallback_model}으로 전환합니다.")
                return self.fallback_llm.invoke(messages, config=config)
            else:
                raise
    
    def __getattr__(self, name):
        """다른 메서드들은 주 모델로 위임"""
        return getattr(self.primary_llm, name)

# 설정 로드
SETTINGS = load_settings()

# 자주 사용되는 값들을 상수로 노출
MAX_ITERATIONS = SETTINGS["translation"]["max_iterations"]
LLM_MODEL = SETTINGS["llm"]["model"] 