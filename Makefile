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

.PHONY: all setup java python clean visualize dashboard cleanup auto-visualize monitor

# Run ALL experiments (setup + java + python in tmux)
all: setup
	bash $(SCRIPTS_DIR)/run_all.sh

# Install dependencies (Java, Maven, Python libs)
setup:
	bash $(SCRIPTS_DIR)/setup_dependencies.sh

#############################
# JAVA PROJECTS
#############################

java: nondex

nondex:
	@for proj in $(JAVA_PROJECTS); do \
		echo "=== Running NonDex on $$proj ==="; \
		bash $(SCRIPTS_DIR)/run_nondex.sh $(EXPERIMENT_DIR)/$$proj; \
	done

#############################
# PYTHON PROJECTS
#############################

python:
	@for proj in $(PYTHON_PROJECTS); do \
		echo "=== Running pytest flaky detection on $$proj ==="; \
		bash $(SCRIPTS_DIR)/run_py_flaky_detection.sh $(EXPERIMENT_DIR)/$$proj $(PYTHON_TEST_ROUNDS); \
	done

#############################
# VISUALIZATION
#############################

visualize:
	bash $(SCRIPTS_DIR)/run_visualization.sh results visualization/reports all

auto-visualize:
	bash $(SCRIPTS_DIR)/run_visualization.sh results visualization/reports all true

dashboard:
	bash $(SCRIPTS_DIR)/run_visualization.sh results visualization/reports dashboard

#############################
# CLEAN
#############################

clean:
	rm -rf results/*

cleanup:
	bash $(SCRIPTS_DIR)/cleanup.sh

monitor:
	bash $(SCRIPTS_DIR)/monitor_tests.sh
