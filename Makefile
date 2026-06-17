.PHONY: build generate etl split

build:
	docker build -t amlsim services/amlsim/

generate:
	bash scripts/make_data.sh $(SIZE) $(SEED)

etl:
	bash scripts/etl.sh

split:
	bash scripts/split.sh
