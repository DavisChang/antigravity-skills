# File Inclusion/Exclusion Rules

Rules for determining which files to analyze and which to skip.

## Code File Extensions (include)

`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.h`, `.hpp`, `.go`, `.rs`, `.jsx`, `.tsx`, `.html`, `.css`, `.php`, `.swift`, `.cs`, `.rb`, `.kt`, `.scala`, `.ex`, `.exs`, `.clj`, `.lua`, `.sh`, `.bash`, `.zsh`, `.ps1`, `.r`, `.jl`, `.dart`, `.zig`, `.nim`, `.v`, `.sol`

## Documentation Extensions (include)

`.md`, `.txt`, `.rst`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.xml`, `.graphql`, `.proto`, `.sql`

## Excluded Directories

```
.git, .svn, .hg, .bzr
node_modules, bower_components, jspm_packages
.venv, venv, env, virtualenv, .conda
__pycache__, .pytest_cache, .mypy_cache, .ruff_cache
dist, build, out, bin, target, .output, .next, .nuxt
coverage, htmlcov, .nyc_output, .tox
.eggs, *.egg-info, *.dist-info
lib-cov, .cache, .parcel-cache
packages/*/dist, packages/*/build
vendor (Go), Pods (iOS)
.terraform, .serverless
```

## Excluded Files

```
# Lock files
yarn.lock, pnpm-lock.yaml, package-lock.json, npm-shrinkwrap.json
poetry.lock, Pipfile.lock, requirements.txt.lock, Cargo.lock
composer.lock, Gemfile.lock, bun.lockb

# OS files
.DS_Store, Thumbs.db, desktop.ini, *.lnk

# Environment / secrets
.env, .env.*, *.env

# Config lint files (low value for wiki)
.gitignore, .gitattributes, .gitmodules
.prettierrc, .eslintrc, .eslintignore, .stylelintrc
.editorconfig, .jshintrc, .pylintrc, .flake8
mypy.ini, pyproject.toml (for lint only), tsconfig.json
webpack.config.js, babel.config.js, rollup.config.js
jest.config.js, karma.conf.js, vite.config.js

# Compiled / minified / generated
*.min.js, *.min.css, *.bundle.js, *.bundle.css
*.map, *.d.ts (declaration maps)
*.pyc, *.pyd, *.pyo, *.class
*.o, *.obj, *.a, *.lib, *.lo, *.la, *.slo

# Binary / archive
*.exe, *.dll, *.so, *.dylib, *.dSYM
*.jar, *.war, *.ear
*.zip, *.tar, *.tgz, *.gz, *.rar, *.7z
*.iso, *.dmg, *.img
*.msi, *.msix, *.appx, *.deb, *.rpm
*.ipa, *.apk, *.aab

# Media (skip for code analysis)
*.png, *.jpg, *.jpeg, *.gif, *.svg, *.ico, *.webp
*.mp3, *.mp4, *.avi, *.mov, *.wav
*.pdf, *.doc, *.docx, *.xls, *.xlsx, *.ppt, *.pptx

# Fonts
*.ttf, *.otf, *.woff, *.woff2, *.eot
```

## Token / Size Limits

- **Skip code files** exceeding ~80,000 tokens (~320KB of code)
- **Skip doc files** exceeding ~8,000 tokens (~32KB of text)
- **Skip any file** larger than 1MB

## Implementation Files vs Test Files

Mark files as `is_implementation: false` if:
- Path starts with `test_` or `spec_`
- Path contains `/test/`, `/tests/`, `/__tests__/`, `/spec/`
- Filename ends with `.test.`, `.spec.`, `_test.`, `_spec.`

This distinction helps prioritize implementation code over test code during analysis.
