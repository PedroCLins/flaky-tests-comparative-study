# Recommended Projects for Flaky Test Detection

This document lists projects known to have flaky tests, ideal for comparative studies.

## Java Projects (for NonDex)

### Already Cloned
- ✅ `commons-lang` - Apache Commons Language utilities (WORKING - flaky tests detected!)
- ✅ `mockito` - Mocking framework

### Recommended to Add

#### From Apache Commons (Known for Order-Dependent Tests)
```bash
cd ../flaky-tests-experiments
git clone https://github.com/apache/commons-collections.git
git clone https://github.com/apache/commons-codec.git
git clone https://github.com/apache/commons-io.git
```

#### Other Popular Projects with Flaky Tests
```bash
cd ../flaky-tests-experiments
git clone https://github.com/google/guava.git
git clone https://github.com/square/retrofit.git
git clone https://github.com/FasterXML/jackson-core.git
```

## Python Projects (for pytest-rerun)

### Already Cloned
- ✅ `pandas` - Data analysis (too complex, many errors)
- ✅ `requests` - HTTP library (too complex, many errors)

### Recommended to Add (Smaller, More Manageable)

#### Web Frameworks & Tools
```bash
cd ../flaky-tests-experiments
git clone https://github.com/httpie/httpie.git
git clone https://github.com/pallets/flask.git
git clone https://github.com/psf/black.git
```

#### Task Queues & Async (Known for Timing-Related Flakiness)
```bash
cd ../flaky-tests-experiments
git clone https://github.com/celery/celery.git
git clone https://github.com/encode/httpx.git
```

#### Testing Tools (Meta!)
```bash
cd ../flaky-tests-experiments
git clone https://github.com/pytest-dev/pytest.git
git clone https://github.com/HypothesisWorks/hypothesis.git
```

## Research Datasets

For academic rigor, consider using curated datasets:

### iDFlakies Dataset
Projects specifically selected for flaky test research:
- https://github.com/idoft/iDFlakies-dataset

### FlakeFlagger Dataset
Labeled flaky tests from real projects:
- https://github.com/ucsb-seclab/flakeflagger

## Quick Setup

After cloning new projects, update your `.env`:

```bash
# Java projects (space-separated)
JAVA_PROJECTS=commons-lang commons-collections commons-codec guava

# Python projects (space-separated)  
PYTHON_PROJECTS=httpie flask black
```

Then run:
```bash
make java    # Run NonDex on Java projects
make python  # Run pytest on Python projects (50 rounds each)
```

## Notes

- **Python**: Avoid very large libraries (pandas, numpy, scipy) - they have complex build requirements
- **Java**: Apache Commons projects work well with NonDex
- **Rounds**: Increase test rounds for better detection (see configuration below)
