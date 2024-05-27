def get_variables():
    return {
        "version": "0.0.90",
    }


def is_supported(wafl_llm_version):
    supported_versions = ["0.0.90"]
    return wafl_llm_version in supported_versions
