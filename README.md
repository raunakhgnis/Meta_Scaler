## Run

docker build -t support-env .

docker run \
-e OPENAI_API_KEY=your_key \
-e API_BASE_URL=https://api.openai.com/v1 \
-e MODEL_NAME=gpt-4o-mini \
support-env