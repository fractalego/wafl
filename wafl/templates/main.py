from wafl.config import Configuration
from wafl.runners.run_web_interface import app
from wafl.variables import get_variables

if __name__ == "__main__":
    print(get_variables())
    app.run(
        host="0.0.0.0",
        port=Configuration.load_local_config().get_value("frontend_port"),
    )
