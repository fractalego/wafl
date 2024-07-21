def get_variables():
    return {
        "version": "1.0.0",
    }


def is_supported(wafl_llm_version):
    supported_versions = ["1.0.0"]
    return wafl_llm_version in supported_versions
