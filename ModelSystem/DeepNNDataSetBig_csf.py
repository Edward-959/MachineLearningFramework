# -*- coding: utf-8 -*-
"""
Created on 2017/10/11 10:35
Updated on 2018/7/11 by 006566  -- 将startSliceData.timeStamp和endSliceData.timeStamp直接换成对应的startTimeStamp

@author: 006547
"""
import numpy as np
from tensorflow.python.framework import random_seed


class DeepNNDataSet(object):
    def __init__(self, factorData, subTagData, sliceLag, priceVolumeFactorIndex, tagName, adjust=False, seed=None):
        seed1, seed2 = random_seed.get_seed(seed)
        # If op level seed is not set, use whatever graph level seed is returned
        np.random.seed(seed1 if seed is None else seed2)
        self._adjust = adjust
        self._factorData = factorData
        self._subTagData = subTagData
        self._sliceLag = sliceLag
        self._tagName = tagName
        self.__priceVolumeFactorIndex = priceVolumeFactorIndex

        if isinstance(tagName, list):
            self._iStartIndex = self.createIStartIndex(self._subTagData, self._sliceLag, tagName[0])
        else:
            self._iStartIndex = self.createIStartIndex(self._subTagData, self._sliceLag, self._tagName)

        self._num_examples = self._iStartIndex.__len__()

        self._tag_convert_method = 'scale'
        self._is_first_convert = True
        self._scale_factor = 100
        self._max_min_scale = []
        self._max_min_offset = []

        self._tags = self.load_tags() * 100
        self._factor_frames = self.load_factor_frames_with_price_features()
        self._iBatchIndex = np.arange(self._num_examples)
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

    def set_tags(self, in_tags):
        self._tags = np.array(in_tags)

    def get_tags(self):
        return np.array(self._tags)

    def load_tags(self):
        tag_len = len(self._subTagData)
        tags = []
        for i in range(tag_len):
            tempTag = []
            if isinstance(self._tagName, list):
                for tagName in self._tagName:
                    if isinstance(self._subTagData[i][tagName].returnRate, list):
                        tempTag += self._subTagData[i][tagName].returnRate
                    else:
                        tempTag.append(self._subTagData[i][tagName].returnRate)
            else:
                if isinstance(self._subTagData[i][self._tagName].returnRate, list):
                    tempTag = self._subTagData[i][self._tagName].returnRate
                else:
                    tempTag = [self._subTagData[i][self._tagName].returnRate]

            tags.append(tempTag)

        tags = np.array(tags)

        return tags

    def load_factor_frames(self):
        factor_frames = []
        for iStart in self._iStartIndex:
            iEnd = iStart + self._sliceLag
            factor_frames.append(self._factorData[iStart:iEnd, :])
        return np.array(factor_frames)

    def load_factor_frames_with_price_features(self):
        factor_frames = []
        factor_frames_final = []
        price_features = []
        for iStart in self._iStartIndex:
            iEnd = iStart + self._sliceLag
            sub_tag_data = self._subTagData[iStart:iEnd]
            tagName = self._tagName
            if isinstance(self._tagName, list):
                tagName = self._tagName[0]
            start_price = []
            for tag_data in sub_tag_data:
                start_price.append(tag_data[tagName].startPrice)

            base_price = self._subTagData[iStart][tagName].startPrice
            price_feature = np.array(start_price) / base_price - 1
            price_feature = np.reshape(price_feature, (-1, 1))
            price_features.append(price_feature)
            factorData = self._factorData[iStart:iEnd, :]
            factor_frames.append(factorData)

        for i in range(len(factor_frames)):
            factorData = np.hstack((factor_frames[i], price_features[i], factor_frames[i][:, self.__priceVolumeFactorIndex]))
            factor_frames_final.append(factorData)

        return np.array(factor_frames_final)

    def next_batch(self, batch_size, shuffle=True):
        """Return the next `batch_size` examples from this data set."""
        start = self._index_in_epoch
        # Shuffle for the first epoch
        if self._epochs_completed == 0 and start == 0 and shuffle:
            perm0 = np.arange(self._num_examples)
            np.random.shuffle(perm0)
            self._iBatchIndex = perm0
        # Go to the next epoch
        if start + batch_size > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Get the rest examples in this epoch
            rest_num_examples = self._num_examples - start
            iBatchIndex_rest_part = self._iBatchIndex[start:self._num_examples]
            # Shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)
                np.random.shuffle(perm)
                self._iBatchIndex = perm
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size - rest_num_examples
            end = self._index_in_epoch
            iBatchIndex_new_part = self._iBatchIndex[start:end]
            iBatchIndex = np.concatenate((iBatchIndex_rest_part, iBatchIndex_new_part), axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            iBatchIndex = self._iBatchIndex[start:end]

        batchData = []
        batchLabel = []
        batchSubTag = []
        for index in iBatchIndex:
            iEnd = self._iStartIndex[index] + self._sliceLag
            tempData = np.reshape(self._factor_frames[index], self._factor_frames[index].size)
            batchData.append(tempData)
            batchLabel.append(self._tags[iEnd - 1])
            batchSubTag.append(self._subTagData[iEnd - 1])
        return np.array(batchData, dtype=np.float32), np.array(batchLabel, dtype=np.float32), batchSubTag

    @staticmethod
    def createIStartIndex(subTagData, sliceLag, tagName):
        iStartIndex = []
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
            iStart += 1
            iEnd += 1
        return np.array(iStartIndex, dtype=np.int32)
