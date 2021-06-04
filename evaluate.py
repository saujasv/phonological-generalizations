import json
import argparse
import os
from utils.evaluation import evaluate_problem
from utils.problem import Problem

def evaluate(args):
    problems = os.listdir(args.answers_dir)
    metrics = list()
    for prob_name in problems:
        try:
            prob = Problem.from_JSON(os.path.join(args.problems_dir, prob_name))
            sol = Problem.from_JSON(os.path.join(args.solutions_dir, prob_name))
            ans = Problem.from_JSON(os.path.join(args.answers_dir, prob_name))
            prob_metrics = evaluate_problem(prob, ans, sol)
            prob_metrics['name'] = prob_name
            metrics.append(prob_metrics)
        except FileNotFoundError:
            print("{} not found!".format(prob_name))
    
    json.dump(metrics, args.metrics_file, indent=4)
    print("{} problems evaluated".format(len(metrics)))

def aggregate(args):
    metrics = json.load(args.metrics_file)
    count = 0
    threshold = {"0.5": 0, "0.75": 0, "1.0": 0}
    fields = ['wer', 'cer', 'sample_averaged_cer', 'total F', 'total precision', 'total recall', 'exact']
    average_metrics = {f: 0 for f in fields}
    metric_counts = {f: 0 for f in fields}
    for m in metrics:
        if args.filter:
            if args.filter == m['type']:
                count += 1
                if m['exact'] >= 0.5:
                    threshold["0.5"] += 1
                if m['exact'] >= 0.75:
                    threshold["0.75"] += 1
                if m['exact'] >= 1:
                    threshold["1.0"] += 1
                for f in fields:
                    if m['type'] == "stress" and f == "total F":
                        continue
                    average_metrics[f] += m[f]
                    metric_counts[f] += 1
        else:
            count += 1
            if m['exact'] >= 0.5:
                    threshold["0.5"] += 1
            if m['exact'] >= 0.75:
                threshold["0.75"] += 1
            if m['exact'] >= 1:
                threshold["1.0"] += 1
            for f in fields:
                if m['type'] == "stress" and f == "total F":
                    continue
                average_metrics[f] += m[f]
                metric_counts[f] += 1
    
    for f in fields:
        if metric_counts[f] > 0:
            average_metrics[f] = average_metrics[f] / metric_counts[f]
        else:
            average_metrics[f] = 0
    
    average_metrics[">=0.5"] = threshold["0.5"]
    average_metrics[">=0.75"] = threshold["0.75"]
    average_metrics[">=1.0"] = threshold["1.0"]
    
    print(*["{} = {}".format(k, v) for k, v in average_metrics.items()], sep='\n', end='\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(help='mode in which to run')
    
    parser_eval = subparsers.add_parser('evaluate', help='evaluate a set of answers given the problems and the solutions\nNOTE: names of files in each directory have to be the same')
    parser_eval.add_argument("problems_dir", type=str, help="Path to directory where problem files are contained")
    parser_eval.add_argument("solutions_dir", type=str, help="Path to directory where solutions files are contained")
    parser_eval.add_argument("answers_dir", type=str, help="Path to directory where answers files are contained")
    parser_eval.add_argument("metrics_file", type=argparse.FileType('w'), help="JSON file in which metrics are written")
    parser_eval.set_defaults(func=evaluate)
    
    parser_aggr = subparsers.add_parser('aggregate', help='aggregate metrics across a set of evaluated problems')
    parser_aggr.add_argument('metrics_file', type=argparse.FileType('r'), help='JSON file in which metrics are written')
    parser_aggr.add_argument('--unsolved', type=int, default=0, help='number of unsolved problems')
    parser_aggr.add_argument('--filter', type=str, help='type of problems to aggregate results for')
    parser_aggr.set_defaults(func=aggregate)

    args = parser.parse_args()
    args.func(args)