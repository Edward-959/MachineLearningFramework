# -*- coding: utf-8 -*-
"""
Created on 2017/10/11 10:35
Updated on 2018/7/11 by 006566  -- 将startSliceData.timeStamp和endSliceData.timeStamp直接换成对应的startTimeStamp

@author: 006547
"""
import numpy as np
from tensorflow.python.framework import random_seed


class DeepNNDataSet(object):
    def __init__(self, factorData, subTagData, sliceLag, tagName, adjust=False, seed=None):
        seed1, seed2 = random_seed.get_seed(seed)
        # If op level seed is not set, use whatever graph level seed is returned
        np.random.seed(seed1 if seed is None else seed2)
        self._adjust = adjust
        self._factorData = factorData
        self._subTagData = subTagData
        self._sliceLag = sliceLag
        self._tagName = tagName
        if isinstance(tagName, list):
            self._iStartIndex = self.createIStartIndex(self._subTagData, self._sliceLag, tagName[0])
        else:
            self._iStartIndex = self.createIStartIndex(self._subTagData, self._sliceLag, self._tagName)
        self._num_examples = self._iStartIndex.__len__()
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def factorData(self):
        return self._factorData

    @property
    def subTagData(self):
        return self._subTagData

    @property
    def iStartIndex(self):
        return self._iStartIndex

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size, shuffle=True):
        """Return the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        # Shuffle for the first epoch
        if self._epochs_completed == 0 and start == 0 and shuffle:
            perm0 = np.arange(self._num_examples)
            np.random.shuffle(perm0)
            self._iStartIndex = self._iStartIndex[perm0]
        # Go to the next epoch
        if start + batch_size > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Get the rest examples in this epoch
            rest_num_examples = self._num_examples - start
            iStartIndex_rest_part = self._iStartIndex[start:self._num_examples]
            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)
                np.random.shuffle(perm)
                self._iStartIndex = self._iStartIndex[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size - rest_num_examples
            end = self._index_in_epoch
            iStartIndex_new_part = self._iStartIndex[start:end]
            iStartIndex = np.concatenate((iStartIndex_rest_part, iStartIndex_new_part), axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            iStartIndex = self._iStartIndex[start:end]

        batchData = []
        batchLabel = []
        batchSubTag = []
        for iStart in iStartIndex:
            iEnd = iStart + self._sliceLag
            tempData = np.reshape(self._factorData[iStart:iEnd, :], self._factorData[iStart:iEnd, :].size)
            # for i in range(iStart, iEnd):
            #     for j in range(self._factorData.shape[1]):
            #        tempData.append(self._factorData[i, j])
            batchData.append(tempData)
            if isinstance(self._tagName, list):
                tempTag = []
                for tagName in self._tagName:
                    if isinstance(self._subTagData[iEnd - 1][tagName].returnRate, list):
                        tempTag += self._subTagData[iEnd - 1][tagName].returnRate
                    else:
                        tempTag.append(self._subTagData[iEnd - 1][tagName].returnRate)
            else:
                if isinstance(self._subTagData[iEnd - 1][self._tagName].returnRate, list):
                    tempTag = self._subTagData[iEnd - 1][self._tagName].returnRate
                else:
                    tempTag = [self._subTagData[iEnd - 1][self._tagName].returnRate]

            labelSoftMax1 = np.array(tempTag) * 100
            batchLabel.append(labelSoftMax1)
            batchSubTag.append(self._subTagData[iEnd - 1])
        return np.array(batchData, dtype=np.float32), np.array(batchLabel, dtype=np.float32), batchSubTag

    def createIStartIndex(self, subTagData, sliceLag, tagName):
        iStartIndex = []
        label = []
        iStart = 0
        iEnd = sliceLag
        while iEnd <= subTagData.__len__():
            # startSliceData = subTagData[iStart][tagName].startSliceData
            # endSliceData = subTagData[iEnd - 1][tagName].startSliceData
            # if endSliceData.timeStamp - startSliceData.timeStamp <= 5.5 * 3600:
            startTimeStamp = subTagData[iStart][tagName].startTimeStamp
            endTimeStamp = subTagData[iEnd - 1][tagName].startTimeStamp
            if endTimeStamp - startTimeStamp <= 5.5 * 3600:
                iStartIndex.append(iStart)
                label.append(self._subTagData[iEnd - 1][tagName].returnRate)
            iStart += 1
            iEnd += 1
        if self._adjust:
            labelArray = np.array(label)
            cond_1_0_1 = (-0.001 < labelArray) & (labelArray <= 0.001)
            cond_1_2 = (0.001 < labelArray) & (labelArray <= 0.002)
            cond_2_s = 0.002 < labelArray
            cond_2_1 = (-0.002 < labelArray) & (labelArray <= -0.001)
            cond_s_2 = labelArray <= -0.002

            freq_1_0_1 = sum(cond_1_0_1) / labelArray.size / 2
            freq_1_2 = sum(cond_1_2) / labelArray.size
            freq_2_s = sum(cond_2_s) / labelArray.size

            freq_2_1 = sum(cond_2_1) / labelArray.size
            freq_s_2 = sum(cond_s_2) / labelArray.size

            adjust_1_2 = np.floor(freq_1_0_1 / 2 / freq_1_2)
            if adjust_1_2 >= 2:
                for i in range(int(adjust_1_2-1)):
                    iStartIndex += np.extract(cond_1_2, iStartIndex).tolist()

            adjust_2_1 = np.floor(freq_1_0_1 / 2 / freq_2_1)
            if adjust_2_1 >= 2:
                for i in range(int(adjust_2_1-1)):
                    iStartIndex += np.extract(cond_2_1, iStartIndex).tolist()

            adjust_2_s = np.floor(freq_1_0_1 / 4 / freq_2_s)
            if adjust_2_s >= 2:
                for i in range(int(adjust_2_s-1)):
                    iStartIndex += np.extract(cond_2_s, iStartIndex).tolist()

            adjust_s_2 = np.floor(freq_1_0_1 / 4 / freq_s_2)
            if adjust_s_2 >= 2:
                for i in range(int(adjust_s_2-1)):
                    iStartIndex += np.extract(cond_s_2, iStartIndex).tolist()
        return np.array(iStartIndex, dtype=np.int32)
