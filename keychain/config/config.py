from keychain.config.base import Config, WebClientConfig

config = Config()  # type: ignore[call-arg]
web_client_config = WebClientConfig()  # type: ignore[call-arg]

__all__ = ["config", "web_client_config"]
