def get_variables():
    return {
        "version": "0.1.1",
    }


def is_supported(wafl_llm_version):
    supported_versions = ["0.1.0"]
    return wafl_llm_version in supported_versions
