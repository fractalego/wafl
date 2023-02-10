echo "Starting the Docker instance."
echo "It might take a few minutes for the model to load."
docker run -p8080:8080 --env NVIDIA_DISABLE_REQUIRE=1 --gpus all wafl-llm
