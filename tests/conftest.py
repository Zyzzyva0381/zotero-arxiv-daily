import pytest
import hydra

@pytest.fixture(scope="package")
def config():
    with hydra.initialize(config_path='../config',version_base=None):
        config = hydra.compose(config_name="default")
    config.pages.output_dir = "site-test"
    config.pages.site_title = "Test Site"
    config.pages.keep_days = 7
    config.pages.generate_empty_page = True
    config.pages.empty_message = "No papers today."
    config.llm.api.base_url = "http://localhost:30000/v1"
    config.llm.api.key = "sk-xxx"
    config.reranker.api.base_url = "http://localhost:30000/v1"
    config.reranker.api.key = "sk-xxx"
    config.reranker.api.model = "text-embedding-3-large"
    return config

