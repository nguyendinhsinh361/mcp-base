npx -y supergateway \
    --stdio "docker run --rm -i -e GITHUB_PERSONAL_ACCESS_TOKEN=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 mcp/github" \
    --port 8002 --baseUrl http://192.168.1.34:8002 \
    --ssePath /sse
    