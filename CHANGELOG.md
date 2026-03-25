# Changelog

## [0.6.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.5.3...v0.6.0) (2026-03-25)


### Features

* upgrade default image model to Gemini 3.1 Flash ([f128f8d](https://github.com/berkayildi/mcp-content-pipeline/commit/f128f8dbd484ec1df373723b9e81ad316c7cc7e6))

## [0.5.3](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.5.2...v0.5.3) (2026-03-23)


### Documentation

* add usage section to README ([9a29abb](https://github.com/berkayildi/mcp-content-pipeline/commit/9a29abb0b929f91daca2e643e9742f835fb0aaa7))
* remove example workflow ([458926b](https://github.com/berkayildi/mcp-content-pipeline/commit/458926b5d5faf51ff542b7743684c563210f7aeb))

## [0.5.2](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.5.1...v0.5.2) (2026-03-23)


### Bug Fixes

* pass raw bytes to PyGithub to prevent double base64-encoding of images ([df42a77](https://github.com/berkayildi/mcp-content-pipeline/commit/df42a777e37b4ac8de125cb9f819832afaddb99a))

## [0.5.1](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.5.0...v0.5.1) (2026-03-22)


### Bug Fixes

* save generated images to temp file to avoid MCP 1MB transport limit ([eee99da](https://github.com/berkayildi/mcp-content-pipeline/commit/eee99da5ab7a2e4284e216acafcd082349585ad2))

## [0.5.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.4.2...v0.5.0) (2026-03-22)


### Features

* add image generation via Gemini API ([4b7fc3f](https://github.com/berkayildi/mcp-content-pipeline/commit/4b7fc3ff47d2f4665b3b225a0173f0bf87ae1aa7))

## [0.4.2](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.4.1...v0.4.2) (2026-03-22)


### Bug Fixes

* remove f string from url ([47cfae3](https://github.com/berkayildi/mcp-content-pipeline/commit/47cfae3d036bc139f3f900effc7eb735d3038ec6))

## [0.4.1](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.4.0...v0.4.1) (2026-03-14)


### Bug Fixes

* escape pipe characters in index table to prevent column breaking ([f39ae71](https://github.com/berkayildi/mcp-content-pipeline/commit/f39ae7155c98016b1cbbcee9f276b3aaabc0786d))
* preserve existing index entries when syncing new analyses ([7006ce6](https://github.com/berkayildi/mcp-content-pipeline/commit/7006ce67a35a32f6578b42ac066b3d4b68a702f7))

## [0.4.0](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.3.2...v0.4.0) (2026-03-10)


### Features

* rename Twitter/X labels to Social Hook in user-facing strings ([42d99d8](https://github.com/berkayyildirim/mcp-content-pipeline/commit/42d99d859a5b79dd1a5ff48b7cc72863521821d4))

## [0.3.2](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.3.1...v0.3.2) (2026-03-10)


### Documentation

* **readme:** add PyPI downloads badge ([d7f4aaa](https://github.com/berkayyildirim/mcp-content-pipeline/commit/d7f4aaad26c71b34f2e5b01ac1a0a7d07cd688ab))
* update readme ([74a4051](https://github.com/berkayyildirim/mcp-content-pipeline/commit/74a405163a580cd99f6a1807ae2beb61cf031617))

## [0.3.1](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.3.0...v0.3.1) (2026-03-10)


### Bug Fixes

* **claude-client:** override date_analysed instead of trusting LLM response ([6af7028](https://github.com/berkayyildirim/mcp-content-pipeline/commit/6af7028c29a36ab7784e160175446e998316d4d6))

## [0.3.0](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.2.1...v0.3.0) (2026-03-09)


### Features

* add cookie-based YouTube authentication for IP bypass ([daeabfe](https://github.com/berkayyildirim/mcp-content-pipeline/commit/daeabfee041143de7d9ac9eab3d573eb1bb24f83))

## [0.2.1](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.2.0...v0.2.1) (2026-03-09)


### Bug Fixes

* update youtube-transcript-api to v1.x API ([5f27c53](https://github.com/berkayyildirim/mcp-content-pipeline/commit/5f27c532be59876c3646ffdb853f00061b3f00f2))

## [0.2.0](https://github.com/berkayyildirim/mcp-content-pipeline/compare/v0.1.0...v0.2.0) (2026-03-09)


### Features

* add transcript translation fallback and live URL support ([9e32e3e](https://github.com/berkayyildirim/mcp-content-pipeline/commit/9e32e3e516692f208823809ca46a809a76d3f607))

## 0.1.0 (2026-03-08)


### Features

* initial mcp-content-pipeline implementation ([feea870](https://github.com/berkayyildirim/mcp-content-pipeline/commit/feea870e9e41abc8e023071749dada3ecc6f89c8))
