cd ..
cd app/supergateway

yarn build
yarn start \
    --stdio "docker run --rm -i -e GITHUB_PERSONAL_ACCESS_TOKEN= mcp/github" \
    --port 8002 --baseUrl http://192.168.1.34:8002 \
    --ssePath /sse
    