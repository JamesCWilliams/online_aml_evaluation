.PHONY: build generate

build:
	docker build -t amlsim services/amlsim/

generate:
	bash scripts/make_data.sh $(SIZE) $(SEED)
	