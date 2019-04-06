#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Developers: Mir, A. and Mahdi Rahbar
# Version: 0.1 - 2019-03-20
# License: GNU General Public License v3.0

from PyQt5.QtCore import QObject, pyqtSlot
from sklearn.model_selection import train_test_split, KFold, ParameterGrid
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from libtsvm.estimators import TSVM, LSTSVM
from libtsvm.mc_scheme import OneVsAllClassifier, OneVsOneClassifier
from datetime import datetime
import numpy as np
import time

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
        
    problem_type : str, {'binary', 'multiclass'}
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

    def tt_validator(self, dict_param):
        
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
        
        # Set parameters of the underlying estimator in the multiclass classifier
        self.estimator.estimator.set_params(**dict_param)

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

        if self.problem_type == 'binary':

            if self.validator[0] == 'CV':

                return self.cv_validator

            elif self.validator[0] == 't_t_split':

                return self.tt_validator

        elif self.problem_type == 'multiclass':

            if self.validator[0] == 'CV':

                return self.cv_validator_mc


def search_space(kernel_type, search_type, C1_range, C2_range, u_range, \
                 step=1):

    """
    It generates all combination of search elements based on the given range of 
    hyperparameters.
    
    Parameters
    ----------
    kernel_type : str, {'linear', 'RBF'}
        Type of the kernel function which is either 'linear' or 'RBF'.
        
    search_type : str, {'full', 'partial'}
        Type of search space
    
    C1_range : tuple
        Lower and upper bound for C1 penalty parameter.
    
    C2_range : tuple
        Lower and upper bound for C2 penalty parameter.
        
    u_range : tuple
        Lower and upper bound for gamma parameter.
          
    step : int, optinal (default=1)
        Step size to increase power of 2. 
    
    Returns
    -------
    list
        Search elements.
        
    Examples
    --------
    """

    c1_range = [2**i for i in np.arange(C1_range[0], C1_range[1]+1, step,
                                         dtype=np.float)]
    c2_range = [2**i for i in np.arange(C2_range[0], C2_range[1]+1, step,
                                         dtype=np.float)]
    
    gamma_range = [2**i for i in np.arange(u_range[0], u_range[1]+1, step,
                   dtype=np.float)] if kernel_type == 'RBF' else [1]
    
    # In full search, C1 and C2 is not same.
    if search_type == 'full':
        
        param_grid = ParameterGrid({'C1': c1_range, 'C2': c2_range,
                                    'gamma': gamma_range})

    elif search_type == 'partial':
        
        # TODO: It will be implemeneted later!
        pass

    return list(param_grid)


class ThreadGS(QObject):
    """
    It runs the Grid Search in a separate Thread.
    
    Parameters
    ----------
    usr_input : object
        An instance of :class:`UserInput` class which holds the user input.
    """
    
    def __init__(self, usr_input):
        
        super(ThreadGS, self).__init__()
        self.usr_input = usr_input
        
#    def __del__(self):
#        
#        self.wait()
    
    @pyqtSlot()
    def run_gs(self):
        """
        Runs grid search for the selected classifier on specified hyper-parameters.
        """
        
        func_eval, search_space = initialize(self.usr_input)
        
        result_list = []
        max_acc, max_acc_std = 0, 0
    
        search_total = len(search_space)
        #self.gs_progress_bar.setRange(0, search_total)

        start_time = datetime.now()
    
        run = 1
    
        # Ehaustive Grid search for finding optimal parameters
        for element in search_space:
    
            try:
    
                acc, acc_std, result = func_eval(element)
    
                # For debugging purpose
                #print('Acc: %.2f+-%.2f | params: %s' % (acc, acc_std, str(result)))
    
                result_list.append(result)
    
                # Save best accuracy
                if acc > max_acc:
                    
                    max_acc = acc
                    max_acc_std = acc_std       
                
                elapsed_time = datetime.now() - start_time
                
                # Update info on screen
                #self.best_acc.setText("%.2f+-%.2f" % (max_acc, max_acc_std))
                #self.acc.setText("%.2f+-%.2f" % (acc, acc_std))
                #self.gs_progress_bar.setValue(run)
    
                run = run + 1
    
            # Some parameters cause errors such as Singular matrix        
            except np.linalg.LinAlgError:
            
                run = run + 1
        
        print("Best Acc: %.2f+-%.2f" % (max_acc, max_acc_std))


def initialize(user_input_obj):
    """
    It passes a user's input to the functions and classes for solving a
    classification task. The steps that this function performs can be summarized
    as follows:
        
    #. Specifies a TwinSVM classifier based on the user's input.
    #. Chooses an evaluation method for assessment of the classifier.
    #. Computes all the combination of search elements.
    #. Computes the evaluation metrics for all the search element using grid search.
    #. Saves the detailed classification results in a spreadsheet file (Excel).
    
    Parameters
    ----------
    user_input_obj : object 
        An instance of :class:`UserInput` class which holds the user input.
        
    Returns
    -------
    object
        The evalution method.
    
    dict
        Grids of search elements.
    """
    
    clf_obj = None
    
    if user_input_obj.clf_type == 'tsvm':
        
        clf_obj = TSVM(user_input_obj.kernel_type, user_input_obj.rect_kernel)
        
    elif user_input_obj.clf_type == 'lstsvm':
        
        clf_obj = LSTSVM(user_input_obj.kernel_type, user_input_obj.rect_kernel)
        
    if user_input_obj.class_type == 'multiclass':
        
        if user_input_obj.mc_scheme == 'ova':
            
            clf_obj = OneVsAllClassifier(clf_obj)
            
        elif user_input_obj.mc_scheme == 'ovo':
            
            clf_obj = OneVsOneClassifier(clf_obj)
            
    eval_method = Validator(user_input_obj.X_train, user_input_obj.y_train,
                            user_input_obj.class_type, user_input_obj.test_method_tuple,
                            clf_obj)

    search_elem = search_space(user_input_obj.kernel_type, 'full',
                               user_input_obj.C1_range, user_input_obj.C2_range,
                               user_input_obj.u_range)
    
    return eval_method.choose_validator(), search_elem   
    