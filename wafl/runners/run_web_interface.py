from wafl.runners.routes import get_app

app = get_app()


def run_app():
    app.run(host="0.0.0.0", port=8889)


if __name__ == "__main__":
    run_app()
