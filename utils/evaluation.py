from jiwer import wer
from collections import defaultdict
from .chrF import computeChrF

def evaluate_problem(problem, answer, solution):
    if not problem.test_set:
        raise ValueError("Problem doesn't have any test samples")

    if not len(problem.data) == len(answer.data) == len(solution.data) \
        or not len(problem.data[0]) == len(answer.data[0]) == len(solution.data[0]):
        raise ValueError("Data table shapes do not match: {}".format(problem.data[0]))

    test_idx = [(i, j) for i in range(len(problem.data)) 
                for j in range(len(problem.data[0])) if problem.data[i][j].strip() == '?']
    
    testing_pairs = [(solution.data[i][j], answer.data[i][j]) for i, j in test_idx]

    problem_cer = 0
    total_cer = 0
    problem_characters = 0
    problem_we = 0

    for truth, hypothesis in testing_pairs:
        cer = wer(truth, hypothesis)
        sample_characters = len(truth.split(" "))
        sample_cer = float(cer) * sample_characters
        total_cer += cer
        problem_cer += sample_cer
        problem_characters += sample_characters
        if truth != hypothesis:
            problem_we += 1
    
    word_metrics, chrf_metrics = computeChrF([p[0] for p in testing_pairs], [p[1] for p in testing_pairs], 2, 1)

    return {
        'type': problem.type,
        'wer': problem_we / len(testing_pairs),
        'cer': problem_cer / problem_characters,
        'sample_averaged_cer': total_cer / len(testing_pairs),
        'correct': len(testing_pairs) - problem_we,
        'exact': (len(testing_pairs) - problem_we) / len(testing_pairs),
        'incorrect': problem_we,
        'total F': chrf_metrics['total F'],
        'average total F': chrf_metrics['average total F'], 
        'total precision': chrf_metrics['total precision'], 
        'total recall': chrf_metrics['total recall']
    }