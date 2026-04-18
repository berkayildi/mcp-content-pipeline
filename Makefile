.PHONY: benchmark benchmark-copy

# Run LLM benchmark against all models in .eval-gate.yml
benchmark:
	@set -a && . ./.env && set +a && uvx --with anthropic --with openai --with google-genai mcp-llm-eval run --config .eval-gate.yml --dataset eval/dataset.json --output-dir eval/results

# Copy benchmark results to llm-benchmarks repo for LLMShot
benchmark-copy:
	@if [ ! -d "../llm-benchmarks/text-generation" ]; then \
		echo "Error: ../llm-benchmarks/text-generation not found. Clone the repo as a sibling directory."; \
		exit 1; \
	fi
	cp eval/results/latest_summary.json ../llm-benchmarks/text-generation/content-pipeline-summary.json
	cp $$(ls -t eval/results/*_benchmark.json | head -1) ../llm-benchmarks/text-generation/content-pipeline-benchmark.json
	@echo "Copied results to ../llm-benchmarks/text-generation/"
