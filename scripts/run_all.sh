for project in apache-commons-lang mockito; do
    ./scripts/run_nondex.sh "$project"
    ./scripts/run_idflakies.sh "$project"
done

for project in pandas requests; do
    ./scripts/run_py_flaky_detection.sh "$project"
done