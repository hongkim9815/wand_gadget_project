#!/usr/bin/python
#
# Python $1 Unistroke Recognizer
#
# This file contains a Python implementation of the $1 algorithm.
# The material I used can be found online at:
# http://depts.washington.edu/madlab/proj/dollar/index.html
#
# The academic publication for the $1 recognizer, and what should be
# used to cite it, is:
#
#  Wobbrock, J.O., Wilson, A.D. and Li, Y. (2007). Gestures without
#	   libraries, toolkits or training: A $1 recognizer for user interface
#	   prototypes. Proceedings of the ACM Symposium on User Interface
#	   Software and Technology (UIST '07). Newport, Rhode Island (October
#	   7-10, 2007). New York: ACM Press, pp. 159-168.
#
# This software is distributed under the "New BSD License" agreement:
#
# Copyright (C) 2007-2012, Jacob O. Wobbrock, Andrew D. Wilson and Yang Li.
# All rights reserved. Last updated July 14, 2018.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the names of the University of Washington nor Microsoft,
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Jacob O. Wobbrock OR Andrew D. Wilson
# OR Yang Li BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from math import pi, atan2, cos, sin, inf
from templates import UNISTROKES


RESAMPLE_SIZE = 64
ORIGIN = (0, 0)
SQUARE_SIZE = 350
ANGLE_RANGE = (2 / 180) * pi
ANGLE_PRECISION = (2 / 180) * pi
PHI = 0.5 * (-1.0 + (5.0)**0.5)


class Dollar:

    def __init__(self):
        # format the example gestures
        self.unistrokes = []
        for template in UNISTROKES:
            self.unistrokes.append(Stroke(template[1]))
            self.unistrokes[-1].name = template[0]

    def get_gesture(self, points):
        stroke = Stroke(points)
        # search for the closest gesture (ie. with minimal distance)
        min_distance = inf
        gesture_name = ''
        for template_stroke in self.unistrokes:
            distance = stroke.distance_at_best_angle(template_stroke.points)
            if distance < min_distance:
                # update the current best gesture
                min_distance = distance
                gesture_name = template_stroke.name
        return gesture_name


class Stroke:

    def __init__(self, points, should_format=True):
        self.points = points
        if should_format:
            self.resample()
            self.rotate_by(-self.indicative_angle())
            self.scale_to(SQUARE_SIZE)
            self.translate_to(ORIGIN)

    def resample(self):
        points = self.points
        I = self.path_length() / (RESAMPLE_SIZE - 1)
        D = 0
        new_points = [points[0]]
        i = 1
        while i < len(points):
            previous, current = points[i - 1:i + 1]
            d = distance(previous, current)
            if ((D + d) >= I):
                q = (previous[0] + ((I - D) / d) * (current[0] - previous[0]),
                     previous[1] + ((I - D) / d) * (current[1] - previous[1]))
                # append new point 'q'
                new_points.append(q)
                # insert 'q' at position i in points s.t. 'q' will be the next i
                points.insert(i, q)
                D = 0
            else:
                D += d
            i += 1
        # somtimes we fall a rounding-error short of adding the last point, so
        # add it if so
        if len(new_points) == RESAMPLE_SIZE - 1:
            new_points.append(new_points[-1])
        self.points = new_points

    def path_length(self):
        d = 0
        for i in range(1, len(self.points)):
            d += distance(self.points[i - 1], self.points[i])
        return d

    def indicative_angle(self):
        # angle formed by (points[0], centroid) and the horizon
        c = self.centroid()
        return atan2(c[1] - self.points[0][1], c[0] - self.points[0][0])

    def centroid(self):
        n = len(self.points)
        return (
            sum([p[0] / n for p in self.points]),
            sum([p[1] / n for p in self.points])
        )

    def rotate_by(self, angle):
        c = self.centroid()
        new_points = []
        for p in self.points:
            dx, dy = p[0] - c[0], p[1] - c[1]
            new_points.append((
                dx * cos(angle) - dy * sin(angle) + c[0],
                dx * sin(angle) + dy * cos(angle) + c[1]
            ))
        self.points = new_points

    def scale_to(self, size):
        B = self.bounding_box()
        new_points = []
        for p in self.points:
            new_points.append((
                p[0] * size / B[0],
                p[1] * size / B[1]
            ))
        self.points = new_points

    def bounding_box(self):
        minX, maxX = inf, -inf
        minY, maxY = inf, -inf
        for point in self.points:
            minX, maxX = min(minX, point[0]), max(maxX, point[0])
            minY, maxY = min(minY, point[1]), max(maxY, point[1])
        return (maxX - minX, maxY - minY)

    def translate_to(self, target):
        c = self.centroid()
        new_points = []
        for p in self.points:
            new_points.append((
                p[0] + target[0] - c[0],
                p[1] + target[1] - c[1]
            ))
        self.points = new_points

    def distance_at_best_angle(self, T):
        a = -ANGLE_RANGE
        b = ANGLE_RANGE
        x1 = PHI * a + (1 - PHI) * b
        x2 = PHI * b + (1 - PHI) * a
        f1 = self.distance_at_angle(T, x1)
        f2 = self.distance_at_angle(T, x2)
        while abs(b - a) > ANGLE_PRECISION:
            if f1 < f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = PHI * a + (1 * PHI) * b
                f1 = self.distance_at_angle(T, x1)
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = PHI * b + (1 - PHI) * a
                f2 = self.distance_at_angle(T, x2)
        return min(f1, f2)

    def distance_at_angle(self, T, angle):
        rotated_stroke = Stroke(self.points, False)
        rotated_stroke.rotate_by(angle)
        return rotated_stroke.path_distance(T)

    def path_distance(self, points):
        n = len(points)
        return sum([distance(self.points[i], points[i]) / n for i in range(n)])


def distance(p1, p2):
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5
