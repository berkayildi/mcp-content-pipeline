# Changelog

## [0.12.3](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.12.2...v0.12.3) (2026-04-26)


### Documentation

* **readme:** bump mcp-llm-eval reference to v0.7.0+, add role in ecosystem ([cea6629](https://github.com/berkayildi/mcp-content-pipeline/commit/cea6629b4128798749429b8d8d7e1ec7175115c1))

## [0.12.2](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.12.1...v0.12.2) (2026-04-19)


### Documentation

* add pipeline flow diagram ([3626b90](https://github.com/berkayildi/mcp-content-pipeline/commit/3626b90d0d161cceb228e2bf7270529d666c2ba0))
* update readme ([959d2d4](https://github.com/berkayildi/mcp-content-pipeline/commit/959d2d4d13b58a881f5f7d2942f0bbd1731c1cd9))

## [0.12.1](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.12.0...v0.12.1) (2026-04-19)


### Bug Fixes

* add path containment check for image_path in sync_to_github ([4d35ace](https://github.com/berkayildi/mcp-content-pipeline/commit/4d35ace9df94e41f07eebb061fa5da545f8ab89f))

## [0.12.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.11.0...v0.12.0) (2026-04-19)


### Features

* expand benchmark to 5 models, add Makefile ([c0f8ccc](https://github.com/berkayildi/mcp-content-pipeline/commit/c0f8ccc94784391bcf75c48861d6d47e5ebd8f80))

## [0.11.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.10.0...v0.11.0) (2026-04-17)


### Features

* add LLM eval gate for prompt quality regression testing ([3097990](https://github.com/berkayildi/mcp-content-pipeline/commit/309799060bc02207919a9f8a99aeb67e92e0b247))


### Bug Fixes

* address codebase audit findings ([bae3a04](https://github.com/berkayildi/mcp-content-pipeline/commit/bae3a044eb6420c7c4be97c7c9dde612911feb89))
* raise eval thresholds to match proven quality baseline ([7fe29c6](https://github.com/berkayildi/mcp-content-pipeline/commit/7fe29c6613f378b8b122dc5c1746e1094ec88c98))
* relax TTFT threshold for CI variance ([c9e4e7c](https://github.com/berkayildi/mcp-content-pipeline/commit/c9e4e7c0fc28bdfd6c925518a5806724f3da327d))
* upgrade Gemini benchmark model and fix PR permissions ([be83182](https://github.com/berkayildi/mcp-content-pipeline/commit/be83182e2be40d7619a91451b4b0eeb8af33a84d))
* use Gemini 2.5 Flash-Lite for eval benchmark ([c01e875](https://github.com/berkayildi/mcp-content-pipeline/commit/c01e8753a85a42d39c8fba725f27567b39991ca8))
* use Gemini 3.1 Pro for eval benchmark ([18544d1](https://github.com/berkayildi/mcp-content-pipeline/commit/18544d1d916031a5be7f3ebe8450f26dbf651689))


### Documentation

* expand cost projections with subscription comparison ([d446d3e](https://github.com/berkayildi/mcp-content-pipeline/commit/d446d3ee19ef20a495efca4d1fc99369ad33cee2))

## [0.10.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.9.2...v0.10.0) (2026-04-12)


### Features

* add configurable image output directory ([0f8f651](https://github.com/berkayildi/mcp-content-pipeline/commit/0f8f6516d921beddcb351adcead30edeccdb3b74))
* separate YouTube and X digest into distinct GitHub directories ([6da3d54](https://github.com/berkayildi/mcp-content-pipeline/commit/6da3d5494bdc8f2b51750f0ab2376e70836e0414))

## [0.9.2](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.9.1...v0.9.2) (2026-04-12)


### Bug Fixes

* handle YouTube oEmbed 401 with graceful fallback ([d94df48](https://github.com/berkayildi/mcp-content-pipeline/commit/d94df484bfa6ecbba5d8a80b2c7ea17f8c5af8c2))
* normalize YouTube live URLs for oEmbed metadata ([60068fc](https://github.com/berkayildi/mcp-content-pipeline/commit/60068fc614350ce95bc54e5b151e9777577ca49d))

## [0.9.1](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.9.0...v0.9.1) (2026-04-12)


### Documentation

* update directive ([c9b1f35](https://github.com/berkayildi/mcp-content-pipeline/commit/c9b1f354e8fc52c1b816ee1c3e56406867a9a09f))
* update usage examples to match working tool triggers ([b7379a6](https://github.com/berkayildi/mcp-content-pipeline/commit/b7379a61e508bf80ca148ccf150ef383785fdcfa))

## [0.9.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.8.1...v0.9.0) (2026-04-12)


### Features

* replace youtube-transcript-api with Supadata API ([a674a7d](https://github.com/berkayildi/mcp-content-pipeline/commit/a674a7d7a26f6bb101496e794559c190dfe7b2ae))


### Documentation

* rewrite README and improve tool descriptions for discovery ([9e9304f](https://github.com/berkayildi/mcp-content-pipeline/commit/9e9304f0166b25441337458126e63fdae11e99f6))
* update example X accounts ([dd7cd18](https://github.com/berkayildi/mcp-content-pipeline/commit/dd7cd185620ef03dea21b6e2eeffd75d31ffa28a))

## [0.8.1](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.8.0...v0.8.1) (2026-04-10)


### Documentation

* add cost and project details ([7e82f2c](https://github.com/berkayildi/mcp-content-pipeline/commit/7e82f2c1bccb97f320467fa9ecd84c5584ae73c3))
* add X env vars to Claude Desktop config example ([5fde080](https://github.com/berkayildi/mcp-content-pipeline/commit/5fde080cc6f1324f859e35f82d56fb9b950f11d3))
* update topic section ([d5b57cd](https://github.com/berkayildi/mcp-content-pipeline/commit/d5b57cd64a6b439f0637a73ed5e19f7709e40097))

## [0.8.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.7.0...v0.8.0) (2026-04-10)


### Features

* add X feed digest analysis tool ([7785f2c](https://github.com/berkayildi/mcp-content-pipeline/commit/7785f2caa87bcf66974fddc3796b3505a1ef08d0))


### Bug Fixes

* pydantic-settings ([ec57ccc](https://github.com/berkayildi/mcp-content-pipeline/commit/ec57cccde9ea771bbe81c23459b5b514700dc0ca))

## [0.7.0](https://github.com/berkayildi/mcp-content-pipeline/compare/v0.6.0...v0.7.0) (2026-03-31)


### Features

* add cookie-based YouTube authentication for IP bypass ([daeabfe](https://github.com/berkayildi/mcp-content-pipeline/commit/daeabfee041143de7d9ac9eab3d573eb1bb24f83))
* add image generation via Gemini API ([8d006c2](https://github.com/berkayildi/mcp-content-pipeline/commit/8d006c27be1e2f9f41abf711224b710dd4ab713b))
* add transcript translation fallback and live URL support ([9e32e3e](https://github.com/berkayildi/mcp-content-pipeline/commit/9e32e3e516692f208823809ca46a809a76d3f607))
* initial mcp-content-pipeline implementation ([feea870](https://github.com/berkayildi/mcp-content-pipeline/commit/feea870e9e41abc8e023071749dada3ecc6f89c8))
* rename Twitter/X labels to Social Hook in user-facing strings ([cd38af8](https://github.com/berkayildi/mcp-content-pipeline/commit/cd38af8299e0d1ffbc9fa5f52235a8143a7e3a27))
* upgrade default image model to Gemini 3.1 Flash ([7db88df](https://github.com/berkayildi/mcp-content-pipeline/commit/7db88dfbb921a866789697db9ec5c43876cd1b97))


### Bug Fixes

* **claude-client:** override date_analysed instead of trusting LLM response ([480dab1](https://github.com/berkayildi/mcp-content-pipeline/commit/480dab16676364f31547b63f8c417cd8fe5f1d14))
* escape pipe characters in index table to prevent column breaking ([7d07438](https://github.com/berkayildi/mcp-content-pipeline/commit/7d07438a977fc02b783e456b9d77b1bcfa97158f))
* pass raw bytes to PyGithub to prevent double base64-encoding of images ([bcd769c](https://github.com/berkayildi/mcp-content-pipeline/commit/bcd769c86fedb9d090632a9f6d70bf27b5921be7))
* preserve existing index entries when syncing new analyses ([ae0cdf9](https://github.com/berkayildi/mcp-content-pipeline/commit/ae0cdf9f84f3983be7433a918812f771539124f4))
* remove f string from url ([d4bddc4](https://github.com/berkayildi/mcp-content-pipeline/commit/d4bddc42929023e44ba1d10a6ee666458ed290de))
* save generated images to temp file to avoid MCP 1MB transport limit ([d6b1e74](https://github.com/berkayildi/mcp-content-pipeline/commit/d6b1e74bb8039aba6ab1ac5042719988d61d0d18))
* update youtube-transcript-api to v1.x API ([5f27c53](https://github.com/berkayildi/mcp-content-pipeline/commit/5f27c532be59876c3646ffdb853f00061b3f00f2))


### Documentation

* add usage section to README ([415c8c9](https://github.com/berkayildi/mcp-content-pipeline/commit/415c8c940b61bb8af181bdfbd343876847c8ec05))
* **readme:** add PyPI downloads badge ([0ecb2d7](https://github.com/berkayildi/mcp-content-pipeline/commit/0ecb2d7bfc797126709866179d17bc4fc7155294))
* remove example workflow ([72513c9](https://github.com/berkayildi/mcp-content-pipeline/commit/72513c93c8dcd1563494e68e4d36edf935d780ee))
* update readme ([3156db9](https://github.com/berkayildi/mcp-content-pipeline/commit/3156db920934725a373e2408e3d972f55322fb64))

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
