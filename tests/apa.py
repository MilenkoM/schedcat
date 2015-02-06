#!/usr/bin/env python

from __future__ import division

import unittest

import schedcat.mapping.binpack as bp
import schedcat.mapping.apa as apa
import schedcat.model.tasks as tasks

import schedcat.sched.native as native
import schedcat.sched as sched

class PartitioningHeuristics(unittest.TestCase):
    def setUp(self):
        self.ts = tasks.TaskSystem([
            tasks.SporadicTask(10, 100),
            tasks.SporadicTask(30, 100),
            tasks.SporadicTask(20, 100, deadline=30),
            tasks.SporadicTask(21, 30),
            ])

        self.ts[0].affinity = set([1])
        self.ts[1].affinity = set([1, 2])
        self.ts[2].affinity = set([2, 3])
        self.ts[3].affinity = set([1, 2, 3])

        self.cores = set([1, 2, 3])

    def test_sorted_by_decreasing_difficulty(self):
        got = apa.sorted_by_decreasing_difficulty(self.ts)
        expected = [
            self.ts[0],
            self.ts[2],
            self.ts[1],
            self.ts[3],
        ]
        self.assertEqual(expected, got)

        got = apa.sorted_by_decreasing_difficulty(
            [t for t in self.ts if 2 in t.affinity])
        expected = [
            self.ts[2],
            self.ts[1],
            self.ts[3],
        ]
        self.assertEqual(expected, got)


    def test_first_fit(self):
        failed, mapping = apa.edf_first_fit_decreasing_difficulty(self.ts, [1, 2, 3])

        self.assertEqual(failed, set())
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[1], [self.ts[0], self.ts[1]])
        self.assertEqual(mapping[2], [self.ts[3]])
        self.assertEqual(mapping[3], [self.ts[2]])


        failed, mapping = apa.edf_first_fit_decreasing_difficulty(self.ts, [2, 1, 3])

        self.assertEqual(failed, set())
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[2], [self.ts[2], self.ts[1]])
        self.assertEqual(mapping[1], [self.ts[0], self.ts[3]])
        self.assertEqual(mapping[3], [])


        # give it one more to place
        self.ts.append(tasks.SporadicTask(19, 31))
        self.ts[-1].affinity = set([2, 3])

        failed, mapping = apa.edf_first_fit_decreasing_difficulty(self.ts, [1, 2, 3])
        self.assertEqual(failed, set([self.ts[-1]]))

        failed, mapping = apa.edf_first_fit_decreasing_difficulty(self.ts, [2, 1, 3])

        self.assertEqual(failed, set())
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[2], [self.ts[2], self.ts[1]])
        self.assertEqual(mapping[1], [self.ts[0], self.ts[3]])
        self.assertEqual(mapping[3], [self.ts[4]])


    def test_worst_fit(self):
        failed, mapping = apa.edf_worst_fit_decreasing_difficulty(self.ts)

        self.assertEqual(failed, set())
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[1], [self.ts[0], self.ts[1]])
        self.assertEqual(mapping[2], [self.ts[2]])
        self.assertEqual(mapping[3], [self.ts[3]])

        # give it one more to place
        self.ts.append(tasks.SporadicTask(19, 31))
        self.ts[-1].affinity = set([2, 3])

        failed, mapping = apa.edf_worst_fit_decreasing_difficulty(self.ts)

        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[1], [self.ts[0], self.ts[1]])
        self.assertEqual(mapping[2], [self.ts[2]])
        self.assertEqual(mapping[3], [self.ts[4]])

        self.assertEqual(failed, set([self.ts[3]]))



class CEqualDHeuristic(unittest.TestCase):
    def setUp(self):
        self.ts1 = tasks.TaskSystem([
            tasks.SporadicTask(66, 100),
            tasks.SporadicTask(66, 100),
            tasks.SporadicTask(66, 100),
        ])

        self.ts2 = tasks.TaskSystem([
            tasks.SporadicTask(14, 40),
            tasks.SporadicTask(16, 48),
        ])

        self.ts3 = tasks.TaskSystem([
            tasks.SporadicTask(1, 16, deadline=11),
            tasks.SporadicTask(6, 15),
            tasks.SporadicTask(9, 20),
        ])

        self.ts4 = tasks.TaskSystem([
            tasks.SporadicTask(10, 100),
            tasks.SporadicTask(30, 100),
        ])



    def test_qpa_get_max_C_equal_D_cost_1(self):
        ts = sched.get_native_taskset(self.ts1[:1])
        max_wcet = native.qpa_get_max_C_equal_D_cost(
            ts, self.ts1[1].cost, self.ts1[1].period)
        self.assertEqual(max_wcet, 34)

    def test_qpa_get_max_C_equal_D_cost_2(self):
        ts = sched.get_native_taskset(self.ts2)
        max_wcet = native.qpa_get_max_C_equal_D_cost(
            ts, 6, 16)
        self.assertEqual(max_wcet, 5)

    def test_qpa_get_max_C_equal_D_cost_3(self):
        ts = sched.get_native_taskset(self.ts3)
        max_wcet = native.qpa_get_max_C_equal_D_cost(
            ts, 6, 12)
        self.assertEqual(max_wcet, 1)

    def test_qpa_get_max_C_equal_D_cost_4(self):
        ts = sched.get_native_taskset(self.ts4)
        max_wcet = native.qpa_get_max_C_equal_D_cost(
            ts, 21, 30)
        self.assertEqual(max_wcet, 16)

