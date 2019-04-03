#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Developers: Mir, A. and Mahdi Rahbar
# Version: 0.1 - 2019-03-20
# License: GNU General Public License v3.0


from sklearn.model_selection import train_test_split, KFold, ParameterGrid
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
import numpy as np


def eval_metrics(y_true, y_pred):
    """
    It computes common evaluation metrics such as Accuracy, Recall, Precision,
    F1-measure, and elements of the confusion matrix.

    Parameters
    ----------
    y_true : array-like
        Target values of samples.

    y_pred : array-like
        Predicted class lables.

    Returns
    -------
    tp : int
        True positive.

    tn : int
        True negative.

    fp : int
        False positive.

    fn : int
        False negative.

    accuracy : float
        Overall accuracy of the model.

    recall_p : float
        Recall of positive class.

    precision_p : float
        Precision of positive class.

    f1_p : float
        F1-measure of positive class.

    recall_n : float
        Recall of negative class.

    precision_n : float
        Precision of negative class.

    f1_n : float
        F1-measure of negative class.
    """

    # Elements of confusion matrix
    tp, tn, fp, fn = 0, 0, 0, 0

    for i in range(y_true.shape[0]):

        # True positive
        if y_true[i] == 1 and y_pred[i] == 1:

            tp = tp + 1

        # True negative
        elif y_true[i] == -1 and y_pred[i] == -1:

            tn = tn + 1

        # False positive
        elif y_true[i] == -1 and y_pred[i] == 1:

            fp = fp + 1

        # False negative
        elif y_true[i] == 1 and y_pred[i] == -1:

            fn = fn + 1

    # Compute total positives and negatives
    positives = tp + fp
    negatives = tn + fn

    # Initialize
    accuracy = 0
    # Positive class
    recall_p = 0
    precision_p = 0
    f1_p = 0
    # Negative class
    recall_n = 0
    precision_n = 0
    f1_n = 0

    try:

        accuracy = (tp + tn) / (positives + negatives)
        # Positive class
        recall_p = tp / (tp + fn)
        precision_p = tp / (tp + fp)
        f1_p = (2 * recall_p * precision_p) / (precision_p + recall_p)

        # Negative class
        recall_n = tn / (tn + fp)
        precision_n = tn / (tn + fn)
        f1_n = (2 * recall_n * precision_n) / (precision_n + recall_n)

    except ZeroDivisionError:

        pass  # Continue if division by zero occured

    return tp, tn, fp, fn, accuracy * 100, recall_p * 100, precision_p * 100, f1_p * 100, \
        recall_n * 100, precision_n * 100, f1_n * 100
        

class Validator:

    """
    It evaluates a TSVM-based estimator based on the specified evaluation method.
    
    Parameters
    ----------
    X_train : array-like, shape (n_samples, n_features)
        Training feature vectors, where n_samples is the number of samples
        and n_features is the number of features.
        
    y_train : array-like, shape (n_samples,)
        Target values or class labels.
        
    problem_type : str, {'bin', 'mc'}
        Type of the classification problem. It is either binary (bin) or
        multi-classification (mc)
        
    validator_type : tuple
        A two-element tuple which contains type of evaluation method and its
        parameter. Example: ('CV', 5) -> 5-fold cross-validation,
        ('t_t_split', 30) -> 30% of samples for test set.
        
    estimator : estimator object
        A TSVM-based estimator which inherits from the :class:`BaseTSVM`.
    """

    def __init__(self, X_train, y_train, problem_type, validator_type,
                 estimator):

        self.train_data = X_train
        self.labels_data = y_train
        self.problem_type = problem_type
        self.validator = validator_type
        self.estimator = estimator

    def cv_validator(self, dict_param):

        """
        It evaluates a TSVM-based estimator using the cross-validation method.
        
        Parameters
        ----------
        dict_param : dict 
            Values of hyper-parameters for a TSVM-based estimator
            
        Returns
        -------
        float
            Mean accuracy of the model.
            
        float
            Standard deviation of accuracy.
            
        dict
            Evaluation metrics such as Recall, Percision and F1-measure for both
            classes as well as elements of the confusion matrix.
        """
        
        self.estimator.set_params(**dict_param)
        
        k_fold = KFold(self.validator[1])    

        # Store result after each run
        mean_accuracy = []
        # Postive class
        mean_recall_p, mean_precision_p, mean_f1_p = [], [], []
        # Negative class
        mean_recall_n, mean_precision_n, mean_f1_n = [], [], []
        
        # Count elements of confusion matrix
        tp, tn, fp, fn = 0, 0, 0, 0
        
        for train_index, test_index in k_fold.split(self.train_data):

            # Extract data based on index created by k_fold
            X_train = np.take(self.train_data, train_index, axis=0) 
            X_test = np.take(self.train_data, test_index, axis=0)

            y_train = np.take(self.labels_data, train_index, axis=0)
            y_test = np.take(self.labels_data, test_index, axis=0)

            self.estimator.fit(X_train, y_train)

            output = self.estimator.predict(X_test)

            accuracy_test = eval_metrics(y_test, output)

            mean_accuracy.append(accuracy_test[4])
            # Positive cass
            mean_recall_p.append(accuracy_test[5])
            mean_precision_p.append(accuracy_test[6])
            mean_f1_p.append(accuracy_test[7])
            # Negative class    
            mean_recall_n.append(accuracy_test[8])
            mean_precision_n.append(accuracy_test[9])
            mean_f1_n.append(accuracy_test[10])

            # Count
            tp = tp + accuracy_test[0]
            tn = tn + accuracy_test[1]
            fp = fp + accuracy_test[2]
            fn = fn + accuracy_test[3]

        return np.mean(mean_accuracy), np.std(mean_accuracy), {**{'accuracy': np.mean(mean_accuracy),
                      'acc_std': np.std(mean_accuracy),'recall_p': np.mean(mean_recall_p),
                      'r_p_std': np.std(mean_recall_p), 'precision_p': np.mean(mean_precision_p),
                      'p_p_std': np.std(mean_precision_p), 'f1_p': np.mean(mean_f1_p),
                      'f1_p_std': np.std(mean_f1_p), 'recall_n': np.mean(mean_recall_n),
                      'r_n_std': np.std(mean_recall_n), 'precision_n': np.mean(mean_precision_n),
                      'p_n_std': np.std(mean_precision_n), 'f1_n': np.mean(mean_f1_n),
                      'f1_n_std': np.std(mean_f1_n), 'tp': tp, 'tn': tn, 'fp': fp,
                      'fn': fn}, **dict_param}

    def split_tt_validator(self, dict_param):
        
        """
        It evaluates a TSVM-based estimator using the train/test split method.
        
        Parameters
        ----------
        dict_param : dict
            Values of hyper-parameters for a TSVM-based estimator
            
        Returns
        -------
        float
            Accuracy of the model.
            
        float
            Zero standard deviation.
            
        dict
            Evaluation metrics such as Recall, Percision and F1-measure for both
            classes as well as elements of the confusion matrix.
        """

        self.estimator.set_params(**dict_param)

        X_train, X_test, y_train, y_test = train_test_split(self.train_data, \
                                           self.labels_data, test_size=self.validator[1], \
                                           random_state=42)

        # fit - create two non-parallel hyperplanes
        self.estimator.fit(X_train, y_train)

        output = self.estimator.predict(X_test)

        tp, tn, fp, fn, accuracy, recall_p, precision_p, f1_p, recall_n, precision_n, \
        f1_n = eval_metrics(y_test, output)

       # m_a=0, m_r_p=1, m_p_p=2, m_f1_p=3, k=4, c1=5, c2=6, gamma=7,
       # m_r_n=8, m_p_n=9, m_f1_n=10, tp=11, tn=12, fp=13, fn=14,
        return accuracy, 0.0, {**{'accuracy': accuracy, 'recall_p': recall_p,
               'precision_p': precision_p, 'f1_p': f1_p, 'recall_n': recall_n,
               'precision_n': precision_n, 'f1_n': f1_n, 'tp': tp, 'tn': tn,
               'fp': fp, 'fn': fn}, **dict_param}

    def cv_validator_mc(self, dict_param):

        """
        It evaluates a multi-class TSVM-based estimator using the cross-validation.
        
        Parameters
        ----------
        dict_param : dict 
            Values of hyper-parameters for a multi-class TSVM-based estimator.
            
        Returns
        -------
        float
            Accuracy of the model.
            
        float
            Zero standard deviation.
            
        dict
            Evaluation metrics such as Recall, Percision and F1-measure.
        """

        self.estimator.set_params(**dict_param)

        k_fold = KFold(self.validator[1])    

        # Store result after each run
        mean_accuracy = []
        
        # Evaluation metrics
        mean_recall, mean_precision, mean_f1 = [], [], []
        
        for train_index, test_index in k_fold.split(self.train_data):

            # Extract data based on index created by k_fold
            X_train = np.take(self.train_data, train_index, axis=0) 
            X_test = np.take(self.train_data, test_index, axis=0)

            y_train = np.take(self.labels_data, train_index, axis=0)
            y_test = np.take(self.labels_data, test_index, axis=0)

            self.estimator.fit(X_train, y_train)

            output = self.estimator.predict(X_test)

            mean_accuracy.append(accuracy_score(y_test, output) * 100)
            mean_recall.append(recall_score(y_test, output, average='micro') * 100)
            mean_precision.append(precision_score(y_test, output, average='micro') * 100)
            mean_f1.append(f1_score(y_test, output, average='micro') * 100)

        return np.mean(mean_accuracy), np.std(mean_accuracy), {**{'accuracy':
               np.mean(mean_accuracy), 'acc_std': np.std(mean_accuracy),
               'micro_recall': np.mean(mean_recall), 'm_rec_std': np.std(mean_recall),
               'micro_precision': np.mean(mean_precision), 'm_prec_std':
               np.std(mean_precision), 'mirco_f1': np.mean(mean_f1), 'm_f1_std':
               np.std(mean_f1)}, **dict_param}

    def choose_validator(self):

        """
        It selects an appropriate evaluation method based on the input
        paramters.
        
        Returns
        -------
        object
            An evaluation method for assesing a TSVM-based estimator's performance.
        """

        if self.problem_type == 'bin':

            if self.validator[0] == 'CV':

                return self.cv_validator

            elif self.validator[0] == 't_t_split':

                return self.split_tt_validator

        elif self.problem_type == 'mc':

            if self.validator[0] == 'CV':

                return self.cv_validator_mc
