FROM node:18-slim AS node-base
FROM python:3.11

# Copy Node.js và npm
COPY --from=node-base /usr/local/bin/node /usr/local/bin/
COPY --from=node-base /usr/local/bin/npm /usr/local/bin/

# Copy toàn bộ thư mục node_modules (quan trọng cho npx)
COPY --from=node-base /usr/local/lib/node_modules /usr/local/lib/node_modules

# Tạo symbolic links cho npx
RUN ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY npx_api.py .

# Expose the port the app runs on
EXPOSE 10000


# Command to run the application with auto-reload
CMD ["uvicorn", "npx_api:app", "--host", "0.0.0.0", "--port", "10000", "--reload"]