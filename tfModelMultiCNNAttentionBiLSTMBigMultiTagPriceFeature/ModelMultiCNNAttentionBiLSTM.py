# -*- coding: utf-8 -*-
"""
Created on 2017/10/16 16:37

@author: 006547
"""

import tensorflow as tf
from tensorflow.contrib import rnn
import json
from ModelSystem.Model import Model
import numpy as np
# from sklearn import preprocessing
from ModelSystem.DeepNNDataSetBig_csf import DeepNNDataSet
import math
import os
# import shutil


class ModelMultiCNNAttentionBiLSTM(Model):
    def __init__(self, paraModel, name, tagName, modelManagement):
        Model.__init__(self, paraModel, name, tagName, modelManagement)
        modelManagement.register(self)

    def train(self, rollingData, outputDict):  # 数据集都是np.array格式
        validationNum = self.paraModel["validationNum"]
        # GPUID = self.paraModel["GPUID"]
        absolutePath = self.paraModel["absolutePath"]
        factorGroup = self.paraModel["factorGroup"]
        priceVolumeFactorIndex = self.paraModel["priceVolumeFactorIndex"]

        trainData = np.array(rollingData["trainData"][:-validationNum])
        validData = np.array(rollingData["trainData"][-validationNum:])
        predictData = np.array(rollingData["predictData"])
        trainSubTag = rollingData["trainSubTag"][:-validationNum]
        validSubTag = rollingData["trainSubTag"][-validationNum:]
        predictSubTag = rollingData["predictSubTag"]
        # 参数设置
        sliceLag = self.paraModel["sliceLag"]
        numFactor = rollingData["trainData"][0].__len__() + priceVolumeFactorIndex.__len__() + 1
        lr = 1e-4
        rnn_keepProbPara = 0.8
        rnn_hiddenSizePara = 256
        conv_len = self.paraModel["conv_len"]
        runStep = 60000
        batchSize = 1000
        checkPeriod = 25

        scale_mean, scale_std = calculateScale(trainData)

        trainNNData = normalizeData(trainData, scale_mean, scale_std)
        validNNData = normalizeData(validData, scale_mean, scale_std)
        predictNNData = normalizeData(predictData, scale_mean, scale_std)

        # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        # os.environ["CUDA_VISIBLE_DEVICES"] = str(GPUID)

        pre_trained_variables = {}
        predictRollingWindow = self.paraModel["predictRollingWindow"]
        if predictRollingWindow == 0.01:
            pre_trained_model_path = absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + "modelCNNRNN" + self.tagName[0] + "Pred" + str(0.2) + 'SliceLag' + str(sliceLag) + '_SavedModelBuilder'
            print('Load model weights from: ', pre_trained_model_path)
            tf.reset_default_graph()
            with tf.Session() as sess:
                tf.saved_model.loader.load(sess, ['model_' + validSubTag[0]['1min'].code[0:6]],
                                           pre_trained_model_path)
                for v in tf.trainable_variables():
                    data = sess.run(v)
                    pre_trained_variables[v.name] = data

        tf.reset_default_graph()
        with tf.Session() as sess:
            triggerRatio = self.paraModel["evaluateModel"]["triggerRatio"]
            riskRatio = self.paraModel["evaluateModel"]["riskRatio"]
            if not os.path.exists(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder'):
                print("Model " + self.backTestUnderlying + " does not exist. Training Model")
                # Create the model
                x = tf.placeholder(tf.float32, [None, sliceLag * numFactor])
                # Define loss and optimizer
                y_ = tf.placeholder(tf.float32, [None, 2])
                # Build the graph for the deep net
                numVariable = [0]
                y_regression, rnn_keepProb = deepnn(x, numVariable, factorGroup, priceVolumeFactorIndex, image_len=sliceLag, factor_num=numFactor,
                                                    conv1_len=conv_len,
                                                    conv1_num=32, pool1_len=2, conv2_len=conv_len, conv2_num=32,
                                                    pool2_len=2,
                                                    conv3_len=conv_len, conv3_num=64, pool3_len=4,
                                                    rnn_hiddenSize=rnn_hiddenSizePara,
                                                    rnn_layerNum=1, regularizationRate=0.001)
                numVariable = numVariable[0]
                print("Number of variables: " + str(numVariable))
                with tf.name_scope('loss'):
                    rmse = tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(y_, y_regression), 2)))
                tf.add_to_collection('losses', rmse)
                loss = tf.add_n(tf.get_collection('losses'))
                with tf.name_scope('adam_optimizer'):
                    train_step = tf.train.AdamOptimizer(learning_rate=lr).minimize(loss)
                sess.run(tf.global_variables_initializer())

                for var in tf.trainable_variables():
                    if var.name in pre_trained_variables:
                        sess.run(tf.assign(var, pre_trained_variables[var.name]))

                trainDeepNNDataSet = DeepNNDataSet(trainNNData, trainSubTag, sliceLag, priceVolumeFactorIndex, self.tagName)
                validDeepNNDataSet = DeepNNDataSet(validNNData, validSubTag, sliceLag, priceVolumeFactorIndex, self.tagName)
                batchValid = validDeepNNDataSet.next_batch(validDeepNNDataSet.num_examples, shuffle=True)
                valid_lossSeries = []
                train_lossSeries = []

                for i in range(runStep):
                    batchTrain = trainDeepNNDataSet.next_batch(batchSize, shuffle=True)
                    if (i+1) % checkPeriod == 0:
                        train_loss = loss.eval(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: 1.0})
                        predict = y_regression.eval(feed_dict={x: batchTrain[0], rnn_keepProb: 1.0}) / 100
                        label = batchTrain[1] / 100
                        predictLongLogic = np.vstack((predict[:, 0] > triggerRatio, predict[:, 1] > riskRatio)).all(0)
                        predictShortLogic = np.vstack((predict[:, 1] < -triggerRatio, predict[:, 0] < -riskRatio)).all(0)
                        train_TriggerTimes = sum(predictLongLogic) + sum(predictShortLogic)
                        if train_TriggerTimes != 0:
                            train_winRate = (sum(label[predictLongLogic, 0] > 0.001) + sum(label[predictShortLogic, 1] < -0.001)) / train_TriggerTimes
                            train_AveReturn = (sum(label[predictLongLogic, 0]) - sum(label[predictShortLogic, 1])) / train_TriggerTimes
                        else:
                            train_winRate = 0
                            train_AveReturn = 0

                        valid_loss = loss.eval(feed_dict={x: batchValid[0], y_: batchValid[1], rnn_keepProb: 1.0})
                        predict = y_regression.eval(feed_dict={x: batchValid[0], rnn_keepProb: 1.0}) / 100
                        label = batchValid[1] / 100
                        predictLongLogic = np.vstack((predict[:, 0] > triggerRatio, predict[:, 1] > riskRatio)).all(0)
                        predictShortLogic = np.vstack((predict[:, 1] < -triggerRatio, predict[:, 0] < -riskRatio)).all(0)
                        valid_TriggerTimes = sum(predictLongLogic) + sum(predictShortLogic)
                        if valid_TriggerTimes != 0:
                            valid_winRate = (sum(label[predictLongLogic, 0] > 0.001) + sum(label[predictShortLogic, 1] < -0.001)) / valid_TriggerTimes
                            valid_AveReturn = (sum(label[predictLongLogic, 0]) - sum(label[predictShortLogic, 1])) / valid_TriggerTimes
                        else:
                            valid_winRate = 0
                            valid_AveReturn = 0

                        print('step %d, training loss %.6f, winRate %.2f, times %d, train AveReturn %.6f, epochs %d; valid loss %.6f, winRate %.2f, times %d, valid AveReturn %.6f' %
                              (i, train_loss, train_winRate, train_TriggerTimes, train_AveReturn, trainDeepNNDataSet.epochs_completed,
                               valid_loss, valid_winRate, valid_TriggerTimes, valid_AveReturn))
                        valid_lossSeries.append(float(valid_loss))
                        train_lossSeries.append(float(train_loss))
                        if valid_loss <= min(valid_lossSeries):

                            sess_variable_weights = {}
                            for v in tf.trainable_variables():
                                data = sess.run(v)
                                sess_variable_weights[v.name] = data

                            print('Model Saved')

                        if (valid_lossSeries.__len__() > 0 and valid_lossSeries.__len__() - 1 - np.argmin(valid_lossSeries) >= trainDeepNNDataSet.num_examples / batchSize / checkPeriod * 2) or i == runStep - 1:
                            if len(sess_variable_weights.keys()) > 0:
                                for v in tf.trainable_variables():
                                    sess.run(tf.assign(v, sess_variable_weights[v.name]))

                            builder = tf.saved_model.builder.SavedModelBuilder(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder')
                            builder.add_meta_graph_and_variables(sess, ['model_' + validSubTag[0]['1min'].code[0:6]])
                            builder.save()

                            with open(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder' + "/ModelSet.json", "w") as f:
                                modelSet = {'mean': scale_mean.tolist(), 'std': scale_std.tolist(), 'ModelInput': self.modelInput, 'WindowSize': sliceLag, 'priceVolumeFactorIndex': priceVolumeFactorIndex}
                                json.dump(modelSet, f)

                            with open(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder' + "/Loss.json", "w") as f:
                                Loss = {'valid_loss': valid_lossSeries, 'train_loss': train_lossSeries}
                                json.dump(Loss, f)
                            print('Stop Training')
                            break
                    train_step.run(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: rnn_keepProbPara})

        tf.reset_default_graph()
        with tf.Session() as sess:
            print("Model " + self.backTestUnderlying + " exists. Loading Model")
            tf.saved_model.loader.load(sess, ['model_' + validSubTag[0]['1min'].code[0:6]], absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder')
            y_regression = sess.graph.get_tensor_by_name('regression/add:0')
            loss = sess.graph.get_tensor_by_name('AddN:0')
            x = sess.graph.get_tensor_by_name('Placeholder:0')
            y_ = sess.graph.get_tensor_by_name('Placeholder_1:0')
            rnn_keepProb = sess.graph.get_tensor_by_name('Placeholder_2:0')

            with open(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder' + "/ModelSet.json", "w") as f:
                modelSet = {'mean': scale_mean.tolist(), 'std': scale_std.tolist(), 'ModelInput': self.modelInput, 'WindowSize': sliceLag, 'priceVolumeFactorIndex': priceVolumeFactorIndex}
                json.dump(modelSet, f)

            trainDeepNNDataSet = DeepNNDataSet(trainNNData, trainSubTag, sliceLag, priceVolumeFactorIndex, self.tagName)
            batchTrain = trainDeepNNDataSet.next_batch(min(40000, trainDeepNNDataSet.num_examples), shuffle=True)
            allTrain_loss = loss.eval(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: 1.0})
            inSamplePredict = y_regression.eval(feed_dict={x: batchTrain[0], rnn_keepProb: 1.0}) / 100
            inSampleLabel = batchTrain[1] / 100
            predictLongLogic = np.vstack((inSamplePredict[:, 0] > triggerRatio, inSamplePredict[:, 1] > riskRatio)).all(0)
            predictShortLogic = np.vstack((inSamplePredict[:, 1] < -triggerRatio, inSamplePredict[:, 0] < -riskRatio)).all(0)
            TriggerTimes = sum(predictLongLogic) + sum(predictShortLogic)
            if TriggerTimes != 0:
                winRate = (sum(inSampleLabel[predictLongLogic, 0] > 0.001) + sum(inSampleLabel[predictLongLogic, 1] < -0.001)) / TriggerTimes
                allTrain_AveReturn = (sum(inSampleLabel[predictLongLogic, 0]) - sum(inSampleLabel[predictLongLogic, 1])) / TriggerTimes
            else:
                winRate = 0
                allTrain_AveReturn = 0
            print('allTrain loss %.6f, winRate %.2f, times %d, allTrain AveReturn %.6f' % (allTrain_loss, winRate, TriggerTimes, allTrain_AveReturn))

            # test_loss = loss.eval(feed_dict={x: batchPredict[0], y_: batchPredict[1], rnn_keepProb: 1.0})
            # outSamplePredict = y_regression.eval(feed_dict={x: batchPredict[0], y_: batchPredict[1], rnn_keepProb: 1.0})[:, 0] / 100
            # 预测太多，需要拆分
            predictDeepNNDataSet = DeepNNDataSet(predictNNData, predictSubTag, sliceLag, priceVolumeFactorIndex, self.tagName)
            batchPredict = predictDeepNNDataSet.next_batch(predictDeepNNDataSet.num_examples, shuffle=False)
            num = int(np.floor(batchPredict[0].shape[0] / 10000))
            res = int(batchPredict[0].shape[0] % 10000)
            test_loss = []
            outSamplePredict = []
            if num > 0:
                for i in range(num):
                    temp1 = loss.eval(feed_dict={x: batchPredict[0][(i * 10000):((i + 1) * 10000), :],
                                                 y_: batchPredict[1][(i * 10000):((i + 1) * 10000), :],
                                                 rnn_keepProb: 1})
                    test_loss.append(temp1)
                    temp2 = y_regression.eval(feed_dict={x: batchPredict[0][(i * 10000):((i + 1) * 10000), :],
                                                         rnn_keepProb: 1}) / 100
                    outSamplePredict += temp2.tolist()
            if res > 0:
                temp1 = loss.eval(feed_dict={x: batchPredict[0][(num * 10000):(num * 10000 + res), :],
                                             y_: batchPredict[1][(num * 10000):(num * 10000 + res), :],
                                             rnn_keepProb: 1})
                test_loss.append(temp1)
                temp2 = y_regression.eval(feed_dict={x: batchPredict[0][(num * 10000):(num * 10000 + res), :],
                                                     rnn_keepProb: 1}) / 100
                outSamplePredict += temp2.tolist()
            outSamplePredict = np.array(outSamplePredict)
            test_loss = float(np.mean(test_loss))

            outSampleLabel = batchPredict[1] / 100
            predictLongLogic = np.vstack((outSamplePredict[:, 0] > triggerRatio, outSamplePredict[:, 1] > riskRatio)).all(0)
            predictShortLogic = np.vstack((outSamplePredict[:, 1] < -triggerRatio, outSamplePredict[:, 0] < -riskRatio)).all(0)
            TriggerTimes = sum(predictLongLogic) + sum(predictShortLogic)
            if TriggerTimes != 0:
                winRate = (sum(outSampleLabel[predictLongLogic, 0] > 0.001) + sum(outSampleLabel[predictLongLogic, 1] < -0.001)) / TriggerTimes
                test_AveReturn = (sum(outSampleLabel[predictLongLogic, 0]) - sum(outSampleLabel[predictLongLogic, 1])) / TriggerTimes
            else:
                winRate = 0
                test_AveReturn = 0
            print('test loss %.6f, winRate %.2f, times %d, test AveReturn %.6f' % (test_loss, winRate, TriggerTimes, test_AveReturn))

        outputDict.update({"model": sess})
        outputDict.update({"trainData": batchTrain[0]})
        outputDict.update({"trainLabel": inSampleLabel})
        outputDict.update({"predictData": batchPredict[0]})
        outputDict.update({"predictLabel": outSampleLabel})
        outputDict.update({"inSamplePredict": inSamplePredict})
        outputDict.update({"outSamplePredict": outSamplePredict})
        outputDict.update({"outSampleSubTag": batchPredict[2]})
        outputDict.update({"numTrainData": trainDeepNNDataSet.num_examples})
        outputDict.update(self.evaluateModel(inSamplePredict, inSampleLabel, "inSample", self.paraModel["evaluateModel"]))
        outputDict.update(self.evaluateModel(outSamplePredict, outSampleLabel, "outSample", self.paraModel["evaluateModel"]))


def deepnn(x, numVariable, factorGroup, priceVolumeFactorIndex, image_len, factor_num, conv1_len, conv1_num, pool1_len, conv2_len, conv2_num, pool2_len,
           conv3_len, conv3_num, pool3_len, rnn_hiddenSize, rnn_layerNum, regularizationRate):
    with tf.name_scope('reshape'):
        x_image = tf.reshape(x, [-1, image_len, factor_num, 1])
        x = []
        for group in factorGroup:
            x.append(tf.slice(x_image, [0, 0, group[0], 0], [-1, image_len, group[1], 1]))
        x_PriceVolumeGroup = tf.slice(x_image, [0, 0, factor_num - priceVolumeFactorIndex.__len__() - 1, 0], [-1, image_len, priceVolumeFactorIndex.__len__() + 1, 1])
        x.append(x_PriceVolumeGroup)
    h_pool3_List = []
    for i in range(x.__len__()):
        h_pool3_List.append(cnn(x[i], 'Group'+str(i), conv1_len, int(x[i].shape[2]), regularizationRate, numVariable, conv1_num, pool1_len,
                                conv2_len, conv2_num, pool2_len, conv3_len, conv3_num, pool3_len))
    h_pool3 = h_pool3_List[0]
    for i in range(1, h_pool3_List.__len__()):
        h_pool3 = tf.concat([h_pool3, h_pool3_List[i]], 3)

    timestep_size = int(math.ceil(math.ceil(math.ceil((image_len - conv1_len + 1) / pool1_len) / pool2_len) / pool3_len))
    x_timeSeries = tf.reshape(h_pool3, [-1, timestep_size, h_pool3.shape[3]])
    batch_size = tf.shape(x_timeSeries)[0]
    rnn_keepProb = tf.placeholder(tf.float32)

    def lstm_cell():
        cell = rnn.LSTMCell(rnn_hiddenSize, reuse=tf.get_variable_scope().reuse)
        return rnn.DropoutWrapper(cell, output_keep_prob=rnn_keepProb)

    # mlstm_cell = rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layerNum)], state_is_tuple=True)
    # init_state = mlstm_cell.zero_state(batch_size, dtype=tf.float32)
    #
    # outputs = list()
    # state = init_state
    # with tf.variable_scope('RNN'):
    #     for timestep in range(timestep_size):
    #         if timestep > 0:
    #             tf.get_variable_scope().reuse_variables()
    #         # 这里的state保存了每一层 LSTM 的状态
    #         (cell_output, state) = mlstm_cell(x_timeSeries[:, timestep, :], state)
    #         outputs.append(cell_output)
    # h_state = outputs[-1]

    x_timeSeries = tf.transpose(x_timeSeries, [1, 0, 2])
    x_timeSeries = tf.reshape(x_timeSeries, [-1, x_timeSeries.shape[2]])
    x_timeSeries = tf.split(x_timeSeries, timestep_size)
    mlstm_fw_cell = rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layerNum)], state_is_tuple=True)
    mlstm_bw_cell = rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layerNum)], state_is_tuple=True)
    fw_state = mlstm_fw_cell.zero_state(batch_size, dtype=tf.float32)
    bw_state = mlstm_bw_cell.zero_state(batch_size, dtype=tf.float32)
    outputs, output_state_fw, output_state_bw = rnn.static_bidirectional_rnn(mlstm_fw_cell, mlstm_bw_cell, x_timeSeries,
                                                                             fw_state, bw_state, dtype=tf.float32)
    # h_state = outputs[-1]

    attention_size = 50

    attention_output = attention(outputs, attention_size, True)

    with tf.name_scope('regression'):
        W_fc = weight_variable([rnn_hiddenSize * 2, 2], regularizationRate, numVariable)
        b_fc = bias_variable([2], numVariable)

        y_regression = tf.matmul(attention_output, W_fc) + b_fc
    return y_regression, rnn_keepProb


def cnn(x, nameScope, conv1_len, factor_num, regularizationRate, numVariable, conv1_num, pool1_len, conv2_len,
        conv2_num, pool2_len, conv3_len, conv3_num, pool3_len):
    with tf.name_scope('conv1' + nameScope):
        W_conv1 = weight_variable([conv1_len, factor_num, 1, conv1_num], regularizationRate, numVariable)
        b_conv1 = bias_variable([conv1_num], numVariable)
        h_conv1 = tf.nn.relu(conv2d(x, W_conv1, [1, 1], 'VALID') + b_conv1)

    with tf.name_scope('pool1' + nameScope):
        h_pool1 = max_pool(h_conv1, [pool1_len, 1], [pool1_len, 1], 'SAME')

    with tf.name_scope('conv2' + nameScope):
        W_conv2 = weight_variable([conv2_len, 1, conv1_num, conv2_num], regularizationRate, numVariable)
        b_conv2 = bias_variable([conv2_num], numVariable)
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2, [1, 1], 'SAME') + b_conv2)

    with tf.name_scope('pool2' + nameScope):
        h_pool2 = max_pool(h_conv2, [pool2_len, 1], [pool2_len, 1], 'SAME')

    with tf.name_scope('conv3' + nameScope):
        W_conv3 = weight_variable([conv3_len, 1, conv2_num, conv3_num], regularizationRate, numVariable)
        b_conv3 = bias_variable([conv3_num], numVariable)
        h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3, [1, 1], 'SAME') + b_conv3)

    with tf.name_scope('Inception1' + nameScope):
        W_Inception1_Branch1 = weight_variable([1, 1, conv3_num, 16], regularizationRate, numVariable)
        b_Inception1_Branch1 = bias_variable([16], numVariable)
        h_Inception1_Branch1 = tf.nn.relu(conv2d(h_conv3, W_Inception1_Branch1, [1, 1], 'SAME') + b_Inception1_Branch1)

        W_Inception1_Branch2 = weight_variable([1, 1, conv3_num, 12], regularizationRate, numVariable)
        b_Inception1_Branch2 = bias_variable([12], numVariable)
        h_Inception1_Branch2 = tf.nn.relu(conv2d(h_conv3, W_Inception1_Branch2, [1, 1], 'SAME') + b_Inception1_Branch2)
        W_Inception1_Branch2 = weight_variable([5, 1, 12, 16], regularizationRate, numVariable)
        b_Inception1_Branch2 = bias_variable([16], numVariable)
        h_Inception1_Branch2 = tf.nn.relu(conv2d(h_Inception1_Branch2, W_Inception1_Branch2, [1, 1], 'SAME') + b_Inception1_Branch2)

        W_Inception1_Branch3 = weight_variable([1, 1, conv3_num, 16], regularizationRate, numVariable)
        b_Inception1_Branch3 = bias_variable([16], numVariable)
        h_Inception1_Branch3 = tf.nn.relu(conv2d(h_conv3, W_Inception1_Branch3, [1, 1], 'SAME') + b_Inception1_Branch3)
        W_Inception1_Branch3 = weight_variable([3, 1, 16, 24], regularizationRate, numVariable)
        b_Inception1_Branch3 = bias_variable([24], numVariable)
        h_Inception1_Branch3 = tf.nn.relu(conv2d(h_Inception1_Branch3, W_Inception1_Branch3, [1, 1], 'SAME') + b_Inception1_Branch3)
        W_Inception1_Branch3 = weight_variable([3, 1, 24, 24], regularizationRate, numVariable)
        b_Inception1_Branch3 = bias_variable([24], numVariable)
        h_Inception1_Branch3 = tf.nn.relu(conv2d(h_Inception1_Branch3, W_Inception1_Branch3, [1, 1], 'SAME') + b_Inception1_Branch3)

        h_Inception1_Branch4 = avg_pool(h_conv3, [3, 1], [1, 1], 'SAME')
        W_Inception1_Branch4 = weight_variable([1, 1, conv3_num, 8], regularizationRate, numVariable)
        b_Inception1_Branch4 = bias_variable([8], numVariable)
        h_Inception1_Branch4 = tf.nn.relu(conv2d(h_Inception1_Branch4, W_Inception1_Branch4, [1, 1], 'SAME') + b_Inception1_Branch4)

        net1 = tf.concat([h_Inception1_Branch1, h_Inception1_Branch2, h_Inception1_Branch3, h_Inception1_Branch4], 3)
    '''
    with tf.name_scope('Inception2'):
        W_Inception2_Branch1 = weight_variable([1, 1, 64, 32], regularizationRate)
        b_Inception2_Branch1 = bias_variable([32])
        h_Inception2_Branch1 = tf.nn.relu(conv2d(net1, W_Inception2_Branch1, [1, 1], 'SAME') + b_Inception2_Branch1)
        W_Inception2_Branch1 = weight_variable([3, 1, 32, 64], regularizationRate)
        b_Inception2_Branch1 = bias_variable([64])
        h_Inception2_Branch1 = tf.nn.relu(conv2d(h_Inception2_Branch1, W_Inception2_Branch1, [2, 1], 'SAME') + b_Inception2_Branch1)

        W_Inception2_Branch2 = weight_variable([1, 1, 64, 32], regularizationRate)
        b_Inception2_Branch2 = bias_variable([32])
        h_Inception2_Branch2 = tf.nn.relu(conv2d(net1, W_Inception2_Branch2, [1, 1], 'SAME') + b_Inception2_Branch2)
        W_Inception2_Branch2 = weight_variable([3, 1, 32, 32], regularizationRate)
        b_Inception2_Branch2 = bias_variable([32])
        h_Inception2_Branch2 = tf.nn.relu(conv2d(h_Inception2_Branch2, W_Inception2_Branch2, [1, 1], 'SAME') + b_Inception2_Branch2)
        W_Inception2_Branch2 = weight_variable([3, 1, 32, 32], regularizationRate)
        b_Inception2_Branch2 = bias_variable([32])
        h_Inception2_Branch2 = tf.nn.relu(conv2d(h_Inception2_Branch2, W_Inception2_Branch2, [2, 1], 'SAME') + b_Inception2_Branch2)

        h_Inception2_Branch3 = avg_pool(net1, [3, 1], [2, 1], 'SAME')

        net2 = tf.concat([h_Inception2_Branch1, h_Inception2_Branch2, h_Inception2_Branch3], 3)
    '''
    with tf.name_scope('pool3' + nameScope):
        h_pool3 = max_pool(net1, [pool3_len, 1], [pool3_len, 1], 'SAME')
    return h_pool3


def attention(inputs, attention_size, time_major=True):
    if time_major:
        # (T,B,D) => (B,T,D)
        inputs = tf.transpose(inputs, [1, 0, 2])

    inputs_shape = inputs.shape
    sequence_length = inputs_shape[1].value  # the length of sequences processed in the antecedent RNN layer
    hidden_size = inputs_shape[2].value  # hidden size of the RNN layer

    # Attention mechanism
    W_omega = tf.Variable(tf.random_normal([hidden_size, attention_size], stddev=0.1))
    b_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))
    u_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))

    v = tf.tanh(tf.matmul(tf.reshape(inputs, [-1, hidden_size]), W_omega) + tf.reshape(b_omega, [1, -1]))
    vu = tf.matmul(v, tf.reshape(u_omega, [-1, 1]))
    exps = tf.reshape(tf.exp(vu), [-1, sequence_length])
    alphas = exps / tf.reshape(tf.reduce_sum(exps, 1), [-1, 1])

    # Output of Bi-RNN is reduced with attention vector
    output = tf.reduce_sum(inputs * tf.reshape(alphas, [-1, sequence_length, 1]), 1)

    return output


def conv2d(x, W, strides, padding):
    return tf.nn.conv2d(x, W, strides=[1, strides[0], strides[1], 1], padding=padding)


def max_pool(x, shape, strides, padding):
    return tf.nn.max_pool(x, ksize=[1, shape[0], shape[1], 1],
                          strides=[1, strides[0], strides[1], 1], padding=padding)


def avg_pool(x, shape, strides, padding):
    return tf.nn.avg_pool(x, ksize=[1, shape[0], shape[1], 1],
                          strides=[1, strides[0], strides[1], 1], padding=padding)


def weight_variable(shape, lam, numVariable):
    var = tf.Variable(tf.truncated_normal(shape, stddev=0.1))
    tf.add_to_collection('losses', tf.contrib.layers.l2_regularizer(lam)(var))
    numVariable[0] += np.prod(shape)
    return var


def bias_variable(shape, numVariable):
    initial = tf.constant(0.1, shape=shape)
    numVariable[0] += np.prod(shape)
    return tf.Variable(initial)


def calculateScale(data):
    scale_mean = np.mean(data, axis=0)
    scale_std = np.std(data, axis=0)
    return scale_mean, scale_std


def normalizeData(data, scale_mean, scale_std):
    result = (data - scale_mean) / scale_std
    result[result >= 3] = 3
    result[result <= -3] = -3
    return result
