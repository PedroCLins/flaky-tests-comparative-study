#############################
# CONFIG
#############################

# Load environment variables from .env file
ifneq (,$(wildcard .env))
    include .env
    export
endif

#############################
# GENERAL TARGETS
#############################

.PHONY: all setup java python clean

# Run ALL experiments (setup + java + python)
all: setup java python

# Install dependencies (Java, Maven, Python libs)
setup:
	bash $(SCRIPTS_DIR)/setup_dependencies.sh

#############################
# JAVA PROJECTS
#############################

java: nondex idflakies

nondex:
	@for proj in $(JAVA_PROJECTS); do \
		echo "=== Running NonDex on $$proj ==="; \
		bash $(SCRIPTS_DIR)/run_nondex.sh $(EXPERIMENT_DIR)/$$proj; \
	done

idflakies:
	@for proj in $(JAVA_PROJECTS); do \
		echo "=== Running iDFlakies on $$proj ==="; \
		bash $(SCRIPTS_DIR)/run_idflakies.sh $(EXPERIMENT_DIR)/$$proj; \
	done

#############################
# PYTHON PROJECTS
#############################

python:
	@for proj in $(PYTHON_PROJECTS); do \
		echo "=== Running pytest flaky detection on $$proj ==="; \
		bash $(SCRIPTS_DIR)/run_py_flaky_detection.sh $(EXPERIMENT_DIR)/$$proj 20; \
	done

#############################
# CLEAN
#############################

clean:
	rm -rf results/*
