# Guide to Publishing Your Code on npm

This guide will walk you through the process of publishing your JavaScript/TypeScript source code to the npm registry.

## Prerequisites

1. **Node.js and npm installed** - If not already installed, download from [nodejs.org](https://nodejs.org/)
2. **npm account** - Create one at [npmjs.com](https://www.npmjs.com/signup)
3. **Your code ready** - Ensure your code is working and properly organized

## Step 1: Prepare Your Package

### Initialize Your Package

If your project doesn't already have a package.json file:

```bash
cd your-project
npm init
```

Fill in the prompts (name, version, description, entry point, etc.).

### Configure package.json

Ensure your package.json includes these essential fields:

```json
{
  "name": "your-package-name",
  "version": "1.0.0",
  "description": "Your package description",
  "main": "index.js", // Or your main entry file
  "files": [
    "dist",          // Include compiled files if applicable
    "src",           // Source files if you want to publish them
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "your-build-command", // If using TypeScript or build tools
    "test": "your-test-command",
    "prepublishOnly": "npm run build && npm test" // Run before publishing
  },
  "keywords": ["keyword1", "keyword2"],
  "author": "Your Name <your.email@example.com>",
  "license": "MIT", // Or your chosen license
  "repository": {
    "type": "git",
    "url": "git+https://github.com/yourusername/your-repo.git"
  },
  "bugs": {
    "url": "https://github.com/yourusername/your-repo/issues"
  },
  "homepage": "https://github.com/yourusername/your-repo#readme"
}
```

### TypeScript Configuration (if applicable)

If your project uses TypeScript, ensure your `tsconfig.json` is properly set up:

```json
{
  "compilerOptions": {
    "target": "es2018",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "strict": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "**/__tests__/*"]
}
```

## Step 2: Add Documentation

Create a README.md file with:

1. Package description
2. Installation instructions
3. Usage examples
4. API documentation
5. License information

## Step 3: Login to npm

```bash
npm login
```

Enter your npm credentials when prompted.

## Step 4: Publish Your Package

First, verify what files will be included:

```bash
npm pack --dry-run
```

If everything looks good, publish:

```bash
npm publish
```

If this is your first version, the package will be published. If the package name is taken, you'll need to choose a different name.

### For Scoped Packages (e.g., @yourname/package)

```bash
npm publish --access public
```

## Step 5: Update Your Package

When you want to update your package:

1. Make your changes
2. Update the version in package.json (follow semantic versioning)
   ```bash
   npm version patch  # For bug fixes
   npm version minor  # For new features
   npm version major  # For breaking changes
   ```
3. Publish again
   ```bash
   npm publish
   ```

## Best Practices

1. **Use semantic versioning** (MAJOR.MINOR.PATCH)
2. **Include tests** in your package
3. **Set up CI/CD** for automated testing and publishing
4. **Use .npmignore** to exclude unnecessary files
5. **Add badges** to your README.md

## Example .npmignore File

```
.git
.github
node_modules
src
tests
coverage
.travis.yml
.eslintrc
.prettierrc
jest.config.js
tsconfig.json
```

## Troubleshooting

- **Name conflicts**: If your package name is taken, choose a different name or use a scoped package (`@username/package-name`)
- **Publishing errors**: Check npm logs (`npm publish --loglevel=verbose`)
- **Version conflicts**: Ensure you're incrementing the version number correctly

## Publishing Private Packages

For private packages (requires npm paid account):

```bash
npm publish --access private
```

## Update version

```bash
git add .
git commit -m "Updated package code"
npm version patch
npm publish
```