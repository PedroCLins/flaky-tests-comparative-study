# Known Issues with Test Projects

## Python Projects

### ✅ Working Projects
- **httpie**: Fully functional (20 rounds completed)
- **flask**: Fully functional (20 rounds completed)

### ⚠️ Fixed Projects (Need Specific Dependencies)
- **black**: Requires `d` extra for `aiohttp` dependency
  - Fix: Install with `pip install -e ".[d,test,dev]"`
  
- **httpx**: Requires async dependencies
  - Fix: Install with `pip install -e ".[http2,brotli]"`
  
- **celery**: Uses `requirements/dev.txt` instead of extras
  - Fix: Script now handles this correctly

## Java Projects

### ✅ Working Projects
- **commons-codec**: Fully functional

### ⚠️ Projects with Known Build Issues

#### commons-lang
- Status: Should work but may be slow
- Issue: None identified yet
- Action: Retry

#### commons-collections  
- Status: Should work
- Issue: Not tested yet
- Action: Retry

#### guava
- Status: **BUILD FAILURE**
- Issue: Module compilation error - `module not found: com.google.common`
- Root Cause: Complex multi-module Maven project with Java 9+ module system
- Recommendation: **Skip this project** - requires significant build configuration

#### retrofit
- Status: **MISSING ANDROID SDK**
- Issue: Requires `ANDROID_HOME` environment variable and Android SDK
- Root Cause: Android library project
- Fix Options:
  1. Install Android SDK and set `ANDROID_HOME`
  2. **Skip this project** (recommended unless Android testing is needed)

## Summary

### Recommended Action
1. ✅ Run Python projects: black, celery, httpx (fixed with new script)
2. ✅ Run Java projects: commons-lang, commons-collections (should work)
3. ❌ Skip: guava (complex build), retrofit (needs Android SDK)

### Success Rate Target
- Python: 5/5 projects (100%)
- Java: 3/5 projects (60% - skip guava & retrofit)
- Overall: 8/10 projects (80%)

## Commands

```bash
# Run only failed Python projects (quick - ~30 min)
make retry-python

# Run only failed Java projects (slower - ~1 hour)
make retry-java

# Run all failed projects
make retry-failed
```
