def get_variables():
    return {
        "version": "0.0.91",
    }


def is_supported(wafl_llm_version):
    supported_versions = ["0.0.91"]
    return wafl_llm_version in supported_versions
