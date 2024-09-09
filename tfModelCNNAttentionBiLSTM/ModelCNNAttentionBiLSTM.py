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
from ModelSystem.DeepNNDataSet import DeepNNDataSet
import math
import os
import shutil


class ModelCNNAttentionBiLSTM(Model):
    def __init__(self, paraModel, name, tagName, modelManagement):
        Model.__init__(self, paraModel, name, tagName, modelManagement)
        modelManagement.register(self)

    def train(self, rollingData, outputDict):  # 数据集都是np.array格式
        validationNum = self.paraModel["validationNum"]
        GPUID = self.paraModel["GPUID"]
        absolutePath = self.paraModel["absolutePath"]

        trainData = np.array(rollingData["trainData"][:-validationNum])
        validData = np.array(rollingData["trainData"][-validationNum:])
        predictData = np.array(rollingData["predictData"])
        trainSubTag = rollingData["trainSubTag"][:-validationNum]
        validSubTag = rollingData["trainSubTag"][-validationNum:]
        predictSubTag = rollingData["predictSubTag"]
        # 参数设置
        sliceLag = self.paraModel["sliceLag"]
        numFactor = rollingData["trainData"][0].__len__()
        lr = 1e-4
        rnn_keepProbPara = 0.8
        rnn_hiddenSizePara = 256
        conv_len = self.paraModel["conv_len"]
        runStep = 30000
        batchSize = 1000
        checkPeriod = 25
        epochsStop = 20

        scale_mean, scale_std = calculateScale(trainData)

        trainNNData = normalizeData(trainData, scale_mean, scale_std)
        validNNData = normalizeData(validData, scale_mean, scale_std)
        predictNNData = normalizeData(predictData, scale_mean, scale_std)

        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = str(GPUID)

        tf.reset_default_graph()
        with tf.Session() as sess:
            triggerRatio = self.paraModel["evaluateModel"]["triggerRatio"]
            if not os.path.exists(absolutePath + 'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder'):
                print("Model " + self.backTestUnderlying + " does not exist. Training Model")
                # Create the model
                x = tf.placeholder(tf.float32, [None, sliceLag * numFactor])
                # Define loss and optimizer
                y_ = tf.placeholder(tf.float32, [None, 1])
                # Build the graph for the deep net
                numVariable = [0]
                y_regression, rnn_keepProb = deepnn(x, numVariable, image_len=sliceLag, factor_num=numFactor, conv1_len=conv_len,
                                                    conv1_num=32, pool1_len=2, conv2_len=conv_len, conv2_num=32, pool2_len=2,
                                                    conv3_len=conv_len, conv3_num=64, pool3_len=4, rnn_hiddenSize=rnn_hiddenSizePara,
                                                    rnn_layerNum=1, regularizationRate=0.001)
                numVariable = numVariable[0]
                print("Number of variables: " + str(numVariable))
                with tf.name_scope('loss'):
                    # cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_softmax))
                    rmse = tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(y_, y_regression), 2)))
                tf.add_to_collection('losses', rmse)
                loss = tf.add_n(tf.get_collection('losses'))
                with tf.name_scope('adam_optimizer'):
                    train_step = tf.train.AdamOptimizer(learning_rate=lr).minimize(loss)
                # saver = tf.train.Saver()
                sess.run(tf.global_variables_initializer())
                trainDeepNNDataSet = DeepNNDataSet(trainNNData, trainSubTag, sliceLag, self.tagName)
                validDeepNNDataSet = DeepNNDataSet(validNNData, validSubTag, sliceLag, self.tagName)
                batchValid = validDeepNNDataSet.next_batch(validDeepNNDataSet.num_examples, shuffle=True)
                valid_lossSeries = []
                train_lossSeries = []

                for i in range(runStep):
                    batchTrain = trainDeepNNDataSet.next_batch(batchSize, shuffle=True)
                    if i % checkPeriod == 0:
                        train_loss = loss.eval(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: 1.0})
                        predict = y_regression.eval(feed_dict={x: batchTrain[0], rnn_keepProb: 1.0})[:, 0] / 100
                        label = batchTrain[1][:, 0] / 100
                        train_TriggerTimes = sum(predict > triggerRatio) + sum(predict < -triggerRatio)
                        if train_TriggerTimes != 0:
                            train_winRate = (sum(label[predict > triggerRatio] > 0.001) + sum(label[predict < -triggerRatio] < -0.001)) / train_TriggerTimes
                            train_AveReturn = (sum(label[predict > triggerRatio]) - sum(label[predict < -triggerRatio])) / train_TriggerTimes
                        else:
                            train_winRate = 0
                            train_AveReturn = 0

                        valid_loss = loss.eval(feed_dict={x: batchValid[0], y_: batchValid[1], rnn_keepProb: 1.0})
                        predict = y_regression.eval(feed_dict={x: batchValid[0], rnn_keepProb: 1.0})[:, 0] / 100
                        label = batchValid[1][:, 0] / 100
                        valid_TriggerTimes = sum(predict > triggerRatio) + sum(predict < -triggerRatio)
                        if valid_TriggerTimes != 0:
                            valid_winRate = (sum(label[predict > triggerRatio] > 0.001) + sum(label[predict < -triggerRatio] < -0.001)) / valid_TriggerTimes
                            valid_AveReturn = (sum(label[predict > triggerRatio]) - sum(label[predict < -triggerRatio])) / valid_TriggerTimes
                        else:
                            valid_winRate = 0
                            valid_AveReturn = 0

                        print('step %d, training loss %.6f, winRate %.2f, times %d, train AveReturn %.6f, epochs %d; valid loss %.6f, winRate %.2f, times %d, valid AveReturn %.6f' % (i, train_loss, train_winRate, train_TriggerTimes, train_AveReturn, trainDeepNNDataSet.epochs_completed, valid_loss, valid_winRate, valid_TriggerTimes, valid_AveReturn))
                        valid_lossSeries.append(float(valid_loss))
                        train_lossSeries.append(float(train_loss))
                        if valid_loss <= min(valid_lossSeries):
                            if os.path.exists(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'):
                                shutil.rmtree(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder')
                            builder = tf.saved_model.builder.SavedModelBuilder(absolutePath+'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder')
                            builder.add_meta_graph_and_variables(sess, ['model_' + validSubTag[0]['1min'].code[0:6]])
                            builder.save()
                            if i == 0:
                                os.mkdir(absolutePath+'ModelSaved/tmp' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder')
                                shutil.move(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb", absolutePath+'ModelSaved/tmp'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb")
                            print('Model Saved')
                            with open(absolutePath+'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder' + "/ModelSet.json", "w") as f:
                                modelSet = {'mean': scale_mean.tolist(), 'std': scale_std.tolist(), 'ModelInput': self.modelInput, 'WindowSize': sliceLag}
                                json.dump(modelSet, f)
                        # if valid_lossSeries.__len__() > 0 and valid_lossSeries.__len__() - 1 - np.argmin(valid_lossSeries) >= earlyStopPeriod:
                        if trainDeepNNDataSet.epochs_completed == epochsStop:
                            with open(absolutePath+'ModelSaved/' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder' + "/Loss.json", "w") as f:
                                Loss = {'valid_loss': valid_lossSeries, 'train_loss': train_lossSeries}
                                json.dump(Loss, f)
                            print('Stop Training')
                            break
                    train_step.run(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: rnn_keepProbPara})
                if os.path.exists(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb"):
                    os.remove(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb")
                shutil.move(absolutePath+'ModelSaved/tmp'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb", absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/saved_model.pb")
                shutil.rmtree(absolutePath + 'ModelSaved/tmp' + self.backTestUnderlying + '_' + self.name + '_SavedModelBuilder')

        tf.reset_default_graph()
        with tf.Session() as sess:
            print("Model " + self.backTestUnderlying + " exists. Loading Model")
            tf.saved_model.loader.load(sess, ['model_' + validSubTag[0]['1min'].code[0:6]], absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder')
            y_regression = sess.graph.get_tensor_by_name('regression/add:0')
            loss = sess.graph.get_tensor_by_name('AddN:0')
            x = sess.graph.get_tensor_by_name('Placeholder:0')
            y_ = sess.graph.get_tensor_by_name('Placeholder_1:0')
            rnn_keepProb = sess.graph.get_tensor_by_name('Placeholder_2:0')

            with open(absolutePath+'ModelSaved/'+self.backTestUnderlying+'_'+self.name+'_SavedModelBuilder'+"/ModelSet.json", "w") as f:
                modelSet = {'mean': scale_mean.tolist(), 'std': scale_std.tolist(), 'ModelInput': self.modelInput, 'WindowSize': sliceLag}
                json.dump(modelSet, f)

            trainDeepNNDataSet = DeepNNDataSet(trainNNData, trainSubTag, sliceLag, self.tagName)
            batchTrain = trainDeepNNDataSet.next_batch(min(40000, trainDeepNNDataSet.num_examples), shuffle=True)
            allTrain_loss = loss.eval(feed_dict={x: batchTrain[0], y_: batchTrain[1], rnn_keepProb: 1.0})
            inSamplePredict = y_regression.eval(feed_dict={x: batchTrain[0], rnn_keepProb: 1.0})[:, 0] / 100
            inSampleLabel = batchTrain[1][:, 0] / 100
            TriggerTimes = sum(inSamplePredict > triggerRatio) + sum(inSamplePredict < -triggerRatio)
            if TriggerTimes != 0:
                winRate = (sum(inSampleLabel[inSamplePredict > triggerRatio] > 0.001) + sum(inSampleLabel[inSamplePredict < -triggerRatio] < -0.001)) / TriggerTimes
                allTrain_AveReturn = (sum(inSampleLabel[inSamplePredict > triggerRatio]) - sum(inSampleLabel[inSamplePredict < -triggerRatio])) / TriggerTimes
            else:
                winRate = 0
                allTrain_AveReturn = 0
            print('allTrain loss %.6f, winRate %.2f, times %d, allTrain AveReturn %.6f' % (allTrain_loss, winRate, TriggerTimes, allTrain_AveReturn))

            # test_loss = loss.eval(feed_dict={x: batchPredict[0], y_: batchPredict[1], rnn_keepProb: 1.0})
            # outSamplePredict = y_regression.eval(feed_dict={x: batchPredict[0], y_: batchPredict[1], rnn_keepProb: 1.0})[:, 0] / 100
            # 预测太多，需要拆分
            predictDeepNNDataSet = DeepNNDataSet(predictNNData, predictSubTag, sliceLag, self.tagName)
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
                                                         rnn_keepProb: 1})[:, 0] / 100
                    outSamplePredict += temp2.tolist()
            if res > 0:
                temp1 = loss.eval(feed_dict={x: batchPredict[0][(num * 10000):(num * 10000 + res), :],
                                             y_: batchPredict[1][(num * 10000):(num * 10000 + res), :],
                                             rnn_keepProb: 1})
                test_loss.append(temp1)
                temp2 = y_regression.eval(feed_dict={x: batchPredict[0][(num * 10000):(num * 10000 + res), :],
                                                     rnn_keepProb: 1})[:, 0] / 100
                outSamplePredict += temp2.tolist()
            outSamplePredict = np.array(outSamplePredict)
            test_loss = float(np.mean(test_loss))

            outSampleLabel = batchPredict[1][:, 0] / 100
            TriggerTimes = sum(outSamplePredict > triggerRatio) + sum(outSamplePredict < -triggerRatio)
            if TriggerTimes != 0:
                winRate = (sum(outSampleLabel[outSamplePredict > triggerRatio] > 0.001) + sum(outSampleLabel[outSamplePredict < -triggerRatio] < -0.001)) / TriggerTimes
                test_AveReturn = (sum(outSampleLabel[outSamplePredict > triggerRatio]) - sum(outSampleLabel[outSamplePredict < -triggerRatio])) / TriggerTimes
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


def deepnn(x, numVariable, image_len, factor_num, conv1_len, conv1_num, pool1_len, conv2_len, conv2_num, pool2_len, conv3_len, conv3_num, pool3_len, rnn_hiddenSize, rnn_layerNum, regularizationRate):
    with tf.name_scope('reshape'):
        x_image = tf.reshape(x, [-1, image_len, factor_num, 1])

    with tf.name_scope('conv1'):
        W_conv1 = weight_variable([conv1_len, factor_num, 1, conv1_num], regularizationRate, numVariable)
        b_conv1 = bias_variable([conv1_num], numVariable)
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1, [1, 1], 'VALID') + b_conv1)

    with tf.name_scope('pool1'):
        h_pool1 = max_pool(h_conv1, [pool1_len, 1], [pool1_len, 1], 'SAME')

    with tf.name_scope('conv2'):
        W_conv2 = weight_variable([conv2_len, 1, conv1_num, conv2_num], regularizationRate, numVariable)
        b_conv2 = bias_variable([conv2_num], numVariable)
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2, [1, 1], 'SAME') + b_conv2)

    with tf.name_scope('pool2'):
        h_pool2 = max_pool(h_conv2, [pool2_len, 1], [pool2_len, 1], 'SAME')

    with tf.name_scope('conv3'):
        W_conv3 = weight_variable([conv3_len, 1, conv2_num, conv3_num], regularizationRate, numVariable)
        b_conv3 = bias_variable([conv3_num], numVariable)
        h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3, [1, 1], 'SAME') + b_conv3)

    with tf.name_scope('Inception1'):
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
    with tf.name_scope('pool3'):
        h_pool3 = max_pool(net1, [pool3_len, 1], [pool3_len, 1], 'SAME')

    timestep_size = int(math.ceil(math.ceil(math.ceil((image_len-conv1_len+1)/pool1_len)/pool2_len)/pool3_len))
    x_timeSeries = tf.reshape(h_pool3, [-1, timestep_size, 64])
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
    x_timeSeries = tf.reshape(x_timeSeries, [-1, 64])
    x_timeSeries = tf.split(x_timeSeries, timestep_size)
    mlstm_fw_cell = rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layerNum)], state_is_tuple=True)
    mlstm_bw_cell = rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layerNum)], state_is_tuple=True)
    fw_state = mlstm_fw_cell.zero_state(batch_size, dtype=tf.float32)
    bw_state = mlstm_bw_cell.zero_state(batch_size, dtype=tf.float32)
    outputs, output_state_fw, output_state_bw = rnn.static_bidirectional_rnn(mlstm_fw_cell, mlstm_bw_cell, x_timeSeries, fw_state, bw_state, dtype=tf.float32)
    # h_state = outputs[-1]

    attention_size = 50

    attention_output = attention(outputs, attention_size, True)

    with tf.name_scope('regression'):
        W_fc = weight_variable([rnn_hiddenSize*2, 1], regularizationRate, numVariable)
        b_fc = bias_variable([1], numVariable)

        y_regression = tf.matmul(attention_output, W_fc) + b_fc
    return y_regression, rnn_keepProb


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
    return (data - scale_mean) / scale_std


'''
def combine(data, subTag, tagName):
    subTagData = []
    for i in range(subTag.__len__()):
        startSliceData = subTag[i][tagName].startSliceData
        tempData = [startSliceData.bidPrice[4] / startSliceData.previousClosingPrice,
                    startSliceData.bidPrice[3] / startSliceData.previousClosingPrice,
                    startSliceData.bidPrice[2] / startSliceData.previousClosingPrice,
                    startSliceData.bidPrice[1] / startSliceData.previousClosingPrice,
                    startSliceData.bidPrice[0] / startSliceData.previousClosingPrice,
                    startSliceData.askPrice[0] / startSliceData.previousClosingPrice,
                    startSliceData.askPrice[1] / startSliceData.previousClosingPrice,
                    startSliceData.askPrice[2] / startSliceData.previousClosingPrice,
                    startSliceData.askPrice[3] / startSliceData.previousClosingPrice,
                    startSliceData.askPrice[4] / startSliceData.previousClosingPrice,
                    startSliceData.lastPrice / startSliceData.previousClosingPrice,
                    startSliceData.bidVolume[4], startSliceData.bidVolume[3],
                    startSliceData.bidVolume[2], startSliceData.bidVolume[1],
                    startSliceData.bidVolume[0], startSliceData.askVolume[0],
                    startSliceData.askVolume[1], startSliceData.askVolume[2],
                    startSliceData.askVolume[3], startSliceData.askVolume[4],
                    startSliceData.volume]
        subTagData.append(tempData)
    return np.concatenate((subTagData, data), axis=1)
    

def adjustRMSE(y_, y_regression, batchSize):
    length = batchSize
    weight = tf.zeros([batchSize, 1])
    for i in range(length):
        weight[i][0] = tf.cond(tf.reduce_any([tf.reduce_all([y_[i][0] > 0.1, y_regression[i][0] > 0.1]),
                                              tf.reduce_all([-0.1 >= y_[i][0], -0.1 >= y_regression[i][0]]),
                                              tf.reduce_all([0.1 >= y_[i][0], y_[i][0] > 0, 0.1 >= y_regression[i][0], y_regression[i][0] > 0]),
                                              tf.reduce_all([0 >= y_[i][0], y_[i][0] > -0.1, 0 >= y_regression[i][0], y_regression[i][0] > -0.1])]), tf.add(weight[i][0], tf.constant(1)), tf.add(weight[i][0], tf.constant(0)))
        if (0.1 >= y_[i][0] > 0 >= y_regression[i][0] > -0.1) or \
                (0.1 >= y_regression[i][0] > 0 >= y_[i][0] > -0.1) or \
                (y_regression[i][0] > 0.1 >= y_[i][0] > 0) or \
                (y_[i][0] > 0.1 >= y_regression[i][0] > 0) or \
                (0 >= y_regression[i][0] > -0.1 > y_[i][0]) or \
                (0 >= y_[i][0] > -0.1 > y_regression[i][0]):
            weight.append(2)
        elif (y_regression[i][0] > 0.1 and 0 >= y_[i][0] > -0.1) or \
                (y_[i][0] > 0.1 and 0 >= y_regression[i][0] > -0.1) or \
                (-0.1 >= y_[i][0] and 0.1 >= y_regression[i][0] > 0) or \
                (-0.1 >= y_regression[i][0] and 0.1 >= y_[i][0] > 0):
            weight.append(3)
        elif (-0.1 >= y_[i][0] and y_regression[i][0] > 0.1) or \
                (y_[i][0] > 0.1 and -0.1 >= y_regression[i][0]):
            weight.append(4)
    return tf.sqrt(tf.reduce_mean(tf.pow(tf.subtract(y_, y_regression), 2) * weight))
'''
