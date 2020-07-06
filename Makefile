SHELL := bash
.ONESHELL:
.SHELLFLAGS := -euic
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Variables ###
# Tools
PYTEST           = pytest
BASH             = bash
CONDA            = conda
PYTHON           = python3.8
SNAKEMAKE        = snakemake
CONDA_ACTIVATE   = source $$(conda info --base)/etc/profile.d/conda.sh && conda activate && conda activate

# Paths
TEST_COMMON      = scripts/common_script_ngs_cleaning.py
TEST_CONFIG      = scripts/prepare_config.py
TEST_DESIGN      = scripts/prepare_design.py
SNAKE_FILE       = Snakefile
ENV_YAML         = envs/workflow.yaml
READS_PATH       = '${PWD}/tests/reads'

# Arguments
ENV_NAME         = ngs-cleaning
SNAKE_THREADS    = 1
PYTEST_ARGS      = -vv

# Recipes
default: all-unit-tests


all-unit-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} ${PYTEST_ARGS} ${TEST_CONFIG} ${TEST_DESIGN} ${TEST_COMMON}
.PHONY: all-unit-tests


# Environment building through conda
conda-tests:
	${CONDA_ACTIVATE} base && \
	${CONDA} env create --file ${ENV_YAML} --force && \
	${CONDA} activate ${ENV_NAME}
.PHONY: conda-tests


# Running tests on configuration only
config-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} ${PYTEST_ARGS} ${TEST_CONFIG} && \
	${PYTHON} ${TEST_CONFIG}
.PHONY: config-tests


design-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} ${PYTEST_ARGS} ${TEST_DESIGN} && \
	${PYTHON} ${TEST_DESIGN} ${READS_PATH}
.PHONY: design-tests

test-conda-report.html:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTHON} ${TEST_CONFIG} --workdir tests/ --design tests/design.tsv && \
	${PYTHON} ${TEST_DESIGN} ${READS_PATH} --output ${PWD}/tests/design.tsv --debug && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --printshellcmds --reason --forceall --directory ${PWD}/tests --configfile ${PWD}/tests/config.yaml && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --printshellcmds --reason --forceall --directory ${PWD}/tests --configfile ${PWD}/tests/config.yaml --report test-conda-report.html


clean:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --printshellcmds --reason --forceall --directory ${PWD}/tests --configfile ${PWD}/tests/config.yaml --delete-all-output
.PHONY: clean



# Display pipeline graph
workflow.png:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTHON} ${TEST_CONFIG} --workdir tests/ --design tests/design.tsv && \
	${PYTHON} ${TEST_DESIGN} ${READS_PATH} --output ${PWD}/tests/design.tsv --debug && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --printshellcmds --reason --forceall --directory ${PWD}/tests --configfile ${PWD}/tests/config.yaml --rulegraph | dot -T png > workflow.png

example.png:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTHON} ${TEST_CONFIG} --workdir tests/ --design tests/design.tsv && \
	${PYTHON} ${TEST_DESIGN} ${READS_PATH} --output ${PWD}/tests/design.tsv --debug && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --printshellcmds --reason --forceall --directory ${PWD}/tests --configfile ${PWD}/tests/config.yaml --dag | dot -T png > example.png
