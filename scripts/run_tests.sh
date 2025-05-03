#!/usr/bin/env bash
# filepath: scripts/run_tests.sh
#
# Test runner script for synsatipy-devel
#
# This script runs both unit tests (via pytest) and executes Jupyter
# notebooks in the docs/examples directory to ensure they run without errors.

set -e  # Exit on error

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="$PROJECT_ROOT/synsatipy/tests"
NOTEBOOKS_DIR="$PROJECT_ROOT/docs/examples"

echo $TEST_DIR

# Default values
VERBOSE=false
RUN_UNIT_TESTS=false
RUN_NOTEBOOKS=false
RUN_ALL=false
SPECIFIC_TEST=""

# Print usage
function print_usage {
    echo "Usage: $(basename $0) [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --unit-tests        Run unit tests"
    echo "  --notebooks         Run Jupyter notebooks"
    echo "  --all               Run all tests"
    echo "  -v, --verbose       Verbose output"
    echo "  --test TEST         Run a specific test file or directory"
    echo "  -h, --help          Display this help message"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --unit-tests)
            RUN_UNIT_TESTS=true
            shift
            ;;
        --notebooks)
            RUN_NOTEBOOKS=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --test)
            SPECIFIC_TEST="$2"
            RUN_UNIT_TESTS=true
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            print_usage
            exit 1
            ;;
    esac
done

# If no specific option is provided, run all tests
if [[ "$RUN_ALL" == "false" && "$RUN_UNIT_TESTS" == "false" && "$RUN_NOTEBOOKS" == "false" && -z "$SPECIFIC_TEST" ]]; then
    RUN_ALL=true
fi

# Run unit tests with pytest
function run_unit_tests {
    echo "========================================================================"
    echo "Running unit tests with pytest"
    echo "========================================================================"
    
    PYTEST_CMD="pytest"
    
    if [[ "$VERBOSE" == "true" ]]; then
        PYTEST_CMD="$PYTEST_CMD -v"
    fi
    
    if [[ -n "$SPECIFIC_TEST" ]]; then
        PYTEST_CMD="$PYTEST_CMD $SPECIFIC_TEST"
    else
        PYTEST_CMD="$PYTEST_CMD $TEST_DIR"
    fi
    
    echo "Running: $PYTEST_CMD"
    $PYTEST_CMD
    return $?
}

# Run a single Jupyter notebook
function run_notebook {
    local notebook=$1
    echo "Running notebook: $notebook"
    
    if jupyter nbconvert --execute --to notebook "$notebook"; then
        if [[ "$VERBOSE" == "true" ]]; then
            echo "✓ Notebook $(basename "$notebook") completed successfully"
        fi
        return 0
    else
        echo "❌ Notebook $(basename "$notebook") failed"
        return 1
    fi
}

# Run all Jupyter notebooks
function run_all_notebooks {
    echo "========================================================================"
    echo "Running Jupyter notebooks in docs/examples"
    echo "========================================================================"
    
    # Get list of notebooks
    NOTEBOOKS=$(find "$NOTEBOOKS_DIR" -type f -name "*.ipynb" -not -path "*/\.*" | sort)    
    
    if [[ -z "$NOTEBOOKS" ]]; then
        echo "No notebooks found in $NOTEBOOKS_DIR"
        return 0
    fi
    
    NOTEBOOK_COUNT=$(echo "$NOTEBOOKS" | wc -l)
    echo "Found $NOTEBOOK_COUNT notebooks"
    
    # Variable to track overall success
    local all_success=true
    
    for notebook in $NOTEBOOKS; do
        if [[ "$VERBOSE" == "true" ]]; then
            echo "Processing $(basename "$notebook")..."
        fi
        
        if ! run_notebook "$notebook"; then
            all_success=false
        fi
    done
    
    if [[ "$all_success" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Variable to track exit code
EXIT_CODE=0

# Run the selected tests
if [[ "$RUN_ALL" == "true" || "$RUN_UNIT_TESTS" == "true" || -n "$SPECIFIC_TEST" ]]; then
    run_unit_tests
    UNIT_RESULT=$?
    EXIT_CODE=$((EXIT_CODE | UNIT_RESULT))
fi

if [[ "$RUN_ALL" == "true" || "$RUN_NOTEBOOKS" == "true" ]]; then
    run_all_notebooks
    NOTEBOOK_RESULT=$?
    EXIT_CODE=$((EXIT_CODE | NOTEBOOK_RESULT))
fi

exit $EXIT_CODE
