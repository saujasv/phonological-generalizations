This repository contains the dataset used in _Sample-efficient Linguistic Generalizations through Program Synthesis: Experiments with Phonology Problems_ (SIGMORPHON 2021).

[\[ACL Anthology\]](https://aclanthology.org/2021.sigmorphon-1.7/) [\[arXiv\]](https://arxiv.org/abs/2106.06566)

## Dataset
The dataset is in the `data/` folder, with problems in `data/problems` and solutions in `data/solutions`. Each problem and solution is presented as a JSON file with the following fields

```
{
    "languages": <list>, // list of languages present in the problem
    "families": <list>, // list of the family to which each language belongs
    "type": <string>, // Type of problem: morphology/multilingual/transliteration/stress
    "columns": <list>, // Name of each column in the data table
    "data": <list of lists>, // The matrix of words in the problem, each appearing as a space-separated sequence of tokens
    "notes": <string>, // Notes accompanying the problem
    "features": <dictionary of dictionaries> // A dictionary that maps tokens to sets of key-value pairs where the key
                                             // is a feature name string, and the value is boolean
}
```

In the problems, test set entries are presented as `?`.

## Evaluation scripts
You may write your own models to solve these problems, and fill in the slots marked `?` in the problem to generate an JSON answer file with the same name (in a different directory) for that problem, leaving all other elements of the problem JSON file unchanged. Then, the metrics may be computed with the following command:

```
python evaluate.py evaluate data/problems data/solutions <answers_dir> <metrics_file>
```

To compute the problem-wise metrics for all problems in `answers_dir` and store them in a JSON `metrics_file`. To aggregate the scores for multiple problems, you may run

```
python evaluate.py aggregate <metrics_file> [--unsolved <n>] [--filter <morphology/multilingual/transliteration/stress>]
```

to obtain aggregate scores for all problems in `metrics_file`, assuming `n` problems have not been solved (score of 0). Additionally, aggregate scores for each type of problem may be obtained by specifying a `filter`.
