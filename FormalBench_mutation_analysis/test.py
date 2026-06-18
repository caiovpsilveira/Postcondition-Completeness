from FormalBench.evaluation import eval_consistency
from FormalBench.evaluation import eval_completeness

for difficulty in ["easy", "medium", "hard"]:
    # Evaluate the consistency of the specifications
    # spec_dir: str, the directory where the specifications are stored
    # analysis_dir: str, the directory where the analysis results will be stored
    success_rate, failure_rate, results = eval_consistency(
                                            spec_dir = f"dataset_v1_annotated/{difficulty}", 
                                            analysis_dir = f"analysis_results/{difficulty}/",
                                        )

    print("Success rate: ", success_rate)
    print("Failure rate: ", failure_rate)

    # Evaluate the completeness of the specifications
    # save_dir: str, the directory where the mutation and completeness results will be stored
    avg_coverage, coverage_results, inconsistent_instances = eval_completeness(
                                            spec_dir = f"dataset_v1_annotated/{difficulty}", 
                                            analysis_dir = f"analysis_results/{difficulty}/",
                                            save_dir = f"completeness_results/{difficulty}/",
                                            language="java",
                                            n_proc=8,
                                            timeout=300
                                        )

    print("Average coverage: ", avg_coverage)
    print("Inconsistent instances: ", inconsistent_instances)
